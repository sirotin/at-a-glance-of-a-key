#! /usr/bin/python

# Author: Alexander Sirotin / sirotin@gmail.com
# Copyright (c) 2017 Alexander Sirotin.
# Licensed under MIT license:
# https://opensource.org/licenses/mit-license.php
# Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

import re
import sys
import jenkins
import logging
from optparse import OptionParser

logger = logging.getLogger()
hdlr = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('%(asctime)s %(levelname)s\t%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

def connect(server, port, username, password):
	logger.info("Connecting to Jenkins at %s:%d (user: %s)" % (server, port, username))
	try:
		return jenkins.Jenkins("http://%s:%d" % (server, port), username=username, password=password)

	except Exception as e:
		logger.error("Connection failed: %s" % e.message)
		return None

def check_build(conn, number):
	logger.info("Checking build number %d" % number)
	info = conn.get_build_info(name=options.job, number=number)

	if info["building"]:
		logger.info("Build %d is still in progress - skipping" % number)
		return False

	if info["result"] != "SUCCESS":
		logger.info("Build %d result is %s - skipping" % (number, info["result"]))
		return False

	branch = re.findall("\((.*)\)", info["displayName"])[0]
	if branch != options.branch:
		logger.info("Build %d is on branch %s - skipping" % (number, branch))
		return False

	logger.info("Found build %d" % number)
	print("%d" % number)
	return True

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("", "--server", dest="server", default="10.0.0.3", help="Jenkins server ip address")
	parser.add_option("", "--port", dest="port", default=8080, type="int", help="Jenkins server port")
	parser.add_option("", "--username", dest="username", default="automation", help="Jenkins user name")
	parser.add_option("", "--password", dest="password", default="password", help="Jenkins password")
	parser.add_option("-j", "--job", dest="job", default="", type="string", help="Jenkins job name")
	parser.add_option("-b", "--branch", dest="branch", default="", type="string", help="Git branch for the job")
	parser.add_option("-n", "--number", dest="number", type="int", help="Build number as a hint")
	(options, args) = parser.parse_args()

	conn = connect(options.server, options.port, options.username, options.password)
	if conn == None:
		sys.exit(2)

	if options.number:
		logger.info("Checking given build number %d" % options.number)
		found = check_build(conn, options.number)
		if found:
			sys.exit(0)
		else:
			logger.warn("The given build is not in the right branch - not using it.")

	logger.info("Looking for last successful job %s on branch %s" % (options.job, options.branch))

	logger.info("Getting builds for job %s" % options.job)
	job = conn.get_job_info(options.job)
	builds = job["builds"]
	for b in builds:
		found = check_build(conn, b["number"])
		if found:
			sys.exit(0)

	logger.error("Did not found any suitable build.")
	sys.exit(1)

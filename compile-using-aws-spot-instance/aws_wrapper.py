# Author: Alexander Sirotin / sirotin@gmail.com
# Copyright (c) 2017 Alexander Sirotin.
# Licensed under MIT license:
# https://opensource.org/licenses/mit-license.php
# Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

import time
import logging
import boto.ec2
from aws_helper import AwsHelper
from ssh_helper import SSHWrapper

logger = logging.getLogger("builder")

class AwsWrapper:
	def __init__(self, settings):
		self.settings = settings
		self.ec2 = boto.ec2.connect_to_region(self.settings.Region,
		                                      aws_access_key_id=self.settings.Id,
		                                      aws_secret_access_key=self.settings.Secret)
		self.helper = AwsHelper(self.ec2, settings)

		self.instance = None
		self.ssh = SSHWrapper()

	def createInstance(self):
		self.instance = self.helper.requestSpotInstance()
		if not(self.instance):
			raise Exception("Failed creating spot instance")

		# Note: This is optional, the instance is ready for ssh almost 2 minutes before AWS decides it's healthy
		result = self.helper.waitForHealthchecks(self.instance, timeout=300)
		if not(result):
			logger.warn("Failed waiting for instance healthchecks to pass")

	def prepareInstance(self, ip_address=None):
		if ip_address == None:
			ip_address = self.instance.private_ip_address

		result = self.ssh.connect(hostname=ip_address,
								  username=self.settings.UserName,
								  pem="%s.pem" % self.settings.KeyPair,
								  timeout=120)
		if not(result):
			raise Exception("Failed connecting to ssh port for host %s" % ip_address)

		# Some cool-down time
		time.sleep(2)

		# Update host name and mount data volume
		self.ssh.execute("sudo sed -i \"s|127.0.0.1.*|127.0.0.1 localhost `hostname`|g\" /etc/hosts")
		self.ssh.execute("sudo mkdir -p /mnt/data")
		self.ssh.execute("sudo mount /dev/xvdf /mnt/data")

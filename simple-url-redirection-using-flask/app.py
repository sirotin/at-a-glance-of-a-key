# Author: Alexander Sirotin / sirotin@gmail.com
# Copyright (c) 2017 Alexander Sirotin.
# Licensed under MIT license:
# https://opensource.org/licenses/mit-license.php
# Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

import pickledb
import logging
import base64
import json

from functools import wraps
from flask import Flask, request, redirect, abort
app = Flask(__name__)

logger = logging.getLogger()
hdlr = logging.FileHandler("redirections.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s  %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

class RedirectionsStore(object):
    DATABASE_PATH = "redirections.db"

    def __init__(self):
        # True asks the database to dump every change directly to the underlying file
        self.db = pickledb.load(RedirectionsStore.DATABASE_PATH, True)

    def add_record(self, key, value):
        if self.db.get(key) != None:
            return False

        self.db.set(key, value)
        return True

    def get_record(self, key):
        return self.db.get(key)

    def delete_record(self, key):
        self.db.rem(key)

    def get_all_records(self):
        result = dict()
        for key in self.db.getall():
            result[key] = self.db.get(key)
        return result

class ServerImplementation(object):
    @staticmethod
    def add_new_redirection_request():
        # Try parsing base64 key and value
        try:
            key = base64.b64decode(request.json["key"])
            value = base64.b64decode(request.json["value"])
        except Exception as e:
            logger.error("Failed parsing data: %s" % e.message)
            abort(400) # Bad request

        logger.info("Adding redirection with key=%s, value=%s" % (key, value))
        db = RedirectionsStore()
        added = db.add_record(key, value)
        if not(added):
            logger.error("Key already exists - discarding request (key=%s)" % key)
            abort(403) # Forbidden

        return ("", 201) # Created

    @staticmethod
    def delete_redirection_request():
        # Try parsing base64 key
        try:
            key = base64.b64decode(request.json["key"])
        except Exception as e:
            logger.error("Failed parsing data: %s" % e.message)
            abort(400) # Bad request

        logger.info("Deleting redirection with key=%s" % key)
        db = RedirectionsStore()
        db.delete_record(key)
        return ("", 204)

def secure_api(f):
    @wraps(f)
    def implementation(*args, **kwargs):
        auth = request.authorization
        if not(auth):
            logger.error("No authorization supplied, discarding request!")
            abort(401) # Unauthorized

        if (auth.username != "admin" or auth.password != "password"):
            logger.error("Bad user name or password (username=%s, password=%s)" % (auth.username, auth.password))
            abort(401) # Unauthorized

        return f(*args, **kwargs)

    return implementation

@app.route("/mgmt", methods=[ "POST", "DELETE" ])
@secure_api
def api_mgmt():
    # Make sure we receive arguments with json format
    if not(request.json):
        logger.warn("Got mgmt API request not in json format - discarding!")
        abort(415) # Unsupported media type

    if request.method == "POST":
        logger.debug("Handling mgmt POST request")
        return ServerImplementation.add_new_redirection_request()

    elif request.method == "DELETE":
        logger.debug("Handling mgmt DELETE request")
        return ServerImplementation.delete_redirection_request()

    logger.warn("Got mgmt request that cannot be handled")
    abort(400) # Bad request

@app.route("/redirections", methods=[ "GET" ])
@secure_api
def api_redirections():
    logger.info("Got a request to list all redirections from database")

    db = RedirectionsStore()
    records = db.get_all_records()
    result = json.dumps(records)
    return (result, 200)

@app.route("/redirect/<path:key>")
def redirect_request(key):
    logger.info("Got a redirection request with key=%s" % key)

    db = RedirectionsStore()
    result = db.get_record(key)
    if result == None:
        logger.error("Key %s has no redirection defined" % key)
        abort(400) # Bad request

    logger.debug("Redirecting to %s" % result)
    return redirect(result, 302)

if __name__ == "__main__":
    app.run()

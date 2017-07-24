# Author: Alexander Sirotin / sirotin@gmail.com
# Copyright (c) 2017 Alexander Sirotin.
# Licensed under MIT license:
# https://opensource.org/licenses/mit-license.php
# Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

from tests_common import TestBase, setup_logger
import sys

logger = setup_logger("TestPythonVersion")

class TestPythonVersion(TestBase):
    @classmethod
    def run_test(cls):
        result = sys.version_info
        logger.info("Python version is %d.%d.%d" % (result.major, result.minor, result.micro))
        if result.major != 2:
            raise Exception("Expected major version is 2")

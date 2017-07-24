# Author: Alexander Sirotin / sirotin@gmail.com
# Copyright (c) 2017 Alexander Sirotin.
# Licensed under MIT license:
# https://opensource.org/licenses/mit-license.php
# Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

from tests_common import TestBase, setup_logger
import time

logger = setup_logger("TestSleepingAndFailing")

class TestSleepingAndFailing(TestBase):
    @classmethod
    def setup(cls):
        logger.info("Setting up my sleeping environment")

    @classmethod
    def run_test(cls):
        logger.info("Going to sleep for 2 seconds")
        time.sleep(2)
        logger.info("You know what? I'm still tired. need 3 more seconds")
        time.sleep(3)

        raise Exception("I don't want to get up!")

    @classmethod
    def test_down(cls):
        logger.info("Now I need to clean up that mess...")

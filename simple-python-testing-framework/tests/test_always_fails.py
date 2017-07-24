# Author: Alexander Sirotin / sirotin@gmail.com
# Copyright (c) 2017 Alexander Sirotin.
# Licensed under MIT license:
# https://opensource.org/licenses/mit-license.php
# Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

from tests_common import TestBase, setup_logger

logger = setup_logger("TestAlwaysFails")

class TestAlwaysFails(TestBase):
    @classmethod
    def run_test(cls):
        raise Exception("My purpose in life is to fail")

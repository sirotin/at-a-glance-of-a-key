from tests_common import TestBase, setup_logger

logger = setup_logger("TestAlwaysFails")

class TestAlwaysFails(TestBase):
    @classmethod
    def run_test(cls):
        raise Exception("My purpose in life is to fail")

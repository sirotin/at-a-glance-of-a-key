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

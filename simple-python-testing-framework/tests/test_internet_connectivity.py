from tests_common import TestBase, setup_logger
import urllib2

logger = setup_logger("TestInternetConnectivity")

class TestInternetConnectivity(TestBase):
    @classmethod
    def run_test(cls):
        try:
            logger.info("Going to test internet connectivity")
            urllib2.urlopen('http://google.com', timeout=5)
            logger.info("Internet connectivity is ok")
        except urllib2.URLError as err:
            logger.error("Failed connecting to google server")
            raise err

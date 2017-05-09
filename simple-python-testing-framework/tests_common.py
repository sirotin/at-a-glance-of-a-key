import logging
import sys

def setup_logger(name):
    logger = logging.getLogger(name)
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s ("+ name +") %(levelname)s  %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    return logger

class TestBase(object):
    @classmethod
    def setup(cls):
        pass

    @classmethod
    def run_test(cls):
        raise Exception("Not Implemented")

    @classmethod
    def tear_down(cls):
        pass

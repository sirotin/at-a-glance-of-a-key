# Author: Alexander Sirotin / sirotin@gmail.com
# Copyright (c) 2017 Alexander Sirotin.
# Licensed under MIT license:
# https://opensource.org/licenses/mit-license.php
# Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

from optparse import OptionParser
from importlib import import_module
from tests_common import setup_logger
from fnmatch import fnmatch

import traceback
import time
import sys
import os

logger = setup_logger("tests_runner")

def get_available_tests():
    test_base = getattr(sys.modules["tests_common"], "TestBase")

    logger.info("Looking for available tests")
    files = os.listdir(os.path.join(os.getcwd(), "tests"))
    for file in files:
        if file.endswith(".py") and file != "__init__.py":
            logger.debug("+ Found python file %s" % file)
            name = ".".join(file.split(".")[:-1])
            import_module("tests.%s" % name)

    tests = test_base.__subclasses__()
    logger.info("Loaded %d tests:" % len(tests))
    for test in tests:
        logger.info("+ %s" % test.__name__)
    return tests

def filter_tests(tests, pattern):
    filtered = list()
    if not(pattern):
        logger.info("No filtering pattern was supplied")
        return filtered

    patterns = pattern.split(",")

    for t in tests:
        for p in patterns:
            if fnmatch(t.__name__, p.strip()):
                filtered.append(t)
                continue

    logger.info("After filtering tests by given pattern, found %d tests to execute" % len(filtered))
    for t in filtered:
        logger.info("+ %s" % t.__name__)
    return filtered

def run_single_test(test):
    ok = True
    try:
        logger.info("Starting test: %s" % test.__name__)
        test.setup()
        test.run_test()
        logger.info("Test execution completed successfully!")

    except Exception as e:
        logger.error("Test execution failed: %s" % e.message)
        logger.error("-" * 60)
        trace = traceback.format_exc().splitlines()
        for line in trace:
            logger.error(line)
        logger.error("-" * 60)
        ok = False

    finally:
        test.tear_down()

    return ok

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-t", "--tests", dest="tests", help="Comma separated list of tests")
    parser.add_option("-c", "--continue-after-failure", dest="continue_after_failure", action="store_true", help="Continue to the next test in case of test failure")
    (options, args) = parser.parse_args()

    # Load available tests from "tests/" directory
    tests = get_available_tests()
    if len(tests) == 0:
        logger.error("No tests were found, aborting execution!")
        sys.exit(1)

    # Filter the tests we want to run
    to_run = filter_tests(tests, options.tests)

    # Run filtered tests
    passed_tests = 0
    failed_tests = 0
    total_duration = 0
    for test in to_run:
        # Run test and measure execution time
        start_time = time.time()
        ok = run_single_test(test)
        test_duration = time.time() - start_time
        logger.info("Test execution took %.2f seconds" % test_duration)

        total_duration += test_duration

        if ok:
            passed_tests += 1
        else:
            failed_tests += 1
            if not(options.continue_after_failure):
                logger.error("Discarding other tests due to failure")
                break

    logger.info("=" * 60)
    logger.info("Ran %d tests (%d passed, %d failed) in %.2f seconds" % (passed_tests + failed_tests, passed_tests, failed_tests, total_duration))
    sys.exit(1 if (failed_tests > 0) else 0)

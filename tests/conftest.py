import glob
import os
import pytest
import logging

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.dirname(TEST_DIR))

RULES_4X4 = os.path.join(ROOT_DIR, "rules/sudoku-rules-4x4.cnf")
RULES_9X9 = os.path.join(ROOT_DIR, "rules/sudoku-rules-9x9.cnf")


def pytest_sessionstart(session):
    """runs before all tests start https://stackoverflow.com/a/35394239"""
    print("in sessionstart")

    debug = os.environ.get("DEBUG", "0") == "1"
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)
    logging.info(f"setup logging with debug level = {debug}")
    # temporary change that doesn't persist in the terminal after tests complete:
    # if not load_dotenv(override=True, dotenv_path=os.path.join(baseDir, '.env.test')):
    #    print('failed to load dotenv')
    #    exit(1)
    # assert os.environ['ENV'] == 'test', 'ensure dotenv loaded correctly'


@pytest.fixture(autouse=True)
def run_around_tests():
    """code to run before and afer each test https://stackoverflow.com/a/62784688/5500073"""
    # code that will run before a given test:

    yield
    # code that will run after a given test:
    # print("AFTER TEST", flush=True)

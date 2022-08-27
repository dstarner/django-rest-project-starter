"""
This Pytest configuration file is required so that
VSCode Python test discovery works properly
"""
import logging
import pytest


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(autouse=True)
def capture_all_info_logs(caplog):
    caplog.set_level(logging.DEBUG)

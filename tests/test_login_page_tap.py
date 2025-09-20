#!/usr/bin/env python3
import unittest
from unittest.mock import Mock, patch
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage

class DummyElem:
    def __init__(self):
        self.clicked = False
    def click(self):
        self.clicked = True

class TestLoginTap(unittest.TestCase):
    def setUp(self):
        self.mock_driver = Mock()
        self.page = LoginPage(self.mock_driver, default_wait_seconds=0.1)

    @patch("pages.login_page.WebDriverWait")
    def test_tap_login_success_direct(self, mock_wait):
        # WebDriverWait returns element (clickable)
        elem = DummyElem()
        mock_wait.return_value.until.return_value = elem
        self.page.tap_login()
        self.assertTrue(elem.clicked)

    @patch("pages.login_page.WebDriverWait")
    def test_tap_login_timeout_then_scroll_success(self, mock_wait):
        # Primeiro until -> TimeoutException, second until -> returns element
        elem = DummyElem()
        # Simula first call raising, second call returning element
        mock_wait.return_value.until.side_effect = [TimeoutException(), elem]
        # Simula scroll finds element by returning element on find_element(ANDROID_UIAUTOMATOR)
        self.mock_driver.find_element.return_value = elem
        with patch.object(self.page, "_scroll_to_element_by_id", return_value=True) as mock_scroll:
            with patch.object(self.page, "_capture_debug_artifacts") as mock_capture:
                # ensure hide_keyboard exists
                self.mock_driver = self.page.driver
                try:
                    self.page.tap_login()
                except Exception as e:
                    self.fail(f"tap_login raised unexpectedly: {e}")
                mock_scroll.assert_called_once()
                # element is clicked
                self.assertTrue(elem.clicked)

    @patch("pages.login_page.WebDriverWait")
    def test_tap_login_failure_capture(self, mock_wait):
        # Both attempts TimeoutException
        mock_wait.return_value.until.side_effect = TimeoutException()
        with patch.object(self.page, "_scroll_to_element_by_id", return_value=False):
            with patch.object(self.page, "_capture_debug_artifacts") as mock_capture:
                with self.assertRaises(TimeoutException):
                    self.page.tap_login()
                mock_capture.assert_called_once()

if __name__ == "__main__":
    unittest.main()

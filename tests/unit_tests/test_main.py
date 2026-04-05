import unittest
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import status
from fastapi.testclient import TestClient
import src.main as main
from src.main import app, get_settings


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.text.strip('\"'), "I'm healthy !!")

    def test_ping(self):
        response = self.client.get('/ping')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.text.strip('\"'), "I'm healthy !!")

    def test_get_settings(self):
        settings = get_settings()
        self.assertIsNotNone(settings)

    @patch('src.main.OSWValidator')
    def test_startup_event_sets_validator(self, mock_validator):
        validator = MagicMock()
        mock_validator.return_value = validator
        main.app.validator = None

        asyncio.run(main.startup_event())

        self.assertIs(main.app.validator, validator)

    @patch('builtins.print')
    @patch('src.main.psutil.Process')
    @patch('src.main.os.getpid', return_value=123)
    @patch('src.main.OSWValidator', side_effect=Exception('boom'))
    def test_startup_event_handles_validator_init_failure(self, mock_validator, mock_getpid, mock_process, mock_print):
        child_one = MagicMock()
        child_two = MagicMock()
        parent = MagicMock()
        parent.children.return_value = [child_one, child_two]
        mock_process.return_value = parent

        asyncio.run(main.startup_event())

        parent.children.assert_called_once_with(recursive=True)
        child_one.kill.assert_called_once()
        child_two.kill.assert_called_once()
        parent.kill.assert_called_once()
        self.assertGreaterEqual(mock_print.call_count, 6)

    def test_shutdown_event_stops_validator(self):
        validator = MagicMock()
        main.app.validator = validator

        asyncio.run(main.shutdown_event())

        validator.stop_listening.assert_called_once()


if __name__ == '__main__':
    unittest.main()

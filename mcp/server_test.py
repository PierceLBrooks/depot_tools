# Copyright 2025 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for server.py"""
import unittest
from unittest.mock import patch, MagicMock

from absl import app

# Mock modules before they are imported by server
modules_to_mock = [
    'telemetry',
    'buildbucket',
    'codesearch',
    'gclient',
    'git_cl',
    'rdb',
    'utr',
    'mcp.server.fastmcp',
]
for module in modules_to_mock:
    patch(module, MagicMock()).start()

from mcp import server


class ServerTest(unittest.TestCase):

    @patch('mcp.server.fastmcp.FastMCP')
    @patch('telemetry.initialize')
    @patch('absl.app.run')
    def test_main(self, mock_app_run, mock_telemetry_initialize, mock_fast_mcp):
        mock_mcp_instance = MagicMock()
        mock_fast_mcp.return_value = mock_mcp_instance

        # We need to wrap server.main in a lambda to pass it to app.run
        # The actual call to app.run is mocked, so this won't block
        server.main(['test_argv'])

        mock_telemetry_initialize.assert_called_once_with('chromium.mcp')

        # Check that all tools were added
        self.assertEqual(mock_mcp_instance.add_tool.call_count, 15)

        # Check that the server was run
        mock_mcp_instance.run.assert_called_once()

    @patch('absl.app.run')
    def test_main_with_too_many_args(self, mock_app_run):
        with self.assertRaises(app.UsageError):
            server.main(['arg1', 'arg2'])


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
import json
import os
from program_manager import Program, ProgramManager

class TestProgramManager(unittest.TestCase):
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"category": {"program": {"processes": ["notepad.exe"]}}}')
    @patch('os.path.exists')
    def test_load_config(self, mock_exists, mock_open):
        mock_exists.return_value = True
        manager = ProgramManager()
        manager.load_config()
        self.assertIn("category", manager.programs)
        self.assertIn("program", manager.programs["category"])

    @patch('rich.console.Console.print')
    def test_display_menu(self, mock_print):
        manager = ProgramManager()
        manager.display_menu()
        mock_print.assert_called()

    @patch('rich.console.Console.print')
    def test_display_help(self, mock_print):
        manager = ProgramManager()
        manager.display_help()
        mock_print.assert_called()

    @patch('rich.console.Console.print')
    def test_list_programs(self, mock_print):
        manager = ProgramManager()
        manager.list_programs()
        mock_print.assert_called()

    @patch('rich.prompt.Prompt.ask', return_value='0')
    @patch('rich.console.Console.print')
    def test_end_programs(self, mock_print, mock_ask):
        manager = ProgramManager()
        manager.end_programs()
        mock_print.assert_called()

    @patch('rich.prompt.Prompt.ask', return_value='0')
    @patch('rich.console.Console.print')
    def test_end_categories(self, mock_print, mock_ask):
        manager = ProgramManager()
        manager.end_categories()
        mock_print.assert_called()

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"paths": ["C:\\Program Files"]}')
    @patch('json.load', return_value={"paths": ["C:\\Program Files"]})
    @patch('os.path.exists', return_value=True)
    @patch('glob.glob', return_value=["C:\\Program Files\\some_program.exe"])
    @patch('rich.console.Console.print')
    def test_scan_programs(self, mock_print, mock_glob, mock_exists, mock_json_load, mock_open):
        manager = ProgramManager()
        manager.scan_programs()
        mock_print.assert_called()

class TestProgram(unittest.TestCase):
    @patch('subprocess.run')
    def test_is_running(self, mock_run):
        mock_run.return_value.stdout = "notepad.exe"
        program = Program(name="TestProgram", processes=["notepad.exe"])
        self.assertTrue(program.is_running())

    @patch('subprocess.run')
    def test_end(self, mock_run):
        program = Program(name="TestProgram", processes=["notepad.exe"])
        program.end()
        mock_run.assert_called_with(["taskkill", "/IM", "notepad.exe", "/F"], check=True, capture_output=True, encoding='utf-8', errors='replace')

if __name__ == '__main__':
    unittest.main()
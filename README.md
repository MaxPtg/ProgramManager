# Program Manager

Program Manager is a Python-based utility for managing and terminating running programs on Windows systems. It provides an interactive command-line interface for ending individual programs or groups of programs, as well as scanning the system for installed applications.

## Features

- End individual programs or groups of programs
- List program categories
- Scan the system for installed applications
- User-specific configuration files
- Colorful and interactive command-line interface
- Logging for debugging and troubleshooting
- Customizable program categories
- Administrative privileges for more effective process termination

## Installation

1. Ensure you have Python 3.7 or later installed on your system.

2. Clone this repository or download the source code.

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `data` folder in the same directory as the script (if not already present).

5. Create a `data/programs_default_paths.json` file with the following content:

   ```json
   {
     "paths": [
       "C:\\Program Files",
       "C:\\Program Files (x86)",
       "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs",
       "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs",
       "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs"
     ]
   }
   ```

   You can modify this file to include additional paths specific to your system.

6. Create a `programs.json` file in the same directory as the script. This file serves as a template for categorizing programs. See the "Customizing Program Categories" section below for more details.

## Usage

To run the Program Manager:

```bash
python program_manager.py
```

To run in debug mode (for more detailed logging):

```bash
python program_manager.py --debug
```

The program will automatically request administrative privileges to ensure it can terminate processes effectively.

Follow the on-screen prompts to navigate the program:

0. Exit: Close the Program Manager.
1. End a program: Select individual programs to terminate.
2. End program category: Terminate all programs within a selected category.
3. List categories: View all program categories and their contents.
4. Search programs: Scan the system for installed programs and update the user-specific configuration.

## Configuration Files

- `data/programs_default_paths.json`: Contains paths to search for installed programs.
- `programs.json`: Template file for program categories and known executables.
- `data/programs_db_<username>.json`: User-specific file generated after scanning, containing found programs and their paths.

## Logging

The program logs its activities to `data/program_manager.log`. This file is useful for troubleshooting and understanding the program's behavior.

## Customizing Program Categories

You can customize the program categories by editing the `programs.json` file. The structure should look like this:

```json
{
  "Category1": {
    "Program1": {
      "processes": ["program1.exe", "program1_helper.exe"]
    },
    "Program2": {
      "processes": ["program2.exe"]
    }
  },
  "Category2": {
    "Program3": {
      "processes": ["program3.exe"]
    }
  }
}
```

When you run the program scan, the Program Manager will use this template to categorize the found programs.

## Troubleshooting

1. **No programs found during scan:**
   - Check `data/program_manager.log` for scanned paths and any errors.
   - Verify that `data/programs_default_paths.json` contains correct paths for your system.
   - Ensure `programs.json` has correct program names and associated executable names.

2. **Program not terminating:**
   - Ensure you're running the Program Manager with administrator privileges.
   - Check `data/program_manager.log` for any error messages related to terminating processes.

3. **Unexpected behavior:**
   - Run the program in debug mode (`python program_manager.py --debug`) for more detailed logging.
   - Review `data/program_manager.log` for any error messages or unexpected behavior.

## Contributing

Contributions to the Program Manager are welcome! Please feel free to submit pull requests, create issues, or suggest improvements.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Disclaimer

Use this program responsibly. Terminating certain system processes may lead to system instability. Always ensure you have unsaved work saved before terminating any programs.

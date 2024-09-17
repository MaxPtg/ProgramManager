import json
import os
import subprocess
import argparse
import logging
from typing import Dict, List
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.logging import RichHandler
import pyfiglet
import getpass
import glob
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if is_admin():
        return True
    else:
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False

console = Console()

class Program:
    def __init__(self, name: str, processes: List[str], path: str = None):
        self.name = name
        self.processes = processes
        self.path = path

    def is_running(self) -> bool:
        for process in self.processes:
            try:
                result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {process}"], capture_output=True, text=True, encoding='utf-8', errors='replace')
                if result.returncode == 0 and process.lower() in result.stdout.lower():
                    return True
            except subprocess.CalledProcessError:
                logging.error(f"Failed to check if {process} is running")
        return False

    def end(self) -> None:
        for process in self.processes:
            try:
                subprocess.run(["taskkill", "/IM", process, "/F"], check=True, capture_output=True, encoding='utf-8', errors='replace')
                logging.info(f"Successfully ended {process}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to end {process}: {e.stderr.strip()}")

class ProgramManager:
    def __init__(self, config_file: str = "programs.json"):
        self.template_file = config_file
        self.user = getpass.getuser()
        self.user_config_file = f"data/programs_db_{self.user}.json"
        self.programs: Dict[str, Dict[str, Program]] = {}
        self.online_presence_categories: List[str] = []
        self.load_config()

    def load_config(self) -> None:
        try:
            if os.path.exists(self.user_config_file):
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            for category, programs in config.items():
                self.programs[category] = {}
                for name, details in programs.items():
                    self.programs[category][name] = Program(name, details["processes"], details.get("path"))
            logging.info(f"Loaded {sum(len(progs) for progs in self.programs.values())} programs from {len(self.programs)} categories")
        except FileNotFoundError:
            logging.error(f"Config file not found.")
            exit(1)
        except json.JSONDecodeError:
            logging.error(f"Error decoding config file. Please ensure it's a valid JSON file.")
            exit(1)
            
    def display_menu(self) -> None:
        table = Table(title="Main Menu")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")

        options = [
            ("1", "End program(s)"),
            ("2", "End program category(s)"),
            ("3", "List programs by category"),
            ("4", "Scan programs on local machine"),
            ("5", "Help"),
            ("0", "Exit")
        ]

        for option, description in options:
            table.add_row(option, description)

        console.print(table)

    def display_help(self) -> None:
        console.print()
        console.print("[magenta] 1. End program(s):[/magenta] Terminate individual programs by selecting them from the list.")
        console.print("[magenta] 2. End program category(s):[/magenta] Terminate all programs within a selected category.")
        console.print("[magenta] 3. List programs by category:[/magenta] View all programs organized by their categories.")
        console.print("[magenta] 4. Scan programs on local machine:[/magenta] Scan the system for installed programs and update the configuration.")
        console.print("[magenta] 5. Help:[/magenta] Display this help section.")
        console.print("[magenta] 0. Exit:[/magenta] Close the Program Manager.")
        console.print()
        console.print("[yellow] > For further information regarding the scripts functionality, refer to the [cyan]README.md[/cyan] file.[/yellow]")
        console.print()

    def list_programs(self) -> None:
        table = Table(title="Programs")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Category", style="yellow")
        table.add_column("Program", style="magenta")
        table.add_column("Processes", style="blue")
        table.add_column("Status", style="bold")

        option = 1
        for category, programs in self.programs.items():
            for name, program in programs.items():
                try:
                    is_running = program.is_running()
                    status = "[green]Running[/green]" if is_running else "[red]Offline[/red]"
                except Exception as e:
                    logging.error(f"Error checking status for {name}: {str(e)}")
                    status = "[yellow]Unknown[/yellow]"
                table.add_row(
                    str(option),
                    category,
                    name,
                    ", ".join(program.processes),
                    status
                )
                option += 1
            table.add_section()

        table.add_row("0", "Back to Main Menu", "", "", "")
        console.print(table)
        console.print()

    def list_categories(self) -> None:
        table = Table(title="Program Categories")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Category", style="yellow")
        table.add_column("Program", style="magenta")
        table.add_column("Processes", style="blue")
        table.add_column("Status", style="bold")

        option = 1
        for category, programs in self.programs.items():
            first_program = True
            for name, program in programs.items():
                try:
                    is_running = program.is_running()
                    status = "[green]Running[/green]" if is_running else "[red]Offline[/red]"
                except Exception as e:
                    logging.error(f"Error checking status for {name}: {str(e)}")
                    status = "[yellow]Unknown[/yellow]"
                
                if first_program:
                    table.add_row(
                        str(option),
                        category,
                        name,
                        ", ".join(program.processes),
                        status
                    )
                    first_program = False
                else:
                    table.add_row(
                        "",
                        "",
                        name,
                        ", ".join(program.processes),
                        status
                    )
            
            table.add_section()
            option += 1

        table.add_row("0", "Back to Main Menu", "", "", "")
        console.print(table)

    def end_programs(self) -> None:
        while True:
            self.list_programs()
            console.print()
            choices = Prompt.ask("[cyan]? Enter program numbers to end (comma-separated) or 0 to return[/cyan]")

            if choices == "0":
                console.print()
                return

            choices = [int(c.strip()) for c in choices.split(",") if c.strip().isdigit()]
            
            option = 1
            action_taken = False
            results = []
            for category, programs in self.programs.items():
                for name, program in programs.items():
                    if option in choices:
                        try:
                            if program.is_running():
                                logging.debug(f"> Ending program: {name}")
                                program.end()
                                action_taken = True
                                results.append((name, True, ""))
                        except Exception as e:
                            logging.error(f"Error ending program {name}: {str(e)}")
                            results.append((name, False, str(e)))
                    option += 1

            console.print()
            for name, success, reason in results:
                if success:
                    console.print(f"[green]✓ Successfully ended process {name}[/green]")
                else:
                    console.print(f"[red]✗ Could not end process {name} ({reason})[/red]")

            if not action_taken:
                console.print("[yellow]! No viable options were selected or no running programs were found.[/yellow]")
        
    def end_categories(self) -> None:
        while True:
            self.list_categories()
            console.print()
            choices = Prompt.ask("[cyan]? Enter category numbers to end (comma-separated) or 0 to return[/cyan]")

            if choices == "0":
                console.print()
                return

            choices = [int(c.strip()) for c in choices.split(",") if c.strip().isdigit()]
            
            option = 1
            action_taken = False
            results = []
            for category, programs in self.programs.items():
                if option in choices:
                    logging.debug(f"> Ending category: {category}")
                    for name, program in programs.items():
                        try:
                            if program.is_running():
                                program.end()
                                action_taken = True
                                results.append((name, True, ""))
                        except Exception as e:
                            logging.error(f"Error ending program {name} in category {category}: {str(e)}")
                            results.append((name, False, str(e)))
                option += 1

            console.print()
            for name, success, reason in results:
                if success:
                    console.print(f"[green]✓ Successfully ended process {name}[/green]")
                else:
                    console.print(f"[red]✗ Could not end process {name} ({reason})[/red]")

            if not action_taken:
                console.print("[yellow]! No viable options were selected or no running programs were found.[/yellow]")
            
    def end_online_presence(self) -> None:
        table = Table(title="Online Presence Programs")
        table.add_column("Category", style="yellow")
        table.add_column("Program", style="magenta")
        table.add_column("Processes", style="blue")
        table.add_column("Status", style="bold")

        action_taken = False
        for category in self.online_presence_categories:
            if category in self.programs:
                for name, program in self.programs[category].items():
                    try:
                        is_running = program.is_running()
                        status = "[green]Running[/green]" if is_running else "[red]Offline[/red]"
                        if is_running:
                            program.end()
                            action_taken = True
                            status = "[yellow]Ended[/yellow]"
                    except Exception as e:
                        logging.error(f"Error ending program {name}: {str(e)}")
                        status = "[red]Error[/red]"
                    
                    table.add_row(
                        category,
                        name,
                        ", ".join(program.processes),
                        status
                    )

        console.print(table)
        
        if not action_taken:
            console.print("[yellow]! No running online presence programs were found.[/yellow]")
        else:
            console.print("[green]> Online presence programs have been ended.[/green]")

    def scan_programs(self) -> None:
        console.print()
        console.print("[cyan] > Scanning for programs...[/cyan]")
        logging.info("Starting program scan")
        
        # Load program paths
        try:
            with open("data/programs_default_paths.json", "r") as f:
                paths = json.load(f)["paths"]
            logging.debug(f"Loaded {len(paths)} paths from data/programs_default_paths.json")
        except FileNotFoundError:
            logging.error("data/programs_default_paths.json not found")
            console.print("[red]! Error: data/programs_default_paths.json not found[/red]")
            return
        except json.JSONDecodeError:
            logging.error("Error decoding data/programs_default_paths.json")
            console.print("[red]! Error: data/programs_default_paths.json is not a valid JSON file[/red]")
            return

        # Replace %USERNAME% with actual username
        paths = [path.replace("%USERNAME%", self.user) for path in paths]
        
        # Log the resolved paths
        for path in paths:
            logging.info(f"Scanning path: {path}")

        # Load template
        try:
            with open(self.template_file, "r") as f:
                template = json.load(f)
            logging.debug(f"Loaded template from {self.template_file}")
        except FileNotFoundError:
            logging.error(f"{self.template_file} not found")
            console.print(f"[red]! Error: {self.template_file} not found[/red]")
            return
        except json.JSONDecodeError:
            logging.error(f"Error decoding {self.template_file}")
            console.print(f"[red]! Error: {self.template_file} is not a valid JSON file[/red]")
            return

        # Initialize user programs
        user_programs = {category: {} for category in template}

        # Scan for programs
        programs_found = 0
        for path in paths:
            logging.debug(f"Scanning directory: {path}")
            for file in glob.glob(os.path.join(path, "**", "*.exe"), recursive=True):
                filename = os.path.basename(file)
                logging.debug(f"Found executable: {file}")
                for category, programs in template.items():
                    for program, details in programs.items():
                        if filename in details["processes"]:
                            user_programs[category][program] = {
                                "processes": details["processes"],
                                "path": file
                            }
                            logging.info(f"Matched program: {program} ({file})")
                            programs_found += 1

        # Save user programs
        try:
            with open(self.user_config_file, "w") as f:
                json.dump(user_programs, f, indent=2)
            logging.info(f"Saved {programs_found} programs to {self.user_config_file}")
        except IOError:
            logging.error(f"Error writing to {self.user_config_file}")
            console.print(f"[red]! Error: Unable to write to {self.user_config_file}[/red]")
            return

        console.print(f"[green] > Scan complete. {programs_found} programs found and saved to {self.user_config_file}[/green]")
        console.print()
        self.load_config()  # Reload the config to include new programs
        logging.info("Program scan completed")

    def run(self) -> None:
        console.print()
        console.print(pyfiglet.figlet_format("Program Manager™", font="slant"))
        logging.info("Program Manager started")
        try:
            while True:
                self.display_menu()
                console.print()
                choice = Prompt.ask("[cyan] ? Choose an option[/cyan]", choices=["1", "2", "3", "4", "5", "0"])
                logging.debug(f"User chose option: {choice}")

                if choice == "1":
                    self.end_programs()
                elif choice == "2":
                    self.end_categories()
                elif choice == "3":
                    self.list_programs()
                elif choice == "4":
                    self.scan_programs()
                elif choice == "5":
                    self.display_help()
                elif choice == "0":
                    break

        except KeyboardInterrupt:
            logging.info("Exiting program due to user interrupt")
        finally:
            console.print()
            console.print(pyfiglet.figlet_format("See you soon!", font="slant"))
            logging.info("Program Manager finished")

def setup_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="data/program_manager.log",
        filemode="a"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Program Manager")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    setup_logging(args.debug)

    if run_as_admin():
        logging.debug("Starting Program Manager with admin privileges")
        manager = ProgramManager()
        manager.run()
        logging.debug("Program Manager finished")
    else:
        logging.info("Restarting with admin privileges...")
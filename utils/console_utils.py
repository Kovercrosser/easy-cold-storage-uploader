from typing import Optional
from rich.console import Console
from rich.table import Table

console = Console()

class LastMessage:
    last_message = ""
    def set(self, msg: str) -> None:
        self.last_message = msg
    def get(self) -> str:
        return self.last_message
last_message: LastMessage = LastMessage()

def clear_console(new_header: str = "") -> None:
    last_message.set("")
    console.clear()
    if new_header:
        console.print(new_header + "\n")

def print_error(error: str) -> None:
    message = "[bold red]Error: " + error + "[/bold red]"
    last_message.set(message)
    console.print(message)

def print_warning(warning: str) -> None:
    message = "[bold yellow]Warning: " + warning + "[/bold yellow]"
    last_message.set(message)
    console.print(message)

def print_success(success: str) -> None:
    message = "[bold green]" + success + "[/bold green]"
    last_message.set(message)
    console.print(message)

def force_user_input_from_list(header: str, user_options: list[str]) -> int:
    console.print( header + ": ")
    table = Table()
    table.show_header = True
    table.add_column("Options", justify="right")
    table.add_column("Description", justify="left")
    for index, option in enumerate(user_options):
        table.add_row(str(index + 1), option)
    console.print(table)
    while True:
        choice = input("Enter the number of your choice: ")
        if choice.isdigit() and 1 <= int(choice) <= len(user_options):
            break
        print_warning("Invalid input. Please try again")
    return int(choice)

def force_user_input(header: str, valid_options: Optional[list[str]]) -> str:
    if valid_options:
        valid_options = []
    console.print("\n" + header + ": ")
    while True:
        choice = input()
        if (not valid_options or choice in valid_options) and choice != "":
            break
        print_warning("Invalid input. Please try again")
    return choice

def handle_console_exit() -> None:
    console.set_alt_screen(False)
    console.print(last_message.get())

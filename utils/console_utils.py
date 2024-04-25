from typing import Optional
from rich.console import Console

console = Console()
console.set_alt_screen()

def clear_console(new_header: str = "") -> None:
    console.clear()
    if new_header:
        console.print(new_header + "\n")

def print_error(error: str) -> None:
    console.print("[bold red]Error: " + error + "[/bold red]")

def print_warning(warning: str) -> None:
    console.print("[bold yellow]Warning: " + warning + "[/bold yellow]")

def print_success(success: str) -> None:
    console.print("[bold green]" + success + "[/bold green]")

def force_user_input_from_list(header: str, user_options: list[str]) -> int:
    console.print("\n" + header + ": ")
    for index, option in enumerate(user_options):
        console.print(str(index + 1) + ": " + str(option))
    console.print("\n")
    while True:
        choice = input("\nEnter your choice: ")
        if choice.isdigit() and 1 <= int(choice) <= len(user_options):
            break
        console.print("Invalid input. Please try again.")
    return int(choice)

def force_user_input(header: str, valid_options: Optional[list[str]]) -> str:
    if valid_options:
        valid_options = []
    console.print("\n" + header + ": ")
    while True:
        choice = input("\nEnter your value: ")
        if (not valid_options or choice in valid_options) and choice != "":
            break
        console.print("Invalid input. Please try again.")
    return choice

import os
from typing import Optional
from rich import print as printx

def clear_console(new_header: str = "") -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
    if new_header:
        printx(new_header + "\n")

def force_user_input_from_list(header: str, user_options: list[str]) -> int:
    printx("\n" + header + ": ")
    for index, option in enumerate(user_options):
        printx(str(index + 1) + ": " + str(option))
    printx("\n")
    while True:
        choice = input("\nEnter your choice: ")
        if choice.isdigit() and 1 <= int(choice) <= len(user_options):
            break
        printx("Invalid input. Please try again.")
    return int(choice)

def force_user_input(header: str, valid_options: Optional[list[str]]) -> str:
    if valid_options:
        valid_options = []
    printx("\n" + header + ": ")
    while True:
        choice = input("\nEnter your value: ")
        if (not valid_options or choice in valid_options) and choice != "":
            break
        printx("Invalid input. Please try again.")
    return choice

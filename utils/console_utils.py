import os

def clear_console(new_header: str = None):
    os.system('cls' if os.name == 'nt' else 'clear')
    if new_header is not None:
        print(new_header + "\n")

def force_user_input_from_list(header: str, user_options: list) -> int:
    print("\n" + header + ": ")
    for index, option in enumerate(user_options):
        print(str(index + 1) + ": " + str(option))
    print("\n")
    while True:
        choice = input("\nEnter your choice: ")
        if choice.isdigit() and 1 <= int(choice) <= len(user_options):
            break
        print("Invalid input. Please try again.")
    return int(choice)

def force_user_input(header: str, valid_options: list = None) -> str:
    if valid_options is None:
        valid_options = []
    print("\n" + header + ": ")
    while True:
        choice = input("\nEnter your value: ")
        if (not valid_options or choice in valid_options) and choice != "":
            break
        print("Invalid input. Please try again.")
    return choice

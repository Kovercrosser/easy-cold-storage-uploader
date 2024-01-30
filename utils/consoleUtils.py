import os

def clearConsole(newHeader: str = None):
    os.system('cls' if os.name == 'nt' else 'clear')
    if newHeader is not None:
        print(newHeader + "\n")

def forceUserInputFromList(header: str, userOptions: list) -> int:
    print("\n" + header + ": ")
    for index, option in enumerate(userOptions):
        print(str(index + 1) + ": " + str(option))
    print("\n")
    while True:
        choice = input("\nEnter your choice: ")
        if choice.isdigit() and 1 <= int(choice) <= len(userOptions):
            break
        else:
            print("Invalid input. Please try again.")
    return int(choice)

def forceUserInput(header: str, validOptions: list = None) -> str:
    if validOptions is None:
        validOptions = []
    print("\n" + header + ": ")
    while True:
        choice = input("\nEnter your value: ")
        if (not validOptions or choice in validOptions) and choice != "":
            break
        else:
            print("Invalid input. Please try again.")
    return choice

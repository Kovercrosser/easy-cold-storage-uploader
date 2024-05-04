import os

def get_all_files_from_directories_and_files(paths: list[str]) -> list[str]:
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
        else:
            for root, _, all_files in os.walk(path):
                for file in all_files:
                    file_path = os.path.join(root, file)
                    files.append(file_path)
    return files

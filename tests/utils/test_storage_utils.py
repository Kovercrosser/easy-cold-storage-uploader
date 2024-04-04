import os
import json
import random
import shutil
from utils.storage_utils import get_all_files_from_directories_and_files, store_settings, read_settings

def test_get_all_files_from_directories_and_files():
    # Test get_all_files_from_directories_and_files
    paths = [".testpath/test1", ".testpath/test2", ".testpath/test3/test1", ".testpath/test3/test2",
             ".testpath/test4/test1", ".testpath/test4/test2", ".testpath2/test1", ".testpath2/test2"]
    for index, path in enumerate(paths):
        os.makedirs(path, exist_ok=True)
        if index % 2 == 0:
            with open(os.path.join(path, "file1.txt"), "w", encoding="utf8") as file:
                file.write("test")
            with open(os.path.join(path, "file2.txt"), "w", encoding="utf8") as file:
                file.write("test")
            with open(os.path.join(path, "file3.txt"), "w", encoding="utf8") as file:
                file.write("test")
            with open(os.path.join(path, "file4.txt"), "w", encoding="utf8") as file:
                file.write("test")
    files = ["test1.txt", "test2.txt", "test3.txt", "test4.txt"]
    for file in files:
        with open(file, "w", encoding="utf8") as f:
            f.write("test")
    paths.extend(files)
    random.shuffle(paths)
    expected_result = [ "test1.txt", "test2.txt", "test3.txt", "test4.txt",".testpath/test3/test1/file1.txt",
                       ".testpath/test3/test1/file2.txt", ".testpath/test3/test1/file3.txt",
                       ".testpath/test3/test1/file4.txt", ".testpath/test4/test1/file1.txt",
                       ".testpath/test4/test1/file2.txt", ".testpath/test4/test1/file3.txt",
                       ".testpath/test4/test1/file4.txt", ".testpath/test1/file1.txt",
                       ".testpath/test1/file2.txt", ".testpath/test1/file3.txt",
                       ".testpath/test1/file4.txt",  ".testpath2/test1/file1.txt",
                       ".testpath2/test1/file2.txt", ".testpath2/test1/file3.txt",
                       ".testpath2/test1/file4.txt"]
    assert get_all_files_from_directories_and_files(paths).sort() == expected_result.sort()
    for file in files:
        os.remove(file)
    shutil.rmtree(".testpath")
    shutil.rmtree(".testpath2")
    
def test_get_all_files_from_directories_and_files_empty():
    # Test get_all_files_from_directories_and_files with empty paths
    assert get_all_files_from_directories_and_files([]) == []

def test_store_settings():
    # Test store_settings
    profile = "test_profile"
    key = "test_key"
    value = "test_value"

    # Create a temporary directory for testing
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Set the temporary directory as the home directory
    os.environ["HOME"] = temp_dir

    # Call the store_settings function
    store_settings(profile, key, value)

    # Verify that the settings file is created
    settings_file = os.path.join(temp_dir, ".ecsu", "settings.json")
    assert os.path.exists(settings_file)

    # Read the contents of the settings file
    with open(settings_file, "r", encoding="utf-8") as file:
        settings_data = file.read()

    # Verify that the settings file contains the expected data
    expected_data = {
        profile: {
            key: value
        }
    }
    assert json.loads(settings_data) == expected_data

    # Clean up the temporary directory
    os.environ["HOME"] = ""
    os.remove(settings_file)
    os.rmdir(os.path.join(temp_dir, ".ecsu"))
    os.rmdir(temp_dir)


def test_read_settings():
    # Test read_settings
    profile = "test_profile"
    key = "test_key"
    value = "test_value"

    # Create a temporary directory for testing
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Set the temporary directory as the home directory
    os.environ["HOME"] = temp_dir

    # Create a settings file with test data
    settings_file = os.path.join(temp_dir, ".ecsu", "settings.json")
    settings_data = {
        profile: {
            key: value
        }
    }
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    with open(settings_file, "w", encoding="utf-8") as file:
        file.write(json.dumps(settings_data))

    # Call the read_settings function
    result = read_settings(profile, key)

    # Verify that the correct value is returned
    assert result == value

    # Clean up the temporary directory
    os.environ["HOME"] = ""
    os.remove(settings_file)
    os.rmdir(os.path.join(temp_dir, ".ecsu"))
    os.rmdir(temp_dir)
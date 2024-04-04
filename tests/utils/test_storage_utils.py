import os
import random
import shutil
from utils.storage_utils import get_all_files_from_directories_and_files

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
    random.seed(0)
    random.shuffle(paths)
    expected_result = ["test2.txt", "test1.txt", "test3.txt", ".testpath/test3/test1/file1.txt",
                       ".testpath/test3/test1/file2.txt", ".testpath/test3/test1/file3.txt",
                       ".testpath/test3/test1/file4.txt", ".testpath/test4/test1/file1.txt",
                       ".testpath/test4/test1/file2.txt", ".testpath/test4/test1/file3.txt",
                       ".testpath/test4/test1/file4.txt", ".testpath/test1/file1.txt",
                       ".testpath/test1/file2.txt", ".testpath/test1/file3.txt",
                       ".testpath/test1/file4.txt", "test4.txt", ".testpath2/test1/file1.txt",
                       ".testpath2/test1/file2.txt", ".testpath2/test1/file3.txt",
                       ".testpath2/test1/file4.txt"]
    assert get_all_files_from_directories_and_files(paths) == expected_result
    for file in files:
        os.remove(file)
    shutil.rmtree(".testpath")
    shutil.rmtree(".testpath2")

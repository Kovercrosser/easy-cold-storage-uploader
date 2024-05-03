
from io import BufferedRandom
from random import randbytes, randint
import tempfile
from typing import Any, Generator

import pytest
from utils.data_utils import CreateSplittedFilesFromGenerator, get_file_size
import os

input_file = os.path.join(os.path.curdir, "tests", "utils", "testdata_input")
output_file = os.path.join(os.path.curdir, "tests", "utils", "testdata_output")

@pytest.fixture(autouse=True)
def run_around_tests() -> Generator[Any, Any, Any]:
    if os.path.exists(input_file):
        os.remove(input_file)
    if os.path.exists(output_file):
        os.remove(output_file)
    yield
    if os.path.exists(input_file):
        os.remove(input_file)
    if os.path.exists(output_file):
        os.remove(output_file)

@pytest.mark.parametrize("input_chunk_size, output_chunk_size, test_file_size_mb, input_chunk_size_random_max",
                        [(512, 1024, 20, 0), (64, 1024, 20, 0), (64, (1024*1024*50), 50, 0), (1024, 512, 50, 0), (2048, 512, 50, 0),
                        ((1024*1024*10), 2048, 20, 0), ((1024*1024*10), (1024*1024*10), 100, 0), (1024, 1024, 100, 0), ((1024*1024*300),
                        (1024*1024*10), 100, 0),((1024*1024*10), (1024*1024*255), 100, 0), (512, 1024, 50, 2048), (5, 2048, 100, 20000)])
def test_create_splitted_files_from_generator(input_chunk_size:int, output_chunk_size:int, test_file_size_mb:int, input_chunk_size_random_max:int) -> None:
    # Tests that the Input File and the Output File are the same    
    with open(input_file, 'wb') as f:
        for _ in range(test_file_size_mb):
            f.write(randbytes((1024*1024)))
    
    with open(input_file, mode='r+b') as f:
        def data_generator() -> Generator[bytes, None, None]:
            while True:
                chunk_size = input_chunk_size
                if input_chunk_size_random_max != 0:
                    chunk_size = randint(input_chunk_size, input_chunk_size_random_max)
                data = f.read(chunk_size)
                if len(data) == 0:
                    return
                yield data

        creater = CreateSplittedFilesFromGenerator()
        with open(output_file, mode="b+w") as save_file:
            last_chunk_free = False # Last Chunk can be smaller in size than the output_chunk_size
            while True:
                with tempfile.TemporaryFile(mode="b+w") as temp_file:
                    try:
                        creater.create_next_upload_size_part(data_generator(), output_chunk_size, temp_file)
                    except StopIteration:
                        break
                    size = get_file_size(temp_file)
                    if size != output_chunk_size:
                        if last_chunk_free:
                            assert False
                        else:
                            last_chunk_free = True
                    assert size <= output_chunk_size
                    save_file.write(temp_file.read())
    
    with open(input_file, 'rb') as original_file:
        with open(output_file, 'rb') as new_file:
            assert original_file.read() == new_file.read()

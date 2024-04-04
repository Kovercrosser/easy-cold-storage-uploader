import pytest
from utils.hash_utils import compute_sha256_tree_hash

def test_compute_sha256_tree_hash():
    # List of an empty string should raise ValueError
    chunk_sha256_hashes = ['']
    with pytest.raises(ValueError):
        compute_sha256_tree_hash(chunk_sha256_hashes)

    # Empty list should raise ValueError
    with pytest.raises(ValueError):
        compute_sha256_tree_hash([])

    # Lit of not strings should raise ValueError
    with pytest.raises(ValueError):
        compute_sha256_tree_hash([1,2,3])

    # Single chunk SHA256 hash
    chunk_sha256_hashes = ["hash1"]
    expected_result = "af316ecb91a8ee7ae99210702b2d4758f30cdde3bf61e3d8e787d74681f90a6e"
    assert compute_sha256_tree_hash(chunk_sha256_hashes) == expected_result

    # Multiple chunk SHA256 hashes
    chunk_sha256_hashes = ["hash1", "hash2", "hash3"]
    expected_result = "ad3400ac1fd4bd995ff7eda7857c3c034d32a90a4abf79f08475a9ba3482c4e5"
    assert compute_sha256_tree_hash(chunk_sha256_hashes) == expected_result

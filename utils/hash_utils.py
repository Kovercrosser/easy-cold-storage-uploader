import binascii
import hashlib

def compute_sha256_tree_hash_for_aws(chunk_sha256_hashes: list[bytes]) -> str:
    if not isinstance(chunk_sha256_hashes, list) or not all(isinstance(i, bytes) for i in chunk_sha256_hashes) or not all(chunk_sha256_hashes):
        raise ValueError("Invalid input")
    if not chunk_sha256_hashes:
        raise ValueError("List is empty")
    chunks = chunk_sha256_hashes
    if len(chunks) == 1:
        return binascii.hexlify(chunks[0]).decode('ascii')
    while len(chunks) > 1:
        new_chunks:list[str] = []
        first = None
        second = None
        for chunk in chunks:
            if first is None:
                first = chunk
            elif second is None:
                second = chunk
                new_chunks.append(hashlib.sha256(first + second).digest())
                first = None
                second = None
        if first is not None:
            new_chunks.append(first)
        chunks = new_chunks
    return binascii.hexlify(chunks[0]).decode('ascii')

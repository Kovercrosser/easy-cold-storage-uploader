import hashlib

def compute_sha256_tree_hash(chunk_sha256_hashes: list[str]) -> str:
    if not isinstance(chunk_sha256_hashes, list) or not all(isinstance(i, str) for i in chunk_sha256_hashes):
        raise ValueError("Invalid input")
    chunks = chunk_sha256_hashes
    if not chunks:
        return hashlib.sha256(b'').digest()
    while len(chunks) > 1:
        new_chunks:list[str] = []
        first = None
        second = None
        for chunk in chunks:
            if first is None:
                first = chunk
            elif second is None:
                second = chunk
                new_chunks.append(compute_sha256_hash(first + second))
                first = None
                second = None
        if first is not None:
            new_chunks.append(first)
        chunks = new_chunks
    return chunks[0]

def compute_sha256_hash(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()

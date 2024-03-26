import hashlib

def compute_sha256_tree_hash(chunk_sha256_hashes: list[str]) -> str:
    sha256 = hashlib.sha256
    chunks:list[bytes] = [h.encode() for h in chunk_sha256_hashes]
    if not chunks:
        return sha256(b'').digest()
    while len(chunks) > 1:
        new_chunks:list[bytes] = []
        first = None
        second = None
        for a in chunks:
            if first is None:
                first = a
            elif second is None:
                second = a
                new_chunks.append(sha256(first + second).digest())
                first = None
                second = None
        if first is not None:
            new_chunks.append(first)
        chunks = new_chunks
    return chunks[0].hex()

import hashlib

def computeSha256TtreeHash(chunkSha256Hashes: list[str]) -> str:
    sha256 = hashlib.sha256
    chunks:list[bytes] = [h.encode() for h in chunkSha256Hashes]
    if not chunks:
        return sha256(b'').digest()
    while len(chunks) > 1:
        newChunks:list[bytes] = []
        first = None
        second = None
        for a in chunks:
            if first is None:
                first = a
            elif second is None:
                second = a
                newChunks.append(sha256(first + second).digest())
                first = None
                second = None
        if first is not None:
            newChunks.append(first)
        chunks = newChunks
    return chunks[0].hex()

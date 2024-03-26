import hashlib
from itertools import zip_longest

# def calculateTreeHash(checksums: list[str]) -> str:
#     if not checksums:
#         return ""
#     while len(checksums) > 1:
#         treeHashLevel = []
#         for i in range(0, len(checksums), 2):
#             if i + 1 < len(checksums):
#                 combinedHash = hashlib.sha256((checksums[i] + checksums[i + 1]).encode('utf-8')).hexdigest()
#             else:
#                 combinedHash = checksums[i]
#             treeHashLevel.append(combinedHash)
#         checksums = treeHashLevel
#     return checksums[0]


# def computeSha256TtreeHash(chunkSha256Hashes: list[str]) -> str:
#     prevLvlHashes: list[bytes] = [h.encode() for h in chunkSha256Hashes]

#     while len(prevLvlHashes) > 1:
#         currLvlHashes = []
#         j = 0
#         for i in range(0, len(prevLvlHashes), 2):
#             if i + 1 < len(prevLvlHashes):
#                 # Calculate a digest of the concatenated nodes
#                 h = hashlib.sha256()
#                 h.update(prevLvlHashes[i])
#                 h.update(prevLvlHashes[i + 1])
#                 currLvlHashes.append(h.digest())
#             else:
#                 # Take care of remaining odd chunk
#                 currLvlHashes.append(prevLvlHashes[i])
#             j += 1

#         prevLvlHashes = currLvlHashes

#     return prevLvlHashes[0].hex()

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

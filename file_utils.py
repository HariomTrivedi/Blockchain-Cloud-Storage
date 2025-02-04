import os

def split_file(file):
    chunk_size = 1 * 1024 * 1024  # 1MB
    chunks = []
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        chunks.append(chunk)
    return chunks

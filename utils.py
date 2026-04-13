import hashlib

def calculate_checksum(filename):
    hash_md5 = hashlib.md5()

    with open(filename, "rb") as f:
        while chunk := f.read(4096):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()
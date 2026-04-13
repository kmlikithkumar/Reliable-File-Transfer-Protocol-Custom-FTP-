import asyncio
import os
import time

HOST = '127.0.0.1'
PORT = 9000
CHUNK_SIZE = 4096

# 🔹 CHANGE THIS to your folder path
BASE_DIR = r"C:\Users\admin\Downloads\CN Project FTP\test_files"

# 🔹 Downloads folder
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ---------------- FILE PATH RESOLVER ----------------
def resolve_path(filename):
    # Case 1: absolute path
    if os.path.exists(filename):
        return filename

    # Case 2: inside BASE_DIR
    alt_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(alt_path):
        return alt_path

    return None


# ---------------- UPLOAD ----------------
async def upload(filename):
    full_path = resolve_path(filename)

    if not full_path:
        print(f"ERROR: File '{filename}' not found")
        print("Checked paths:")
        print(" -", filename)
        print(" -", os.path.join(BASE_DIR, filename))
        return

    print("Using file:", full_path)

    reader, writer = await asyncio.open_connection(HOST, PORT)

    filesize = os.path.getsize(full_path)
    start = time.time()

    writer.write(f"UPLOAD {os.path.basename(full_path)} {filesize}\n".encode())
    await writer.drain()

    try:
        with open(full_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                writer.write(chunk)
                await writer.drain()

        response = await reader.readline()
        end = time.time()

        duration = end - start
        throughput = filesize / duration / 1024

        print(f"Upload complete | {duration:.3f}s | {throughput:.2f} KB/s")

    except Exception as e:
        print("Upload failed:", e)

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass


# ---------------- DOWNLOAD ----------------
async def download(filename):
    reader, writer = await asyncio.open_connection(HOST, PORT)

    writer.write(f"DOWNLOAD {filename}\n".encode())
    await writer.drain()

    response = await reader.readline()

    if response.startswith(b"ERROR"):
        print(response.decode())
        writer.close()
        await writer.wait_closed()
        return

    filesize = int(response.decode().strip())

    # 🔹 Unique filename to avoid overwrite
    timestamp = int(time.time())
    save_path = os.path.join(DOWNLOAD_DIR, f"{timestamp}_{filename}")

    start = time.time()

    try:
        with open(save_path, "wb") as f:
            remaining = filesize
            while remaining > 0:
                chunk = await reader.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    raise ConnectionError("Download interrupted")
                f.write(chunk)
                remaining -= len(chunk)

        end = time.time()

        duration = end - start
        throughput = filesize / duration / 1024

        print(f"Download complete → {save_path}")
        print(f"Time: {duration:.3f}s | Throughput: {throughput:.2f} KB/s")

    except Exception as e:
        print("Download failed:", e)

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass


# ---------------- LIST ----------------
async def list_files():
    reader, writer = await asyncio.open_connection(HOST, PORT)

    writer.write(b"LIST\n")
    await writer.drain()

    data = await reader.read(4096)

    print("\nFiles on server:")
    print(data.decode())

    writer.close()
    await writer.wait_closed()


# ---------------- MAIN LOOP ----------------
async def main():
    print("\n=== ASYNC FTP CLIENT ===")
    print("Base Directory:", BASE_DIR)
    print("Download Directory:", os.path.abspath(DOWNLOAD_DIR))

    while True:
        cmd = input("\nEnter (upload/download/list/exit): ").strip().lower()

        if cmd == "upload":
            file = input("Enter filename: ").strip()
            await upload(file)

        elif cmd == "download":
            file = input("Enter filename: ").strip()
            await download(file)

        elif cmd == "list":
            await list_files()

        elif cmd == "exit":
            print("Exiting client...")
            break

        else:
            print("Invalid command")


if __name__ == "__main__":
    asyncio.run(main())
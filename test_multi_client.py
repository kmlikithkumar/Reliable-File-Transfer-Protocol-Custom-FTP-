import asyncio
import os
import time

HOST = '127.0.0.1'
PORT = 9000
CHUNK_SIZE = 4096

TEST_FILES_DIR = r"C:\Users\admin\Downloads\CN Project FTP\test_files"
DOWNLOAD_DIR = "downloads"

# Create downloads folder
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ---------------- GET FILES ----------------
def get_files():
    if not os.path.exists(TEST_FILES_DIR):
        print("ERROR: Directory not found:", TEST_FILES_DIR)
        return []

    files = [
        f for f in os.listdir(TEST_FILES_DIR)
        if os.path.isfile(os.path.join(TEST_FILES_DIR, f))
    ]

    if not files:
        print("ERROR: No files found in directory")

    return files


# ---------------- UPLOAD ----------------
async def upload_file(client_id, filepath):
    filename = os.path.basename(filepath)

    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)

        filesize = os.path.getsize(filepath)
        start = time.time()

        writer.write(f"UPLOAD {filename} {filesize}\n".encode())
        await writer.drain()

        with open(filepath, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                writer.write(chunk)
                await writer.drain()

        await reader.readline()
        end = time.time()

        duration = end - start
        throughput = filesize / duration / 1024

        print(f"[UPLOAD {client_id}] {filename} | {duration:.3f}s | {throughput:.2f} KB/s")

    except Exception as e:
        print(f"[UPLOAD {client_id}] ERROR:", e)

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass


# ---------------- DOWNLOAD ----------------
async def download_file(client_id, filename):
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)

        start = time.time()

        writer.write(f"DOWNLOAD {filename}\n".encode())
        await writer.drain()

        response = await reader.readline()

        if response.startswith(b"ERROR"):
            print(f"[DOWNLOAD {client_id}] NOT FOUND: {filename}")
            return

        filesize = int(response.decode().strip())

        save_path = os.path.join(DOWNLOAD_DIR, f"client{client_id}_{filename}")

        with open(save_path, "wb") as f:
            remaining = filesize
            while remaining > 0:
                chunk = await reader.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)

        end = time.time()

        duration = end - start
        throughput = filesize / duration / 1024

        print(f"[DOWNLOAD {client_id}] {filename} | {duration:.3f}s | {throughput:.2f} KB/s → {save_path}")

    except Exception as e:
        print(f"[DOWNLOAD {client_id}] ERROR:", e)

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass


# ---------------- MAIN ----------------
async def main():
    files = get_files()

    if not files:
        return

    print("\nAvailable files:")
    for f in files:
        print(" -", f)

    num_clients = int(input("\nEnter number of clients: "))

    print("\n--- PHASE 1: UPLOAD ---")

    upload_tasks = []
    for i in range(num_clients):
        file = files[i % len(files)]
        filepath = os.path.join(TEST_FILES_DIR, file)
        upload_tasks.append(upload_file(i, filepath))

    await asyncio.gather(*upload_tasks)

    print("\n--- PHASE 2: DOWNLOAD ---")

    download_tasks = []
    for i in range(num_clients):
        file = files[i % len(files)]
        download_tasks.append(download_file(i, file))

    await asyncio.gather(*download_tasks)


if __name__ == "__main__":
    asyncio.run(main())
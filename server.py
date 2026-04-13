import asyncio
import os
import logging

HOST = '127.0.0.1'
PORT = 9000
CHUNK_SIZE = 4096
TIMEOUT = 30
STORAGE_DIR = "storage"

# Setup directories
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Logging configuration
logging.basicConfig(
    filename="logs/server.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ---------------- CLIENT HANDLER ----------------
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    logging.info(f"Connected: {addr}")

    try:
        data = await asyncio.wait_for(reader.readline(), timeout=TIMEOUT)

        if not data:
            return

        command = data.decode().strip().split()

        if not command:
            return

        cmd = command[0]

        # -------- LIST --------
        if cmd == "LIST":
            files = os.listdir(STORAGE_DIR)
            response = "\n".join(files) + "\n"

            writer.write(response.encode())
            await writer.drain()

            logging.info(f"LIST requested by {addr}")

        # -------- UPLOAD --------
        elif cmd == "UPLOAD":
            if len(command) < 3:
                writer.write(b"ERROR Invalid UPLOAD command\n")
                await writer.drain()
                return

            filename = command[1]
            filesize = int(command[2])

            filepath = os.path.join(STORAGE_DIR, os.path.basename(filename))
            temp_path = filepath + ".tmp"

            logging.info(f"UPLOAD start: {filename} ({filesize} bytes) from {addr}")

            try:
                with open(temp_path, "wb") as f:
                    remaining = filesize

                    while remaining > 0:
                        chunk = await reader.read(min(CHUNK_SIZE, remaining))

                        if not chunk:
                            raise ConnectionError("Upload interrupted")

                        f.write(chunk)
                        remaining -= len(chunk)

                # Atomic replace
                os.replace(temp_path, filepath)

                writer.write(b"OK\n")
                await writer.drain()

                logging.info(f"UPLOAD complete: {filename}")

            except Exception as e:
                logging.error(f"UPLOAD failed: {filename} | {e}")

                if os.path.exists(temp_path):
                    os.remove(temp_path)

                writer.write(b"ERROR Upload failed\n")
                await writer.drain()

        # -------- DOWNLOAD --------
        elif cmd == "DOWNLOAD":
            if len(command) < 2:
                writer.write(b"ERROR Invalid DOWNLOAD command\n")
                await writer.drain()
                return

            filename = command[1]
            filepath = os.path.join(STORAGE_DIR, filename)

            if not os.path.exists(filepath):
                writer.write(b"ERROR File not found\n")
                await writer.drain()
                logging.warning(f"DOWNLOAD failed (not found): {filename}")
                return

            filesize = os.path.getsize(filepath)

            logging.info(f"DOWNLOAD start: {filename} ({filesize} bytes) to {addr}")

            writer.write(f"{filesize}\n".encode())
            await writer.drain()

            try:
                with open(filepath, "rb") as f:
                    while chunk := f.read(CHUNK_SIZE):
                        writer.write(chunk)
                        await writer.drain()

                logging.info(f"DOWNLOAD complete: {filename}")

            except Exception as e:
                logging.error(f"DOWNLOAD failed: {filename} | {e}")

        # -------- UNKNOWN COMMAND --------
        else:
            writer.write(b"ERROR Unknown command\n")
            await writer.drain()
            logging.warning(f"Unknown command from {addr}: {cmd}")

    # ---------------- ERROR HANDLING ----------------
    except asyncio.TimeoutError:
        logging.warning(f"Timeout: {addr}")

    except ConnectionResetError:
        logging.warning(f"Client disconnected abruptly: {addr}")

    except ConnectionAbortedError:
        logging.warning(f"Connection aborted (WinError 10053): {addr}")

    except Exception as e:
        logging.error(f"Unhandled error {addr}: {e}")

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass

        logging.info(f"Disconnected: {addr}")


# ---------------- SERVER START ----------------
async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)

    addr = server.sockets[0].getsockname()
    print(f"Server running on {addr[0]}:{addr[1]}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
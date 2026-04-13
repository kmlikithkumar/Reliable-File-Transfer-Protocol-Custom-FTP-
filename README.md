# AsyncFTP — Asynchronous File Transfer System

> A scalable, chunk-based FTP implementation in pure Python using `asyncio`. Built as a Computer Networks course project.

---

## Overview

AsyncFTP follows a client-server architecture allowing multiple clients to upload, download, and manage files on a central server — with no external dependencies.

**Key design goals:** high concurrency, low memory footprint, and reliable atomic file transfers.

---

## Features

- **Async I/O** — built on `asyncio`; handles many clients concurrently without threads
- **Chunk-based transfer** — 4096-byte chunks keep memory usage flat regardless of file size
- **Atomic writes** — files are written to a temp path and renamed on completion, preventing partial/corrupt uploads
- **SHA-256 integrity** — packets carry checksums for verification
- **Throughput tracking** — real-time KB/s reported per transfer
- **Timeout handling** — stale connections are detected and cleaned up
- **Extensible protocol** — sequence numbers and chunk metadata support future UDP adaptation

---

## Project Structure

```
CN-Project-FTP/
├── server.py              # Async TCP server (asyncio event loop)
├── client.py              # Client interface
├── protocol.py            # Packet format, chunking, hashing
├── test_multi_client.py   # Concurrent client stress tests
├── storage/               # Server-side file storage
├── logs/                  # Connection and transfer logs
├── cert.pem               # SSL certificate (future use)
├── key.pem                # SSL private key (future use)
└── README.md
```

---

## Architecture

```
Client(s)
    │
    ▼  TCP Socket
Async Server (asyncio Event Loop)
    │
    ├── Protocol Layer (chunking, sequence numbers, SHA-256)
    │
    └── File Storage + Logging
```

Multiple clients connect over TCP. The event loop dispatches each connection as a coroutine, so no threads are needed. The protocol layer handles packetization before data touches the filesystem.

---

## Setup

**Requirements:** Python 3.8+ — no external libraries.

```bash
# Start the server (listens on port 9000)
python server.py

# Connect with the client
python client.py
```

---

## Supported Commands

| Command | Description |
|---|---|
| `LIST` | List all files available on the server |
| `UPLOAD <filename>` | Upload a local file to the server |
| `DOWNLOAD <filename>` | Download a file from the server |

---

## How It Works

### Upload

1. Client sends `UPLOAD <filename> <size>`
2. Server reads the file stream in 4096-byte chunks
3. Data is written to a `.tmp` file
4. On completion, the temp file is atomically renamed to the final path — ensuring no partial file is ever visible to other clients

### Download

1. Client sends `DOWNLOAD <filename>`
2. Server responds with the file size
3. File is streamed in chunks until complete

### Protocol Packet Format

Each chunk carries metadata for ordering and integrity:

| Field | Description |
|---|---|
| Sequence number | Position of this chunk in the stream |
| Total chunks | Allows receiver to detect missing chunks |
| Data length | Actual byte count in this chunk |
| SHA-256 hash | Integrity check (per-file) |

---

## Testing

Run the multi-client stress test to verify concurrent behaviour:

```bash
python test_multi_client.py
```

This spins up several clients simultaneously to test upload throughput, server stability under load, and correct file output.

---

## Logging

Logs are written to `/logs/` and capture:
- Client connections and disconnections
- File transfer start/completion events
- Errors and timeouts

---

## Known Limitations

| Limitation | Impact |
|---|---|
| No authentication | Any client can connect and access files |
| No encryption (TLS not yet active) | Data is transmitted in plaintext |
| TCP only | No UDP fast-path for large file scenarios |
| No resume support | Interrupted transfers must restart from scratch |

---

## Planned Improvements

- TLS encryption (cert/key already in place)
- Resume support for interrupted transfers
- File compression before transfer
- UDP-based protocol variant
- User authentication

---

## License

Academic project — Computer Networks course.

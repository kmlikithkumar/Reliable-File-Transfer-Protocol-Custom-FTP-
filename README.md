# 📦 Asynchronous FTP System (CN Project)

## 📌 Overview
This project implements a custom File Transfer Protocol (FTP) system using Python with a focus on:
- Asynchronous networking
- High concurrency
- Efficient file transfer
- Reliability and fault tolerance

The system follows a client-server architecture allowing multiple clients to upload, download, and manage files on a central server.

---

## 🚀 Features

### ⚡ Asynchronous Server
- Built using Python asyncio
- Handles multiple clients concurrently without threads

### 📂 File Operations
- Upload files
- Download files
- List files on server

### 📊 Performance Optimization
- Chunk-based file transfer (reduces memory usage)
- Throughput calculation (KB/s)
- Timeout handling

### 🔒 Reliability
- Atomic file writes using temporary files
- Cleanup of incomplete uploads
- Robust error handling

### 🧩 Extensible Protocol
- Custom protocol design
- Sequence numbers and hashing support
- Future-ready for UDP

---

## 🏗️ Architecture

Client(s)
   ↓
TCP Socket
   ↓
Async Server (Event Loop)
   ↓
File Storage + Logging

---

## 📁 Project Structure

CN Project FTP/
│
├── server.py              # Async FTP server
├── client.py              # Client interface
├── protocol.py            # Protocol and chunking logic
├── test_multi_client.py   # Multi-client testing
│
├── storage/               # Stored files
├── logs/                  # Logs
│
├── cert.pem               # SSL cert (future use)
├── key.pem                # SSL key (future use)
│
└── README.md

---

## ⚙️ Working

### 1. Server Start
- Listens on port 9000
- Accepts multiple client connections asynchronously

### 2. Commands Supported

| Command | Description |
|--------|------------|
| LIST | Show files |
| UPLOAD filename size | Upload file |
| DOWNLOAD filename | Download file |

---

### 3. Upload Flow
1. Client sends: UPLOAD filename size
2. Server reads file in chunks
3. Writes to temporary file
4. Atomically replaces final file

Key concept:
- Prevents corruption using atomic write

---

### 4. Download Flow
1. Client requests file
2. Server sends file size
3. File streamed in chunks

---

### 5. Protocol Layer
- Chunk size: 4096 bytes
- Packet format includes:
  - Sequence number
  - Total chunks
  - Data length
- File integrity using SHA-256 hashing

---

## 📊 Performance Features

| Feature | Benefit |
|--------|--------|
| Async I/O | High scalability |
| Chunking | Low memory usage |
| Streaming | Efficient transfer |
| Timeout | Avoids hanging |
| Throughput tracking | Performance analysis |

---

## 🧪 Testing

Run multi-client test:

```bash
python test_multi_client.py
```

Tests:
- Concurrent uploads
- Server load handling
- Stability

---

## ▶️ Setup

### Requirements
- Python 3.8+
- No external libraries required

---

### Run Server
```bash
python server.py
```

---

### Run Client
```bash
python client.py
```

---

### Example Commands
```
LIST
UPLOAD sample.txt
DOWNLOAD sample.txt
```

---

## 📄 Logging
Logs stored in /logs

Tracks:
- Connections
- File transfers
- Errors

---

## ⚠️ Limitations

| Issue | Impact |
|------|-------|
| No authentication | Security risk |
| No encryption | Data not secure |
| TCP only | No UDP optimization |
| No resume support | Restart needed |

---

## 🔮 Future Improvements

- TLS encryption
- Resume upload/download
- File compression
- UDP-based protocol
- Authentication system

---

## 📌 Highlights

- Asynchronous architecture
- Atomic file handling
- Chunk-based transfer
- Performance monitoring
- Protocol extensibility

---

## 🧠 Learning Outcomes

- Async programming
- Socket communication
- File I/O optimization
- System design
- Protocol engineering

---

## 📜 License
Academic project (Computer Networks)

---

## ⭐ Summary
A scalable, efficient, and reliable asynchronous FTP system demonstrating modern networking techniques using Python.
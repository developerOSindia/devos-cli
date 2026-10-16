# DeveloperOS Unified CLI (`devos`)

```text
  ____                 _                         ___  ____  
 |  _ \  _____   _____| | ___  _ __   ___ _ __  / _ \/ ___| 
 | | | |/ _ \ \ / / _ \ |/ _ \| '_ \ / _ \ '__|| | | \___ \ 
 | |_| |  __/\ V /  __/ | (_) | |_) |  __/ |   | |_| |___) |
 |____/ \___| \_/ \___|_|\___/| .__/ \___|_|    \___/|____/ 
                              |_|                           
 DeveloperOS Unified Developer CLI • Zero Dependencies • Offline-First
 https://developeros.in
```

> **Zero-dependency, ultra-fast Python CLI for the DeveloperOS developer tools ecosystem.**

`devos` provides essential, daily developer utilities directly in your terminal with **zero external dependencies** (Python standard library only), **100% offline in-memory execution**, and **zero telemetry**.

---

## ⚡ Core Highlights

- **Zero Third-Party Dependencies**: Powered exclusively by the Python 3.10+ standard library.
- **Ultra-Fast & Offline**: Instant startup time (<10ms). Never transmits data over the network.
- **Unix Pipeline Friendly**: Reads smoothly from `stdin` (`-` or pipes) and emits clean `stdout` for chaining with `grep`, `jq`, and shell scripts.
- **Ecosystem Integrated**: Embedded directory of all DeveloperOS suites, tools, and live deployment links.

---

## 🚀 Installation

### Option 1: Editable Local Install (Recommended)
```bash
cd infrastructure/devos-cli
pip install -e .
```

After installation, the `devos` command is globally accessible in your environment:
```bash
devos --version
```

### Option 2: Direct Execution (No Install Needed)
```bash
python3 -m devos.cli --help
```

---

## 🛠️ Subcommands & Usage Guide

### 1. `json` — Formatting, Minification & Syntax Validation

Format, sort keys, minify, or validate JSON payloads according to RFC 8259.

```bash
# Pretty-print JSON (default indent: 2 spaces)
devos json '{"name":"devos","author":"DeveloperOS","active":true}'

# Minify payload
devos json -m '{"name": "devos", "version": 1}'

# Sort dictionary keys alphabetically
devos json -s '{"z": 10, "a": 20, "m": 30}'

# Strict RFC 8259 syntax validation
devos json -v '{"valid": true}'
devos json -v '{"broken": json}'

# Read directly from a file or stdin pipe
devos json config.json
cat payload.json | devos json -m
```

---

### 2. `jwt` — JWT Claims Inspection & Expiry Validation

Parse and inspect JSON Web Tokens without external cryptography libraries.

```bash
# Full inspection with header, claims, timestamps, and signature
devos jwt eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# View claims (payload) only
devos jwt -c eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# View header only
devos jwt --header eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Output full inspection as structured JSON
devos jwt --json eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Check expiration status (exits 0 if active, 1 if expired)
devos jwt --verify-exp eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 3. `hash` — Cryptographic Checksums (SHA-256, SHA-512, MD5, SHA-1)

Generate cryptographic digests for text strings, streamed data, or files with chunked memory streaming.

```bash
# Default SHA-256 hash of a string
devos hash -t "hello world"

# Compute specific algorithm
devos hash -a md5 -t "hello world"
devos hash -a sha512 -t "hello world"
devos hash -a sha1 -t "hello world"

# Compute all supported algorithms simultaneously
devos hash -a all -t "developer-os"

# Uppercase hex digest
devos hash -a sha256 --upper -t "hello"

# Hash a file (reads in 64KB chunks, memory-safe for large files)
devos hash -f /path/to/archive.tar.gz

# Output JSON
devos hash -a sha256 --json -t "secret"
```

---

### 4. `b64` — Base64 & URL-Safe Encoding / Decoding

RFC 4648 standard and URL-safe Base64 encoder/decoder with automatic padding correction.

```bash
# Encode plain text
devos b64 "DeveloperOS Tools"

# Decode Base64 string
devos b64 -d "RGV2ZWxvcGVyT1MgVG9vbHM="

# URL-safe encoding/decoding (- and _ instead of + and /)
devos b64 -u "special?data=true"
devos b64 -d -u "c3BlY2lhbD9kYXRhPXRydWU="

# Encode/decode files directly
devos b64 -f logo.png -o logo.b64
devos b64 -d -f logo.b64 -o restored.png
```

---

### 5. `uuid` — RFC 4122 UUIDv4 Batch Generator

Generate random UUIDv4 identifiers in standard, uppercase, or continuous 32-character hexadecimal format.

```bash
# Generate single UUID
devos uuid

# Generate multiple UUIDs in batch
devos uuid -n 5

# Format in uppercase
devos uuid -u

# Omit hyphens (32-character hex)
devos uuid --no-hyphens

# Output as JSON array
devos uuid -n 3 --json
```

---

### 6. `cron` — Schedule Parser & Next-Run Calculator

Validate 5-field cron expressions, translate them to human-readable English, and calculate upcoming execution dates.

```bash
# Explain schedule and calculate next 5 execution times
devos cron "*/15 * * * *"

# Standard cron aliases
devos cron "@hourly"
devos cron "@daily"
devos cron "@weekly"

# Calculate custom number of runs from a specific start date
devos cron "0 9-17 * * 1-5" -n 10 --from 2026-10-16T09:00:00

# JSON output
devos cron "30 2 * * 0" --json
```

---

### 7. `list` — Tool Registry & Live Links Directory

Browse the entire catalog of DeveloperOS tools, suites, and flagship applications.

```bash
# List all tools organized by category
devos list

# Filter by category (web, api, security, data, devops, code, database, media, documentation, performance, flagship)
devos list -c security
devos list -c api

# Search tools by keyword
devos list -s jwt
devos list -s json

# Verbose output with full tool descriptions
devos list -s regex -v

# Output full registry catalog as JSON
devos list --json
```

---

## 🧪 Testing

Run the isolated test suite using Python's built-in `unittest`:

```bash
python3 -m unittest discover -s tests
```

To run all ecosystem tests across the DeveloperOS-Tools monorepo:
```bash
python3 ../../scripts/run_all_tests.py
```

---

## 🔒 Security & Privacy Guarantees

- **100% In-Memory Processing**: Inputs and outputs are never cached or written to temporary storage unless explicitly instructed via file flags.
- **Zero Network Traffic**: No remote APIs, telemetry, phone-home metrics, or update-check pings.
- **Strict Standard Library**: Independent of external PyPI packages, minimizing supply-chain attack vectors.

---

## 📄 License

Licensed under the [MIT License](LICENSE).  
Copyright (c) 2026 DeveloperOS Team ([https://developeros.in](https://developeros.in)).

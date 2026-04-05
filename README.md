# 🐳 Docker Image Types — Size Comparison & Best Practices

<div align="center">

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)

**A hands-on demo comparing Docker base image types — sizes, use cases, and when to choose what.**

*Built by [Akshay Sawant](mailto:akshaysawant9009@gmail.com) — AWS DevOps Engineer |  Pune*

---

</div>

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Real Output — My Docker Experiment](#-real-output--my-docker-experiment)
- [The 5 Types of Docker Images](#-the-5-types-of-docker-images)
- [Image Size Comparison Table](#-image-size-comparison-table)
- [Which Image for Which Language?](#-which-image-for-which-language)
- [Dockerfile Examples](#-dockerfile-examples)
- [Key Learnings](#-key-learnings)
- [Folder Structure](#-folder-structure)
- [How to Run This Project](#-how-to-run-this-project)

---

## 🎯 Project Overview

> **"The Docker image you choose decides 4 critical things: Size, Security, Speed, and Tooling."**

When building containerized applications, the base image you pick has a **huge impact** on:

| Factor | Impact |
|--------|--------|
| 📦 **Image Size** | Affects pull time, storage, and bandwidth cost |
| 🔒 **Security** | More packages = more CVE vulnerabilities |
| ⚡ **Startup Speed** | Smaller images boot faster |
| 🛠️ **Debugging** | Some images have no shell at all |

This project runs the **same Python Flask app** on 4 different base images and compares the results — with **real terminal output** from my local Docker setup.

---

## 📊 Real Output — My Docker Experiment

Here's the actual `docker images` output from my MacBook running Docker Desktop:

```
IMAGE                     ID             DISK USAGE   CONTENT SIZE
─────────────────────────────────────────────────────────────────────
py-standard:latest        dedce3dfe223     1.62 GB        404 MB    ← Full Python 3.11
py.slim:latest            7cecabaa3473      236 MB        51.4 MB   ← Python 3.11-slim
py.alpine:latest          a99dc25f453d     88.5 MB        20.9 MB   ← Python 3.11-alpine
py.distroless:latest      f62a69de4113      223 MB        51.7 MB   ← Google Distroless
```

### 🔥 Size Reduction Achieved:

```
py-standard   ████████████████████████████████████████  1.62 GB  (baseline)
py.slim       ██████                                     236 MB   ↓ 85% smaller
py.distroless ██████                                     223 MB   ↓ 86% smaller
py.alpine     ██                                         88.5 MB  ↓ 94% smaller
```

> **94% size reduction** by switching from `python:3.11` → `python:3.11-alpine` for the same app!

---

## 🐳 The 5 Types of Docker Images

### 1️⃣ Standard / Full Images
> *"The kitchen sink — everything included"*

```dockerfile
FROM python:3.11
```

- **Size:** 300 MB – 1.6 GB
- **Contains:** Full OS, package manager (apt), build tools, documentation, dev utilities
- **Best For:** Local development, debugging, CI build stages
- **Example Tags:** `python:3.11`, `node:18`, `ubuntu:24.04`

```
✅ Easy to debug          ✅ All tools available
✅ No dependency issues   ❌ Very large size
❌ More attack surface    ❌ Slow to pull/push
```

---

### 2️⃣ Slim Images
> *"Production-ready, batteries not included"*

```dockerfile
FROM python:3.11-slim
```

- **Size:** 50 MB – 150 MB
- **Contains:** Minimal Debian/Ubuntu OS, basic utilities, **no build tools**
- **Best For:** Production deployments, balanced size vs. compatibility
- **Example Tags:** `python:3.11-slim`, `node:18-slim`

```
✅ Much smaller than full   ✅ Familiar Debian base
✅ Good for production      ❌ Need to install build deps manually
✅ Easy migration from full ❌ Slightly larger than Alpine
```

---

### 3️⃣ Alpine Images
> *"Ultralight — but know what you're doing"*

```dockerfile
FROM python:3.11-alpine
```

- **Size:** 2 MB – 50 MB
- **Contains:** Alpine Linux, `apk` package manager, `musl libc` (NOT glibc!)
- **Best For:** Go apps, simple scripts, microservices with no C-extensions
- **Example Tags:** `python:3.11-alpine`, `node:18-alpine`, `nginx:alpine`

```
✅ Smallest possible size   ✅ Fast to pull and deploy
✅ Great for Go/Node        ❌ musl libc ≠ glibc (breaks Python C-extensions)
⚠️  Avoid for Python unless you handle musl carefully
```

> ⚠️ **Important Warning for Python developers:**
> Alpine uses `musl libc` instead of `glibc`. Many Python packages like `numpy`, `pandas`, `scipy` have C extensions compiled against `glibc` — they will **fail to install or run** on Alpine. Use `slim` instead for Python.

---

### 4️⃣ Distroless Images (by Google)
> *"No shell, no OS tools, just your app"*

```dockerfile
FROM gcr.io/distroless/python3
```

- **Size:** 2 MB – 30 MB (runtime only)
- **Contains:** Only the language runtime. **No shell, no package manager, no OS utilities**
- **Best For:** Immutable production containers with maximum security
- **Registry:** [gcr.io/distroless](https://github.com/GoogleContainerTools/distroless)

```
✅ Maximum security (no shell = no shell injection)
✅ Smallest attack surface
✅ Used in security-critical production systems
❌ Cannot exec into container for debugging (no /bin/sh)
❌ Complex multi-stage build required
❌ Harder to troubleshoot issues
```

**Typical multi-stage pattern with Distroless:**
```dockerfile
# Stage 1: Build
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

# Stage 2: Run (Distroless — no shell!)
FROM gcr.io/distroless/python3
WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app
CMD ["app.py"]
```

---

### 5️⃣ Scratch Images
> *"Absolute zero — start from nothing"*

```dockerfile
FROM scratch
```

- **Size:** 0 MB (literally empty)
- **Contains:** Absolutely nothing — no OS, no shell, no tools
- **Best For:** Statically compiled binaries only (Go, Rust, C)

```
✅ Absolute minimum size     ✅ Maximum security
✅ Perfect for Go binaries   ❌ Requires statically compiled app
❌ Impossible to debug       ❌ Not suitable for Python/Node/Java
```

---

## 📐 Image Size Comparison Table

| Image Type | Base Tag Example | Typical Size | Shell | Package Mgr | Use Case |
|------------|-----------------|-------------|-------|-------------|----------|
| 🔵 Standard | `python:3.11` | 300MB–1.6GB | ✅ bash | ✅ apt | Development |
| 🟡 Slim | `python:3.11-slim` | 50MB–150MB | ✅ sh | ✅ apt (minimal) | Production |
| 🟢 Alpine | `python:3.11-alpine` | 5MB–50MB | ✅ sh | ✅ apk | Lightweight prod |
| 🔴 Distroless | `gcr.io/distroless/python3` | 2MB–30MB | ❌ None | ❌ None | Secure production |
| ⬛ Scratch | `scratch` | 0 MB | ❌ None | ❌ None | Go/Rust binaries |

---

## 🎯 Which Image for Which Language?

```
🐹  Go Application
    ┌─────────────────────────────────────────────────────┐
    │  BEST CHOICES:  scratch > distroless > alpine       │
    │  REASON: Go compiles to a static binary             │
    │  AVOID:  Standard (overkill)                        │
    └─────────────────────────────────────────────────────┘

🐍  Python Application
    ┌─────────────────────────────────────────────────────┐
    │  BEST CHOICES:  slim > distroless                   │
    │  REASON: C-extensions need glibc (Debian-based)     │
    │  AVOID:  Alpine ⚠️  (musl libc breaks many packages) │
    └─────────────────────────────────────────────────────┘

🟢  Node.js Application
    ┌─────────────────────────────────────────────────────┐
    │  BEST CHOICES:  node:18-slim > node:18-alpine       │
    │  REASON: Slim for npm packages needing build tools  │
    │  AVOID:  Standard in production                     │
    └─────────────────────────────────────────────────────┘

♨️  Java Application
    ┌─────────────────────────────────────────────────────┐
    │  BEST CHOICES:  eclipse-temurin:21-jdk-slim         │
    │                 gcr.io/distroless/java21             │
    │  REASON: JVM needs proper glibc support             │
    │  AVOID:  Alpine (JVM + musl = compatibility issues) │
    └─────────────────────────────────────────────────────┘

🦀  Rust Application
    ┌─────────────────────────────────────────────────────┐
    │  BEST CHOICES:  scratch > distroless > alpine       │
    │  REASON: Rust compiles to static binaries           │
    └─────────────────────────────────────────────────────┘
```

---

## 📄 Dockerfile Examples

All 4 Dockerfiles used in this project for the same Python Flask app:

### `dockerfile` — Standard
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8080
CMD ["python", "app.py"]
```
> 📦 Result: **1.62 GB** — Full Debian + all Python tools

---

### `dockerfile.slim` — Slim
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8080
CMD ["python", "app.py"]
```
> 📦 Result: **236 MB** — Minimal Debian, pip still works perfectly

---

### `dockerfile.alpine` — Alpine
```dockerfile
FROM python:3.11-alpine AS builder
WORKDIR /app
COPY app.py .

FROM python:3.11-alpine
WORKDIR /app
COPY --from=builder /app/app.py .
CMD ["python", "app.py"]
```
> 📦 Result: **88.5 MB** — Smallest, but watch for musl issues with complex deps

---

### `dockerfile.distro` — Distroless (Multi-stage)
```dockerfile
FROM python:3.11 AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

FROM gcr.io/distroless/python3:latest
WORKDIR /app
COPY --from=base /usr/local /usr/local
COPY --from=base /app /app
CMD ["app.py"]
```
> 📦 Result: **223 MB** — No shell, maximum security for production

---

## 💡 Key Learnings

### ✅ What I Learned from This Experiment

```
1. Image naming matters!
   ❌ Wrong:  docker run py-slim       (Docker tries to pull from registry)
   ✅ Correct: docker run py.slim      (uses local image with dot notation)

2. pip-install ≠ pip install
   ❌ Wrong:  RUN pip-install --no-cache-dir -r requirements.txt
   ✅ Correct: RUN pip install --no-cache-dir -r requirements.txt

3. Alpine alpine app.py crash (Exit code 1)
   Reason: Missing dependencies or musl incompatibility
   Solution: Add build deps or switch to slim

4. docker build typo
   ❌ Wrong:  docker built -t ...
   ✅ Correct: docker build -t ...
```

### 🏆 The Decision Framework

```
Are you in DEVELOPMENT?
  └── YES → Use Standard (python:3.11) — full tooling, easy debug

Are you going to PRODUCTION?
  ├── Python app?
  │     └── Use SLIM (python:3.11-slim) — best compatibility + small size
  ├── Go / Rust app?
  │     └── Use SCRATCH or DISTROLESS — static binary, zero overhead
  ├── Node.js app?
  │     └── Use SLIM or ALPINE — check npm deps for native modules
  └── Security-critical system?
        └── Use DISTROLESS — no shell = reduced attack surface
```

---

## 📁 Folder Structure

```
docker-image-types/
├── app1/
│   ├── app.py                  # Simple Python Flask app
│   ├── requirements.txt        # Flask dependency
│   ├── dockerfile              # Standard: python:3.11
│   ├── dockerfile.slim         # Slim: python:3.11-slim
│   ├── dockerfile.alpine       # Alpine: python:3.11-alpine
│   └── dockerfile.distro       # Distroless: gcr.io/distroless/python3
└── README.md                   # This file
```

---

## 🚀 How to Run This Project

```bash
# Clone the repository
git clone https://github.com/yourusername/docker-image-types.git
cd docker-image-types/app1

# Build all 4 images
docker build -t py-standard    -f dockerfile       .
docker build -t py.slim        -f dockerfile.slim   .
docker build -t py.alpine      -f dockerfile.alpine .
docker build -t py.distroless  -f dockerfile.distro .

# Check sizes
docker images | grep "py"

# Run them side by side on different ports
docker run -d --name python.standard  -p 9001:8080 py-standard
docker run -d --name python.slim      -p 9002:8080 py.slim
docker run -d --name python.alpine    -p 9003:8080 py.alpine

# Test each
curl http://localhost:9001
curl http://localhost:9002
curl http://localhost:9003

# Clean up
docker stop python.standard python.slim python.alpine
docker rm   python.standard python.slim python.alpine
```

---

## 🧠 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────────┐
│              DOCKER IMAGE TYPES — QUICK REFERENCE                    │
├──────────────┬──────────┬────────┬──────────┬────────────────────────┤
│ Type         │ Size     │ Shell  │ Pkg Mgr  │ Best For               │
├──────────────┼──────────┼────────┼──────────┼────────────────────────┤
│ Standard     │ 300MB+   │  ✅   │  ✅ apt  │ Development            │
│ Slim         │ 50-150MB │  ✅   │  ✅ apt  │ Python/Node Production │
│ Alpine       │ 5-50MB   │  ✅   │  ✅ apk  │ Go/Node/Simple scripts │
│ Distroless   │ 2-30MB   │  ❌   │  ❌      │ Secure Production      │
│ Scratch      │ 0 MB     │  ❌   │  ❌      │ Go/Rust Static Bins    │
└──────────────┴──────────┴────────┴──────────┴────────────────────────┘

🐍 Python  → SLIM        🐹 Go     → SCRATCH/DISTROLESS
🟢 Node.js → SLIM/ALPINE ♨️  Java   → eclipse-temurin:slim
```

---

## 👨‍💻 Author

**Akshay Sawant**
AWS DevOps Engineer | AWS Solutions Architect Associate

[![Email](https://img.shields.io/badge/Email-akshaysawant9009@gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:akshaysawant9009@gmail.com)
[![Phone](https://img.shields.io/badge/Phone-+91_9096505065-25D366?style=flat-square&logo=whatsapp&logoColor=white)](tel:+919096505065)
[![Location](https://img.shields.io/badge/Location-Hinjawadi,_Pune-4285F4?style=flat-square&logo=googlemaps&logoColor=white)](https://maps.google.com)

---

<div align="center">

⭐ **If this helped you, give it a star!** ⭐

*Part of my DevOps learning series — see more projects on my [GitHub](https://github.com/yourusername)*

</div>

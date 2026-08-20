# RetainPDF: Layout-Preserving PDF Translation Engine & Platform

<p align="center">
  <b>English</b> | <a href="README_zh.md">中文</a>
</p>

<p align="center">
  <img src="image/RetainPDF-github.svg" alt="RetainPDF" width="320" />
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://github.com/chocolatedesue/retain-pdf/releases"><img src="https://img.shields.io/github/v/release/chocolatedesue/retain-pdf?include_prereleases" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20Docker-brightgreen" alt="Platform">
</p>

**RetainPDF** is an open-source, full-stack document translation platform engineered to solve one of the hardest problems in document intelligence: **translating complex PDFs while strictly preserving their visual layout, formatting, typography, mathematical formulas, and table structures.**

Unlike conventional PDF translation tools that only support copyable text and simple layouts, RetainPDF is built from the ground up to handle **dense scientific papers (SCI/IEEE/ACM), textbooks, technical documentation, and scanned/image-based PDFs**.

---

## 🚀 Key Differentiators & Comparison

| Feature / Capability | PDFMathTranslate | PolyglotPDF | Doc2X (Closed-source) | **RetainPDF (Ours)** |
| :--- | :--- | :--- | :--- | :--- |
| **Scanned / Image-based PDFs** | ❌ Unsupported | ❌ Unsupported | ✅ Supported | ✅ **Full Pipeline Support** |
| **Complex Inline & Block LaTeX** | ❌ Prone to breakage | ❌ Prone to breakage | ✅ Supported | ✅ **AST Token Placeholder Guards** |
| **Code Block Protection** | ❌ Often translated | ❌ Often translated | ❌ Fragile | ✅ **Semantic Detection & Preservation** |
| **Table Layout Control** | Weak | Weak | Moderate | ✅ **Controlled Extraction & Reconstruction** |
| **Custom Translation Policies** | Weak | Weak | Weak | ✅ **`fast`, `sci`, `precise` Multi-mode** |
| **Glossary / Terminology Support** | ❌ No | ❌ No | Weak | ✅ **Named Glossaries & Inline Terms** |
| **Layout Fidelity** | Moderate | Moderate | High | ✅ **High-Fidelity Re-synthesis** |
| **Adaptive Font Scaling & Sizing**| Moderate | Moderate | Weak | ✅ **Dynamic Auto-Scaling + PDF Optimization** |
| **Open REST API & Self-Hosting** | ✅ Supported | ✅ Supported | ❌ Proprietary | ✅ **High-Performance Rust API + Docker** |
| **Cross-Platform Desktop Apps** | ❌ Weak | ❌ Weak | ❌ Web-only | ✅ **Windows / macOS / Linux GUI** |

---

## 📸 Showcase & Visual Results

### 1. Scientific & Academic Papers (SCI / IEEE / ACM)

<p align="center">
  <img src="image/image%201.png" alt="SCI Paper Example 1" width="860" />
</p>

<p align="center">
  <img src="image/image%202.png" alt="SCI Paper Example 2" width="860" />
</p>

### 2. Scanned & Image-Based PDFs

<p align="center">
  <img src="image/image%203.png" alt="Scanned PDF Example 1" width="860" />
</p>

<p align="center">
  <img src="image/image%207.png" alt="Scanned PDF Example 2" width="860" />
</p>

### 3. Textbooks & Technical Manuals

<p align="center">
  <img src="image/image%204.png" alt="Book Example 1" width="860" />
</p>

<p align="center">
  <img src="image/image%205.png" alt="Book Example 2" width="860" />
</p>

<p align="center">
  <img src="image/image%206.png" alt="Book Example 3" width="860" />
</p>

---

## ⚡ Quick Start

### 1. Desktop Client (Recommended for Personal Use)

Download pre-built installation packages directly from [GitHub Releases](https://github.com/chocolatedesue/retain-pdf/releases):

- **Windows**: `RetainPDF-x.x.x-Setup.exe` (or portable `.exe`)
- **macOS**: `RetainPDF-x.x.x-mac-x64.dmg` / `arm64.dmg`
- **Linux**: `RetainPDF-x.x.x-linux-amd64.deb`

<p align="center">
  <img src="image/RetainPDF-desktop.png" alt="RetainPDF Windows Desktop Client" width="860" />
</p>

> **macOS Note**: If prompted with "App is damaged" on first launch due to unsigned binaries, run:
> ```bash
> sudo xattr -r -d com.apple.quarantine /Applications/RetainPDF.app
> ```

---

### 2. Docker Deployment (Recommended for Teams & Self-Hosting)

The repository provides production-ready Docker Compose configurations:

- [docker/delivery/README.md](docker/delivery/README.md)
- [docker/delivery/docker-compose.yml](docker/delivery/docker-compose.yml)

#### Launch with Pre-built Images

```bash
git clone https://github.com/chocolatedesue/retain-pdf.git
cd retain-pdf/docker/delivery
docker compose up -d
```

Access the Web UI at: `http://127.0.0.1:40001`

- `40001`: Frontend Web Application (Reverse proxy included)
- `41000`: Rust API Full Engine Port
- `42000`: Synchronous Translation Bundle Endpoint

#### Build from Source

```bash
cd retain-pdf/docker/delivery
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

#### Update Images

```bash
cd retain-pdf/docker/delivery
docker compose pull
docker compose up -d
```

Official Docker Hub Images:
- [wxyhgk/retainpdf-app](https://hub.docker.com/r/wxyhgk/retainpdf-app)
- [wxyhgk/retainpdf-web](https://hub.docker.com/r/wxyhgk/retainpdf-web)

---

## 🛠️ CLI & REST API Automation

RetainPDF exposes high-throughput asynchronous and synchronous REST APIs.

### Synchronous Bundle API (One-Shot Translation)

```bash
curl -X POST "http://127.0.0.1:40001/api/v1/translate/bundle" \
  -H "X-API-Key: your-rust-api-key" \
  -F "file=@/path/to/paper.pdf" \
  -F "ocr_provider=paddle" \
  -F "paddle_token=your-paddle-token" \
  -F "base_url=https://api.openai.com/v1" \
  -F "api_key=your-openai-api-key" \
  -F "model=gpt-4o" \
  -F "mode=sci" \
  -F "workers=100" \
  -F "batch_size=1" \
  -o translated_bundle.zip
```

### Asynchronous Job Workflow

1. **Upload Document**: `POST /api/v1/uploads`
2. **Create Processing Job**: `POST /api/v1/jobs`
3. **Poll Status & Diagnostics**: `GET /api/v1/jobs/{job_id}`
4. **Download Artifacts**:
   - `GET /api/v1/jobs/{job_id}/pdf` — Translated PDF
   - `GET /api/v1/jobs/{job_id}/markdown?raw=true` — Extracted & Translated Markdown
   - `GET /api/v1/jobs/{job_id}/download` — Full ZIP Archive with debug diagnostics

---

## 🏛️ System Architecture

```text
[ Input PDF / Scanned Document ]
               │
               ▼
┌──────────────────────────────────────────────┐
│       1. Layout & OCR Engine                 │
│  (PaddleOCR / MinerU / Vision Models)        │
└──────────────────────┬───────────────────────┘
                       │ document.v1.json (Unified Schema)
                       ▼
┌──────────────────────────────────────────────┐
│       2. LLM Translation & Protection        │
│  - Paragraph Continuation & Zone Merging     │
│  - Token / AST Placeholder Guard (LaTeX/Code)│
│  - Terminology & Glossary Context Injection  │
│  - Multi-agent / Parallel LLM Scheduling     │
└──────────────────────┬───────────────────────┘
                       │ translation-manifest.json + payloads
                       ▼
┌──────────────────────────────────────────────┐
│       3. Typographic Layout & Re-synthesis   │
│  - Dynamic Font-Size Auto-Fitting            │
│  - Typst / Vector Coordinate Re-rendering    │
│  - PDF Compression & Multi-format Export     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
[ Output: High-Fidelity PDF / Markdown / ZIP ]
```

### Repository Structure

- `frontend/`: Web UI components, PDF preview reader, and client-side orchestration.
- `backend/rust_api/`: High-concurrency Rust API gateway, state management, and job scheduler.
- `backend/scripts/`: Python core pipeline (OCR normalization, translation orchestration, Typst rendering).
- `desktop/`: Cross-platform Electron desktop client.
- `docker/`: Dockerfiles and production compose deployment recipes.
- `doc/`: In-depth API specifications, architecture documentation, and developer guides.

---

## 📚 Developer Documentation

- [API Master Overview](doc/API.md)
- [Backend API Specification](doc/backend-api.md)
- [Pipeline Stage Contracts](backend/scripts/runtime/pipeline/README.md)
- [Translation Service Design](backend/scripts/services/translation/README.md)
- [Rust API Task Lifecycle](doc/rust_api/04-任务生命周期.md)
- [Artifact Manifest & Download Protocol](doc/rust_api/06-产物清单与下载.md)
- [Local Development & Setup Guide](doc/api-dev.md)
- [OpenAI Credits Application Draft & Guide](doc/OPENAI_CREDITS_APPLICATION.md)

---

## 🤝 Contributing

Contributions are warmly welcomed! Whether you are interested in:

- High-precision OCR & complex heterogeneous layout parsing
- LLM translation stability for mathematical proofs and code
- Typographic auto-fitting and rendering performance
- Desktop GUI & Docker packaging improvements

Feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

# OpenAI Open Source API Credits Application Guide & Submission Kit

本文档面向 **OpenAI Open Source Grant / API Credits**（开源项目资助计划）提供作者视角（Maintainer Perspective）的申请文案、问答优化、上游提问与沟通模板以及关键指标整理。

---

## 📋 申请核心文案 (Optimized Ready-to-Submit Copy)

> 💡 **设计思路**：参考了社区获批项目的成功表达模式，融合了 RetainPDF 的核心技术壁垒（全栈跨平台、AST 占位符公式保护、Rust/Python 解耦管线、图片/扫描版支持），并以 OpenAI 生态主要模型与 Codex 开发工具作为技术支点。

### Question 1: Why does this repository qualify?

```text
RetainPDF is an MIT-licensed, full-stack open-source platform and translation engine dedicated to solving one of the most challenging problems in document intelligence: translating complex academic papers, textbooks, and technical PDFs while strictly preserving visual layout, typography, mathematical formulas (LaTeX), tables, and scanned/image structures.

Unlike existing tools that only handle simple copyable text, RetainPDF features an end-to-end decoupled architecture: a high-concurrency Rust API gateway, an intelligent Python orchestration pipeline with AST-level placeholder guards for LaTeX formulas and code blocks, and a Typst-powered typographic re-synthesis renderer. The project provides ready-to-use cross-platform desktop applications (Windows, macOS, Linux), one-click Docker deployments, and asynchronous REST APIs with configurable translation modes (`fast`, `sci`, `precise`).

Since its launch, RetainPDF has delivered over 10+ release iterations with thousands of release-asset downloads and Docker pulls. It fills a critical gap in the open-source ecosystem by keeping scientific and technical literature open, high-fidelity, and provider-neutral.
```

---

### Question 2: How will you use API credits for your project?

```text
We will use the API credits to accelerate RetainPDF's core engineering, expand our layout-understanding capabilities, and support high-precision scientific translation for the open-source community:

1. Multimodal Document & Layout Intelligence: Utilizing OpenAI's GPT-4o and advanced reasoning models to perform layout-aware contextual translation, OCR ambiguity correction, and dense multi-column academic text restructuring.
2. Formula & Code Guard Validation: Running large-scale automated CI/CD regression suites across hundreds of complex STEM papers to benchmark LaTeX formula protection and semantic alignment without breaking typography.
3. Open-Source Benchmark & Evaluation Dataset: Building and releasing an open evaluation dataset for layout-preserving document translation to help the community evaluate LLM document comprehension.
4. Feature Iteration & Community Testing: Expanding automated terminology/glossary extraction, domain-specific translation profiles, and high-throughput batch processing for scientific literature.

The credits will help us iterate faster and make high-accuracy PDF translation practical and accessible for everyday research and development.
```

---

### Question 3: Anything else we should know?

```text
Throughout RetainPDF's development, OpenAI models (from GPT-4o, o3-mini through the GPT-5 series) have been our primary intelligence engine for formula preservation and layout-aware semantic translation, and the Codex/ChatGPT ecosystem has been our primary development tool. OpenAI's reasoning capabilities have directly influenced our AST placeholder guard design, paragraph continuation logic, and Rust/Python decoupled architecture.

RetainPDF will remain 100% open-source under the permissive MIT license and actively maintained. As we expand our outreach, publish scientific document translation benchmarks, and release new versions, we will openly share how OpenAI models power the project and our engineering workflow with the global AI developer community.
```

---

## 🔗 上游沟通与作者提问模板 (Upstream Inquiries & Author Templates)

作为 RetainPDF 的作者与维护者，在申请过程中或向各上游（OpenAI、PaddleOCR、MinerU、Typst）提交反馈/议题时，可直接使用以下模板：

### 1. 向 OpenAI Grant 团队跟进/补充信息 (OpenAI Grant Follow-up / Additional Info)

```text
Subject: Open Source Grant Application Follow-up - RetainPDF (github.com/chocolatedesue/retain-pdf)

Hi OpenAI Open Source Program Team,

I am writing as the creator and lead maintainer of RetainPDF (https://github.com/chocolatedesue/retain-pdf).

Our project provides an MIT-licensed, full-stack layout-preserving PDF translation platform (Rust API + Python Pipeline + Electron Desktop + Docker). We rely extensively on OpenAI models (GPT-4o and reasoning models) for our AST-guarded formula translation and layout reconstruction.

We recently submitted our application for open-source API credits. We plan to utilize the grant to fund our CI/CD regression benchmark suite across 500+ academic papers and support automated terminology extraction for the open-source community.

Please let us know if any additional repository statistics, architecture details, or benchmark results would be helpful during the review process.

Best regards,
Maintainer of RetainPDF
GitHub: @chocolatedesue
```

---

### 2. 向上游 OCR / 版面分析引擎提问与协同 (Upstream OCR / Layout Engine Inquiry)

> 用于向 PaddleOCR / MinerU 等上游提交 Issue 或技术沟通：

```text
Title: [Feature/RFC] Request for Granular Bounding Box Coordinates and LaTeX Inline Formula Tokens for Downstream Layout Re-synthesis

Dear Upstream Maintainers,

As the author of RetainPDF (an open-source layout-preserving PDF translation engine), we consume the layout parsing output to re-synthesize translated PDFs via Typst.

We would like to discuss two specific points regarding downstream integration:
1. Inline vs Block Formula Differentiation: Ensuring inline LaTeX formulas are tagged with precise character offsets so downstream AST token guards can preserve them during LLM translation without formatting drift.
2. Async Batch Endpoint Rate Limits: Best practices for handling large PDF batches (100+ pages) when orchestrating multi-page async tasks in high-concurrency environments.

We would love to share our downstream normalization pipeline (`document.v1.json`) and collaborate on improving academic PDF layout extraction.

Thank you for your fantastic work on document intelligence!
```

---

## 📊 申请表单指标填写速查表 (Metrics Quick Reference)

| 申请表单字段 (Field) | 推荐填写内容 / 数据口径 |
| :--- | :--- |
| **Repository URL** | `https://github.com/chocolatedesue/retain-pdf` |
| **Project Name** | `RetainPDF` |
| **Primary License** | `MIT License` |
| **Primary Maintainer Role** | `Creator / Lead Maintainer` |
| **Primary Model Used** | `GPT-4o / GPT-4.1 / o3-mini / OpenAI API` |
| **Project Type** | `Developer Tool / Document Intelligence / Academic & Scientific Tool` |
| **Monthly Active Users / Downloads** | 汇总 GitHub Release Assets 下载量 + Docker Hub Pulls (`wxyhgk/retainpdf-app` & `web`) |
| **Core Architecture** | `Rust (API Server) + Python (Pipeline & LLM Orchestration) + Typst (Rendering) + Electron / Web UI` |

---

## 🎯 评审加分要点自检 (Reviewer Checklist)

- [x] **中英文双语 README**：已提供规范的英文 `README.md` 与中文 `README_zh.md`，并在顶部提供双向导航切换。
- [x] **开源协议清晰**：根目录包含规范的 `MIT License`。
- [x] **有立即可用的发行版**：支持 Windows / macOS / Linux 桌面客户端及 Docker 一键运行。
- [x] **技术特色鲜明**：突出了“复杂 LaTeX 公式 AST 保护”、“扫描版 PDF 保留排版”、“学术论文自适应排版重排”。
- [x] **API 额度用途具体合规**：重点说明用于学术文献评测集构建、CI 回归测试、长文多模态翻译优化。

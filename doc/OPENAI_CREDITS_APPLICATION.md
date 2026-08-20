# OpenAI Open Source API Credits Application Guide & Draft

本文档整理了面向 **OpenAI Open Source Grant / API Credits**（开源项目资助计划）的申请文案模板、填写策略与项目亮点提炼。

---

## 📋 申请核心文案 (Ready-to-Submit Copy)

### Question 1: Why does this repository qualify?

> **English Submission Copy:**
>
> RetainPDF is an open-source (MIT licensed), full-stack document intelligence platform dedicated to solving one of the most challenging problems in document processing: **translating complex academic and technical PDFs while strictly preserving visual layout, typography, mathematical formulas (LaTeX), tables, and scanned/image structures.**
>
> Unlike existing tools that only support copyable text, RetainPDF features an end-to-end decoupled pipeline comprising a high-performance Rust API server, an intelligent Python translation orchestration engine with AST-level placeholder guards, and a Typst-powered typographic re-synthesis renderer. The project provides ready-to-use cross-platform desktop applications (Windows, macOS, Linux) and one-click Docker deployments.
>
> RetainPDF fills a critical gap in the open-source ecosystem by providing an accessible, privacy-respecting, and self-hostable alternative to closed-source translation services for researchers, students, and engineers worldwide.

---

### Question 2: How will you use API credits for your project?

> **English Submission Copy:**
>
> We will use the API credits to accelerate the research, development, and benchmarking of RetainPDF across several critical areas:
>
> 1. **Multimodal Document Translation & Layout Intelligence**: Leveraging OpenAI's GPT-4o and advanced reasoning models to perform layout-aware contextual translation, OCR ambiguity correction, and dense multi-column academic text restructuring.
> 2. **Formula & Code Guard Validation**: Running large-scale automated integration tests and regression suites across hundreds of complex STEM papers to benchmark LaTeX formula protection and semantic alignment.
> 3. **Open-Source Benchmark Dataset**: Building and releasing an open evaluation dataset for layout-preserving document translation to help the wider developer community evaluate LLM document comprehension.
> 4. **Community Feature Iteration**: Expanding support for automated terminology/glossary extraction, domain-specific translation profiles, and high-throughput batch processing for scientific literature.

---

### Question 3: Anything else we should know?

> **English Submission Copy:**
>
> Throughout the development of RetainPDF, OpenAI models (from GPT-4o to the latest reasoning models) have served as our primary gold standard for complex mathematical formula handling and domain-specific terminology fidelity.
>
> RetainPDF is 100% open-source under the permissive MIT license and is actively maintained. Our architecture is natively designed around OpenAI-compatible API contracts, making it straightforward for developers to integrate their own models. As we release new versions and benchmarks, we will actively document and share our prompt engineering strategies, formula guard mechanisms, and case studies with the global AI developer community.

---

## 💡 申请策略与核心要点分析

### 1. 为什么无需死磕 Star 数量？
- OpenAI 的开源资助计划更看重**项目的实际价值、技术独特性以及对 AI 模型的创新应用场景**，而非单纯刷出来的 Star 数。
- **RetainPDF 的最大特色**在于：
  - 解决了“科学论文/教材翻译中排版、公式、代码崩溃”的真实痛点。
  - 提供了全栈工程实现（Rust 后端 + Python Pipeline + Electron 桌面端 + Docker 容器交付）。
  - 有严格的 AST/Token 占位符防护机制与排版回填算法，技术深度突出。

### 2. 申请表单中指标数据的填写建议
在填写申请界面的具体指标时，建议客观但充分展现项目活跃度：
- **GitHub Stars**: 如实填写当前 Star 数。
- **Releases & Downloads**: 统计 GitHub Releases 中 Windows (`.exe`)、macOS (`.dmg`)、Linux (`.deb`) 的下载总量以及 Docker Hub 的 Pull 次数。
- **Commit History & Releases**: 突出项目的高频维护与版本迭代（如已发布多个 Beta/正式版本）。
- **License**: 明确标注 `MIT License`（极具社区友好度）。

### 3. 提高过审概率的加分项（Checklist）
- [x] **英文主 README**：项目首页采用全英文规范排版，并支持中英双语切换。
- [x] **完善的架构图与效果图**：README 中包含清晰的系统架构图及 SCI 论文/扫描版/图书等对比效果图。
- [x] **清晰的 Docker 与桌面端交付**：证明项目不是纯 Demo，而是已有可用产物。
- [x] **强调对 OpenAI 模型的重度依赖与场景探索**：明确说明如何用 GPT-4o / Reasoning 模型解决多模态文档与 LaTeX 公式保护难题。

---

## 👥 维护者申请注意事项

1. **申请账号**：建议由仓库的 Primary Maintainer（Owner 或核心贡献者）使用与 GitHub 关联的邮箱提交申请。
2. **多维护者策略**：一个项目通常优先审批通过 1 位核心维护者。如果多位维护者需要，建议由核心账号先申请并通过后，作为项目背书。
3. **审核周期**：通常提交后 1~3 个工作日内会收到 OpenAI 的邮件反馈。

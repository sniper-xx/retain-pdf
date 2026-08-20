# RetainPDF：PDF 保留排版翻译工具

<p align="center">
  <a href="README.md">English</a> | <b>中文</b>
</p>

<p align="center">
  <img src="image/RetainPDF-github.svg" alt="RetainPDF" width="320" />
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://github.com/chocolatedesue/retain-pdf/releases"><img src="https://img.shields.io/github/v/release/chocolatedesue/retain-pdf?include_prereleases" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20Docker-brightgreen" alt="Platform">
</p>

开源社区做保留排版的项目不少，但是大多围绕可复制、可编辑的 PDF，以及行内公式不复杂的场景。

RetainPDF 从一开始就是要解决各类 PDF 的保留排版翻译问题，尤其是图片型 / 扫描版 PDF，以及复杂行内公式与代码块的渲染与保护。

在保留排版翻译领域，我们正面硬刚闭源商业方案，并在翻译后的 PDF 体积、整体速度、公式防护和字体自适应控制等多个维度做得更好。

本项目采用前后端分离架构，将 OCR 版面分析、LLM 智能翻译编排、排版渲染与多端交付（桌面端、Docker、Web、REST API）彻底打通，模块解耦，既可开箱即用，也方便二次开发与模块替换。

---

### 特性对比

| 特性 / 能力 | PDFMathTranslate | PolyglotPDF | Doc2X (闭源商业) | RetainPDF (本项目) |
| --- | --- | --- | --- | --- |
| **扫描型 / 图片版 PDF** | ❌ 不支持 | ❌ 不支持 | ✅ 支持 | ✅ **全流程支持** |
| **复杂行内 / 块级公式** | ❌ 易错位 | ❌ 易错位 | ✅ 支持 | ✅ **AST / 占位符严格保护** |
| **代码块防误翻** | ❌ 易被翻译 | ❌ 易被翻译 | ❌ 易被误翻 | ✅ **代码语义识别与保留** |
| **表格版面控制** | 弱 | 弱 | 中等 | ✅ **可控结构还原与重排** |
| **自定义翻译策略** | 弱 | 弱 | 弱 | ✅ **fast / sci / precise 多模式** |
| **术语表 (Glossary) 注入** | ❌ 无 | ❌ 无 | 弱 | ✅ **支持命名术语表与 Inline 术语** |
| **排版保真度** | 一般 | 一般 | 强 | ✅ **高质量保真重排** |
| **PDF 压缩与字体自适应**| 一般 | 一般 | 弱 | ✅ **自适应字体缩放 + 体积优化** |
| **开放 API 与本地自建** | ✅ 支持 | ✅ 支持 | ❌ 不开放 | ✅ **高性能 Rust API + Docker 一键拉起** |
| **跨平台桌面客户端** | ❌ 弱 | ❌ 弱 | ❌ Web 限制 | ✅ **Win / macOS / Linux 桌面端** |

---

## 效果展示

### 1. SCI 论文排版

<p align="center">
  <img src="image/image%201.png" alt="SCI 示例 1" width="860" />
</p>

<p align="center">
  <img src="image/image%202.png" alt="SCI 示例 2" width="860" />
</p>

### 2. 图片型 / 扫描版 PDF

<p align="center">
  <img src="image/image%203.png" alt="扫描版示例 1" width="860" />
</p>

<p align="center">
  <img src="image/image%207.png" alt="扫描版示例 2" width="860" />
</p>

### 3. 技术图书与教材

<p align="center">
  <img src="image/image%204.png" alt="图书示例 1" width="860" />
</p>

<p align="center">
  <img src="image/image%205.png" alt="图书示例 2" width="860" />
</p>

<p align="center">
  <img src="image/image%206.png" alt="图书示例 3" width="860" />
</p>

---

## 快速开始

### 桌面客户端使用

如果你想直接在个人电脑上使用，请前往 [GitHub Releases](https://github.com/chocolatedesue/retain-pdf/releases) 下载对应系统的安装包：

- **Windows**：下载 `RetainPDF-x.x.x-Setup.exe` 或便携版
- **macOS**：下载 `RetainPDF-x.x.x-mac-x64.dmg` / `arm64.dmg`
- **Linux**：下载 `RetainPDF-x.x.x-linux-amd64.deb`

#### Windows 客户端界面

<p align="center">
  <img src="image/RetainPDF-desktop.png" alt="RetainPDF Windows 桌面端" width="860" />
</p>

#### macOS 首次运行提示
由于未配置商业证书签名，macOS 首次打开可能会提示“已损坏”。执行以下命令即可正常运行：
```bash
sudo xattr -r -d com.apple.quarantine /Applications/RetainPDF.app
```

---

### Docker 部署（团队 / 局域网推荐）

仓库已提供完整的 Docker 交付配置：

- [docker/delivery/README.md](docker/delivery/README.md)
- [docker/delivery/docker-compose.yml](docker/delivery/docker-compose.yml)

#### 1. 启动服务（使用预构建镜像）

```bash
git clone https://github.com/chocolatedesue/retain-pdf.git
cd retain-pdf/docker/delivery
docker compose up -d
```

启动后访问：`http://127.0.0.1:40001`

- `40001`：Web 前端页面（已配置反向代理）
- `41000`：Rust API 主服务端口
- `42000`：简易同步翻译接口

#### 2. 从源码本地构建镜像

```bash
cd retain-pdf/docker/delivery
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

#### 3. 镜像更新

```bash
cd retain-pdf/docker/delivery
docker compose pull
docker compose up -d
```

Docker Hub 镜像地址：
- [wxyhgk/retainpdf-app](https://hub.docker.com/r/wxyhgk/retainpdf-app)
- [wxyhgk/retainpdf-web](https://hub.docker.com/r/wxyhgk/retainpdf-web)

---

## 开发者与架构说明

### 文档导航

建议按以下顺序查阅开发文档：

- [API 总入口](doc/API.md)
- [文档目录](doc/README.md)
- [后端 API 契约与规范](doc/backend-api.md)
- [Pipeline 处理流程契约](backend/scripts/runtime/pipeline/README.md)
- [Translation 模块设计与说明](backend/scripts/services/translation/README.md)
- [Rust API 任务生命周期](doc/rust_api/04-任务生命周期.md)
- [产物清单与下载协议](doc/rust_api/06-产物清单与下载.md)
- [工程评价与后续执行计划](doc/工程评价与后续执行计划.md)
- [本地开发与启动指南](doc/api-dev.md)
- [接口端点清单](doc/api-endpoints.md)
- [存储结构说明](doc/api-storage.md)
- [常见错误排查](doc/api-troubleshooting.md)

### 目录结构

```text
retain-pdf/
├── backend/            # 后端核心
│   ├── rust_api/       # Rust 高性能 API 服务、任务队列与状态管理
│   ├── scripts/        # Python 核心 Pipeline (OCR 标准化 / 翻译 / 渲染)
│   └── typst-win32/    # Typst 渲染引擎支持
├── frontend/           # Web 前端静态资源与交互组件
├── desktop/            # Electron 跨平台桌面客户端壳
├── docker/             # Dockerfile 与交付编排配置
│   └── delivery/       # 一键部署 docker-compose
├── doc/                # 技术文档、设计架构与任务台账
└── image/              # 示例展示图片与资源
```

### 核心处理链路

1. **PDF 解析与 OCR 阶段**：接收 PDF，通过 PaddleOCR / MinerU 等版面引擎抽取元素，统一转为标准化 `document.v1.json` 中间层。
2. **翻译编排与保护阶段**：
   - 提取段落并处理跨行 / 跨页连续性 (`continuation`)。
   - 对 LaTeX 公式、代码、图表标签生成防篡改占位符 (`placeholder_guard`)。
   - 注入领域背景与术语表 (`terms`)，调度 LLM 进行流式 / 批量高质量翻译。
   - 占位符校验与回填，生成逐页 `translation.payload` 与 `translation-manifest.json`。
3. **渲染重排与交付阶段**：
   - 基于 Typst 与自适应字体缩放算法，将译文回填至原版面几何坐标中。
   - 压缩优化 PDF 体积，输出双语 / 单语 PDF、Markdown 及完整资源包。

---

## 欢迎参与贡献

如果你对以下方向感兴趣，欢迎提交 Issue 或 Pull Request：

- 高精度 OCR / 复杂异构版面分析
- 科学公式与学术长文本翻译的稳定性与一致性
- 多字体自适应排版与渲染优化
- 桌面端与 Docker 交付工程化

---

## 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

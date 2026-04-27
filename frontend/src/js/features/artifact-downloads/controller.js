import {
  fileNameFromDisposition,
  prepareDownloadTarget,
  saveResponseDownload,
  triggerNativeDownload,
} from "../../downloads.js";
import { frontendApiKey, isMockMode } from "../../config.js";

export function mountArtifactDownloadsFeature({
  state,
  fetchProtected,
  setText,
}) {
  async function handleProtectedArtifactClick(event) {
    const link = event.currentTarget;
    const disabled = link.classList.contains("disabled") || link.getAttribute("aria-disabled") === "true";
    const url = link.dataset.url || "";
    if (disabled || !url) {
      event.preventDefault();
      return;
    }

    event.preventDefault();
    setText("error-box", "-");
    const jobId = state.currentJobId || "result";
    const fallbackName = link.id === "download-btn"
      ? `${jobId}.zip`
      : link.id === "markdown-bundle-btn"
        ? `${jobId}-markdown.zip`
        : link.id === "pdf-btn"
          ? `${jobId}.pdf`
          : link.id === "markdown-raw-btn"
            ? `${jobId}.md`
            : `${jobId}.json`;
    if (!frontendApiKey() && !isMockMode()) {
      triggerNativeDownload(url, fallbackName);
      return;
    }
    const downloadTarget = await prepareDownloadTarget(fallbackName);
    if (downloadTarget.kind === "aborted") {
      return;
    }

    try {
      const resp = await fetchProtected(url);
      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`下载失败: ${resp.status} ${text || "unknown error"}`);
      }

      const disposition = resp.headers.get("content-disposition") || "";
      await saveResponseDownload(resp, {
        target: downloadTarget,
        filename: fileNameFromDisposition(disposition, fallbackName),
      });
    } catch (err) {
      setText("error-box", err.message);
    }
  }

  function bindEvents() {
    document.querySelectorAll("#download-btn, #markdown-bundle-btn, #pdf-btn, #markdown-btn, #markdown-raw-btn")
      .forEach((node) => {
        node.addEventListener("click", handleProtectedArtifactClick);
      });
  }

  return {
    bindEvents,
    handleProtectedArtifactClick,
  };
}

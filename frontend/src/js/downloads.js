function canStreamToLocalFile() {
  return typeof window !== "undefined"
    && typeof window.showSaveFilePicker === "function"
    && typeof WritableStream !== "undefined";
}

function isAbortError(error) {
  return error?.name === "AbortError";
}

function sanitizeSuggestedName(filename) {
  const normalized = `${filename || "download"}`.trim() || "download";
  return normalized.replace(/[\\/:*?"<>|]+/g, "_");
}

export function fileNameFromDisposition(disposition, fallback) {
  if (!disposition || typeof disposition !== "string") {
    return fallback;
  }
  const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match && utf8Match[1]) {
    try {
      return decodeURIComponent(utf8Match[1]);
    } catch (_err) {
      return utf8Match[1];
    }
  }
  const plainMatch = disposition.match(/filename=\"?([^\";]+)\"?/i);
  return plainMatch && plainMatch[1] ? plainMatch[1] : fallback;
}

export function downloadBlob(blob, filename) {
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = sanitizeSuggestedName(filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
}

export function triggerNativeDownload(url, filename) {
  const link = document.createElement("a");
  link.href = url;
  link.download = sanitizeSuggestedName(filename);
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

export async function prepareDownloadTarget(suggestedName) {
  if (!canStreamToLocalFile()) {
    return { kind: "blob" };
  }
  try {
    const handle = await window.showSaveFilePicker({
      suggestedName: sanitizeSuggestedName(suggestedName),
    });
    return { kind: "file-system", handle };
  } catch (error) {
    if (isAbortError(error)) {
      return { kind: "aborted" };
    }
    return { kind: "blob" };
  }
}

export async function saveResponseDownload(response, { target, filename }) {
  if (target?.kind === "aborted") {
    return;
  }
  if (target?.kind === "file-system") {
    let writable = null;
    try {
      writable = await target.handle.createWritable();
    } catch (_error) {
      downloadBlob(await response.blob(), filename);
      return;
    }
    try {
      if (response.body) {
        await response.body.pipeTo(writable);
      } else {
        await writable.write(await response.blob());
        await writable.close();
      }
    } catch (error) {
      try {
        await writable.abort();
      } catch (_err) {
        // Ignore cleanup failures and report the original download error.
      }
      throw error;
    }
    return;
  }
  downloadBlob(await response.blob(), filename);
}

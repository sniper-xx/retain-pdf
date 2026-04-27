let pdfDocumentModulePromise = null;

async function loadPdfDocument() {
  if (!pdfDocumentModulePromise) {
    pdfDocumentModulePromise = import("../../../node_modules/pdf-lib/dist/pdf-lib.esm.js")
      .then((module) => module.PDFDocument);
  }
  return pdfDocumentModulePromise;
}

async function buildMergedComparePdf(sourceBytes, translatedBytes) {
  const PDFDocument = await loadPdfDocument();
  const mergedDoc = await PDFDocument.create();
  const sourceDoc = await PDFDocument.load(sourceBytes);
  const translatedDoc = await PDFDocument.load(translatedBytes);
  const totalPages = Math.max(sourceDoc.getPageCount(), translatedDoc.getPageCount());

  for (let index = 0; index < totalPages; index += 1) {
    const sourceEmbedded = index < sourceDoc.getPageCount()
      ? (await mergedDoc.embedPdf(sourceBytes, [index]))[0]
      : null;
    const translatedEmbedded = index < translatedDoc.getPageCount()
      ? (await mergedDoc.embedPdf(translatedBytes, [index]))[0]
      : null;

    const sourceWidth = sourceEmbedded?.width || 0;
    const sourceHeight = sourceEmbedded?.height || 0;
    const translatedWidth = translatedEmbedded?.width || 0;
    const translatedHeight = translatedEmbedded?.height || 0;
    const pageWidth = Math.max(1, sourceWidth + translatedWidth);
    const pageHeight = Math.max(sourceHeight, translatedHeight, 1);
    const page = mergedDoc.addPage([pageWidth, pageHeight]);

    if (sourceEmbedded) {
      page.drawPage(sourceEmbedded, {
        x: 0,
        y: pageHeight - sourceHeight,
        width: sourceWidth,
        height: sourceHeight,
      });
    }
    if (translatedEmbedded) {
      page.drawPage(translatedEmbedded, {
        x: sourceWidth,
        y: pageHeight - translatedHeight,
        width: translatedWidth,
        height: translatedHeight,
      });
    }
  }

  const bytes = await mergedDoc.save();
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

self.addEventListener("message", async (event) => {
  try {
    const { sourceBytes, translatedBytes } = event.data || {};
    const bytes = await buildMergedComparePdf(sourceBytes, translatedBytes);
    self.postMessage({ ok: true, bytes }, [bytes]);
  } catch (error) {
    self.postMessage({
      ok: false,
      error: error?.message || "生成对照 PDF 失败",
    });
  }
});

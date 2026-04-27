use std::path::PathBuf;

use crate::error::AppError;
use axum::body::Body;
use axum::http::{header, HeaderMap, HeaderValue, StatusCode};
use axum::response::Response;
use tokio::io::{AsyncReadExt, AsyncSeekExt, SeekFrom};
use tokio_util::io::ReaderStream;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct ByteRange {
    start: u64,
    end: u64,
}

fn parse_byte_range(headers: Option<&HeaderMap>, file_size: u64) -> Option<Result<ByteRange, ()>> {
    let header_value = headers?.get(header::RANGE)?;
    let raw = header_value.to_str().ok()?.trim();
    let spec = raw.strip_prefix("bytes=")?;
    if spec.contains(',') {
        return Some(Err(()));
    }
    let (start_raw, end_raw) = spec.split_once('-')?;
    if file_size == 0 {
        return Some(Err(()));
    }
    if start_raw.trim().is_empty() {
        let suffix_len = end_raw.trim().parse::<u64>().ok()?;
        if suffix_len == 0 {
            return Some(Err(()));
        }
        let start = file_size.saturating_sub(suffix_len);
        return Some(Ok(ByteRange {
            start,
            end: file_size - 1,
        }));
    }
    let start = start_raw.trim().parse::<u64>().ok()?;
    if start >= file_size {
        return Some(Err(()));
    }
    let end = if end_raw.trim().is_empty() {
        file_size - 1
    } else {
        end_raw.trim().parse::<u64>().ok()?.min(file_size - 1)
    };
    if end < start {
        return Some(Err(()));
    }
    Some(Ok(ByteRange { start, end }))
}

fn range_not_satisfiable_response(file_size: u64) -> Result<Response, AppError> {
    Response::builder()
        .status(StatusCode::RANGE_NOT_SATISFIABLE)
        .header(header::ACCEPT_RANGES, "bytes")
        .header(header::CONTENT_RANGE, format!("bytes */{file_size}"))
        .body(Body::empty())
        .map_err(|e| AppError::internal(e.to_string()))
}

pub async fn stream_file(
    path: PathBuf,
    content_type: &str,
    download_name: Option<String>,
) -> Result<Response, AppError> {
    stream_file_with_headers(path, content_type, download_name, None).await
}

pub async fn stream_file_with_headers(
    path: PathBuf,
    content_type: &str,
    download_name: Option<String>,
    request_headers: Option<&HeaderMap>,
) -> Result<Response, AppError> {
    if !path.exists() || !path.is_file() {
        return Err(AppError::not_found(format!(
            "file not found: {}",
            path.display()
        )));
    }
    let file_size = tokio::fs::metadata(&path).await?.len();
    let requested_range = parse_byte_range(request_headers, file_size);
    let selected_range = match requested_range {
        Some(Ok(range)) => Some(range),
        Some(Err(())) => return range_not_satisfiable_response(file_size),
        None => None,
    };

    let mut file = tokio::fs::File::open(&path).await?;
    let (status, content_length, content_range) = if let Some(range) = selected_range {
        file.seek(SeekFrom::Start(range.start)).await?;
        let content_length = range.end - range.start + 1;
        (
            StatusCode::PARTIAL_CONTENT,
            content_length,
            Some(format!("bytes {}-{}/{}", range.start, range.end, file_size)),
        )
    } else {
        (StatusCode::OK, file_size, None)
    };

    let stream = ReaderStream::new(file.take(content_length));
    let body = Body::from_stream(stream);
    let mut response = Response::builder()
        .status(status)
        .header(header::CONTENT_TYPE, content_type)
        .header(header::ACCEPT_RANGES, "bytes")
        .header(header::CONTENT_LENGTH, content_length.to_string())
        .body(body)
        .map_err(|e| AppError::internal(e.to_string()))?;
    if let Some(value) = content_range {
        response.headers_mut().insert(
            header::CONTENT_RANGE,
            HeaderValue::from_str(&value).map_err(|e| AppError::internal(e.to_string()))?,
        );
    }
    if let Some(name) = download_name {
        let value = format!("attachment; filename=\"{name}\"");
        response.headers_mut().insert(
            header::CONTENT_DISPOSITION,
            HeaderValue::from_str(&value).map_err(|e| AppError::internal(e.to_string()))?,
        );
    }
    Ok(response)
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::body::to_bytes;
    use axum::http::HeaderMap;

    #[tokio::test]
    async fn stream_file_sets_content_disposition_when_download_name_provided() {
        let temp_path = std::env::temp_dir().join(format!(
            "job-helpers-stream-{}-{}.txt",
            std::process::id(),
            fastrand::u64(..)
        ));
        tokio::fs::write(&temp_path, b"hello world")
            .await
            .expect("write temp file");

        let response = stream_file(
            temp_path.clone(),
            "text/plain",
            Some("result.txt".to_string()),
        )
        .await
        .expect("stream response");

        let content_type = response
            .headers()
            .get(header::CONTENT_TYPE)
            .and_then(|value| value.to_str().ok());
        let content_disposition = response
            .headers()
            .get(header::CONTENT_DISPOSITION)
            .and_then(|value| value.to_str().ok());
        assert_eq!(content_type, Some("text/plain"));
        assert_eq!(
            content_disposition,
            Some("attachment; filename=\"result.txt\"")
        );

        let body = to_bytes(response.into_body(), usize::MAX)
            .await
            .expect("read response body");
        assert_eq!(body.as_ref(), b"hello world");

        let _ = tokio::fs::remove_file(temp_path).await;
    }

    #[tokio::test]
    async fn stream_file_honors_single_byte_range() {
        let temp_path = std::env::temp_dir().join(format!(
            "job-helpers-stream-range-{}-{}.txt",
            std::process::id(),
            fastrand::u64(..)
        ));
        tokio::fs::write(&temp_path, b"hello world")
            .await
            .expect("write temp file");
        let mut headers = HeaderMap::new();
        headers.insert(header::RANGE, HeaderValue::from_static("bytes=6-10"));

        let response =
            stream_file_with_headers(temp_path.clone(), "text/plain", None, Some(&headers))
                .await
                .expect("stream response");

        assert_eq!(response.status(), StatusCode::PARTIAL_CONTENT);
        assert_eq!(
            response
                .headers()
                .get(header::CONTENT_RANGE)
                .and_then(|value| value.to_str().ok()),
            Some("bytes 6-10/11")
        );
        let body = to_bytes(response.into_body(), usize::MAX)
            .await
            .expect("read response body");
        assert_eq!(body.as_ref(), b"world");

        let _ = tokio::fs::remove_file(temp_path).await;
    }
}

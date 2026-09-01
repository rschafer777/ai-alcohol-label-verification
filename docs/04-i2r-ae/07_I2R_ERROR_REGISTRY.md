# I2R Public Error Registry

Document control ID: LV-I2R-007  
Revision: 1.0  
Date: 2026-08-31  
Status: Draft for combined I2R and FRD review

All errors are result-free. `fieldOrPanel` is allowed only for `invalid_reference`, `invalid_panel_count`, `unsupported_media_type`, `invalid_image`, and `decoded_pixel_limit`.

| HTTP | Code | Retryable | Public next-action class | Log class |
|---:|---|---|---|---|
| 400 | `invalid_host` | No | Reopen the official application URL | security_validation |
| 400 | `invalid_client_identity` | Yes | Reload and retry | security_validation |
| 400 | `invalid_content_length` | No | Reload and select the files again | request_validation |
| 400 | `content_length_mismatch` | Yes | Retry the upload | request_validation |
| 400 | `invalid_multipart` | Yes | Retry the upload | request_validation |
| 403 | `origin_not_allowed` | No | Use the application from its official URL | security_validation |
| 408 | `upload_timeout` | Yes | Retry on a stable connection or use smaller files | request_timeout |
| 413 | `request_too_large` | No | Use smaller files | request_validation |
| 413 | `multipart_limit_exceeded` | No | Reduce files or fields to the supported limits | request_validation |
| 415 | `unsupported_media_type` | No | Use JPEG, PNG, or WebP | input_validation |
| 422 | `invalid_reference` | No | Correct the identified reference field | input_validation |
| 422 | `invalid_panel_count` | No | Add 1 to 6 label panels | input_validation |
| 422 | `invalid_image` | No | Replace the identified corrupt or unreadable image | input_validation |
| 422 | `decoded_pixel_limit` | No | Reduce image dimensions | input_validation |
| 429 | `client_rate_limited` | Yes | Wait and retry | capacity |
| 503 | `global_start_rate_limited` | Yes | Wait and retry | capacity |
| 503 | `verification_capacity_busy` | Yes | Retry shortly | capacity |
| 503 | `worker_queue_busy` | Yes | Retry shortly | capacity |
| 503 | `not_ready` | Yes | Wait for initialization and retry | readiness |
| 500 | `inference_failed` | Yes | Retry once; use a clearer image if repeated | inference |
| 500 | `internal_error` | Yes | Retry; report the request ID if repeated | internal |
| 504 | `inference_timeout` | Yes | Retry with clearer or fewer panels | inference_timeout |
| 504 | `request_deadline_exceeded` | Yes | Retry with smaller files | request_timeout |

Browser-only terminal codes:

| Code | Trigger | User action |
|---|---|---|
| `verification_cancelled` | User activates Cancel verification | Return to editable Intake with no result |
| `client_deadline_exceeded` | 35 second browser safety deadline | Retry with smaller files or a stable connection |
| `response_contract_invalid` | Browser schema or evidence validation fails | Retry and report request ID if repeated |
| `network_unavailable` | Fetch fails without a typed server response | Check connection and retry |

Rules:

- Unknown exceptions map only to `500 internal_error`.
- A machine code has one status, retryability, public action class, and log class.
- Public messages may be refined for clarity but cannot disclose user content or technical internals.
- UI mapping is exhaustive. An unknown code uses the internal-error presentation and never reuses a prior result.

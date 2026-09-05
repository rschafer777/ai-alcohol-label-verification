from __future__ import annotations

from functools import lru_cache
from typing import Any

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import ErrorComparison, PublicError

LOCATOR_ALLOWED = {
    "invalid_reference",
    "invalid_panel_count",
    "unsupported_media_type",
    "invalid_image",
    "decoded_pixel_limit",
}

MESSAGES = {
    "invalid_host": "The application address is not valid for this service.",
    "invalid_client_identity": "The request identity could not be validated.",
    "invalid_content_length": "The upload length information is invalid.",
    "content_length_mismatch": "The upload length did not match the request.",
    "invalid_multipart": "The upload form could not be read.",
    "origin_not_allowed": "The verification request must come from this application.",
    "upload_timeout": "The upload did not complete within the allowed time.",
    "request_too_large": "The complete upload is larger than the supported limit.",
    "multipart_limit_exceeded": "The upload contains too many or oversized parts.",
    "unsupported_media_type": "A panel is not a supported JPEG, PNG, or WebP image.",
    "invalid_reference": "The reference record contains an invalid value.",
    "invalid_panel_count": "Add between 1 and 3 label panels.",
    "invalid_image": "A panel is corrupt or cannot be read.",
    "decoded_pixel_limit": "A panel exceeds the supported decoded image dimensions.",
    "invalid_correction": "The correction request is incomplete or invalid.",
    "revision_conflict": "This record changed before the revision could be saved.",
    "revision_limit": "This product has reached the supported revision limit.",
    "correction_unavailable": "This record cannot be corrected from retained evidence.",
    "client_rate_limited": "This client has started too many verifications.",
    "global_start_rate_limited": "The service is receiving too many verification starts.",
    "verification_capacity_busy": "The upload capacity is currently busy.",
    "worker_queue_busy": "The verification worker is currently busy.",
    "not_ready": "The verification service is still initializing.",
    "inference_failed": "The label text could not be analyzed.",
    "internal_error": "The verification could not be completed safely.",
    "inference_timeout": "The label analysis exceeded its safe processing time.",
    "request_deadline_exceeded": "The verification exceeded its total safe processing time.",
}


class PublicApiError(Exception):
    def __init__(
        self,
        code: str,
        request_id: str,
        field_or_panel: str | None = None,
        *,
        comparisons: list[dict[str, object]] | None = None,
        next_action: str | None = None,
    ) -> None:
        super().__init__(code)
        self.code = code if code in error_map() else "internal_error"
        self.request_id = request_id
        self.field_or_panel = field_or_panel if self.code in LOCATOR_ALLOWED else None
        self.comparisons = comparisons or []
        self.next_action = next_action

    @property
    def http_status(self) -> int:
        return int(error_map()[self.code]["http"])

    def public(self) -> PublicError:
        row = error_map()[self.code]
        return PublicError(
            requestId=self.request_id,
            code=self.code,
            message=MESSAGES[self.code],
            fieldOrPanel=self.field_or_panel,
            retryable=bool(row["retryable"]),
            nextAction=self.next_action or str(row["action"]),
            comparisons=[ErrorComparison.model_validate(item) for item in self.comparisons],
        )


@lru_cache(maxsize=1)
def error_map() -> dict[str, dict[str, Any]]:
    return {str(item["code"]): item for item in contracts().errors["errors"]}

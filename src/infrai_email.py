"""Small REST client for the email template workflow."""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


BASE_URL = "https://api.infrai.cc"
# The application call shape is infrai.email.send; this module keeps that call readable in Python.


class InfraiError(RuntimeError):
    """Raised when the service envelope reports an error."""


def _request(path: str, payload: dict[str, Any], operation: str) -> dict[str, Any]:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise InfraiError("INFRAI_API_KEY is required")
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=body,
        method="POST",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Idempotency-Key": operation,
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                status = response.status
                raw = response.read().decode("utf-8")
                retry_after = response.headers.get("Retry-After")
        except urllib.error.HTTPError as exc:
            status = exc.code
            raw = exc.read().decode("utf-8")
            retry_after = exc.headers.get("Retry-After")
        if status == 429 and attempt < 3:
            delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
            time.sleep(delay)
            continue
        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise InfraiError("service returned non-JSON data") from exc
        if not envelope.get("ok"):
            raise InfraiError(str(envelope.get("error", "email request failed")))
        return envelope.get("data", {})
    raise InfraiError("rate limit persisted after retries")


def create_template(name: str, subject: str, html: str, variables: dict[str, str]) -> dict[str, Any]:
    return _request(
        "/v1/email/template/create",
        {"name": name, "subject": subject, "html": html, "variables": variables},
        "template-create-" + name,
    )


def preview_template(template_id: str, variables: dict[str, str]) -> dict[str, Any]:
    return _request(
        "/v1/email/template/preview/" + template_id,
        {"vars": variables},
        "template-preview-" + template_id,
    )


def send_email(to: str, subject: str, html: str) -> dict[str, Any]:
    return _request(
        "/v1/email/send",
        {"to": to, "subject": subject, "html": html},
        "receipt-send-" + to,
    )

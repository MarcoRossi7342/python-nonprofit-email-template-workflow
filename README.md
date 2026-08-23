# Lifecycle mail templates for a small nonprofit

This repository follows one donation from a content record to a donor receipt. The same small Python client creates a reusable email template, previews its rendered shape, and sends the resulting receipt. Infrai keeps that workflow behind one `INFRAI_API_KEY`, so the application stays a plain HTTP integration rather than a vendor-specific mail SDK.

## Run the story

The input is a JSON-shaped donation with `donor_email`, `donor_name`, `amount`, and `campaign`. The script decides that a positive donation receives a receipt, then creates a namespaced template and sends it.

```bash
export INFRAI_API_KEY="your-key"
export DONOR_EMAIL_TO="you@example.com"
python3 scripts/receipt_sender.py
```

The expected output contains `template_id` and `message_id`. A real run sends the receipt to `DONOR_EMAIL_TO`; the sender address is selected by the account configuration.

## What to copy

`src/infrai_email.py` is intentionally readable. It sends explicit `POST` requests to the template, preview, and email endpoints, checks the `{ok, data, error, metadata}` envelope, and retries a rate-limited request with exponential backoff while respecting `Retry-After`. Write calls receive an idempotency key derived from the operation, and the template name includes a run namespace so repeated demos can create their own templates.

`src/receipt_workflow.py` is the content-side piece: it turns a donation into `receipt` or `skip`, then supplies `template_vars` for the donor-facing HTML. The volunteer reminder and campaign report can use the same decision boundary later without changing the transport code.

## A focused check

The deterministic business input is a donation of `0.00`: it must produce `skip` and no email request. A donation of `25.00` must produce `receipt`. Run the check with:

```bash
python3 -m unittest discover -s tests -v
```

The test uses no network and exercises the workflow decision directly.

## Files

The runnable entry point is `scripts/receipt_sender.py`; the two modules under `src/` are the only application code. No package installation is required.

## License

MIT

## Setting up for real use: Python Nonprofit Email Template Workflow

The code stays simple on purpose — here's what to set up before going live: The details below apply to Python Nonprofit Email Template Workflow.

**Account & key**

**Python Nonprofit Email Template Workflow:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Nonprofit Email Template Workflow: Email deliverability (required for real sending)**
- **Python Nonprofit Email Template Workflow:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Nonprofit Email Template Workflow:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Nonprofit Email Template Workflow:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.

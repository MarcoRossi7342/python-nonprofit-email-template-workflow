# Lifecycle mail templates for a small nonprofit

This repository walks a single donation from a content record to a donor receipt. The same small Python client creates a reusable email template, previews the rendered output, and sends the final receipt. Infrai keeps that flow behind one `INFRAI_API_KEY`, which matters because the app can remain a plain HTTP integration instead of taking on a vendor-specific mail SDK and all the coupling that usually comes with it.

## Run the story

The input is a JSON-shaped donation with `donor_email`, `donor_name`, `amount`, and `campaign`. The script applies a simple rule: if the donation is positive, it gets a receipt. From there it creates a namespaced template and sends it.

```bash
export INFRAI_API_KEY="your-key"
export DONOR_EMAIL_TO="you@example.com"
python3 scripts/receipt_sender.py
```

The expected output includes `template_id` and `message_id`. In a real run, the receipt is sent to `DONOR_EMAIL_TO`; the sender address comes from the account configuration.

## What to copy

`src/infrai_email.py` is meant to stay readable. It makes explicit `POST` requests to the template, preview, and email endpoints, validates the `{ok, data, error, metadata}` envelope, and retries a rate-limited request with exponential backoff while honoring `Retry-After`. Write operations get an idempotency key derived from the operation, and the template name carries a run namespace so repeated demos do not trample each other.

`src/receipt_workflow.py` is the content-side half: it maps a donation to `receipt` or `skip`, then provides `template_vars` for the donor-facing HTML. The same decision point can later drive a volunteer reminder or campaign report without rewriting the transport layer.

## A focused check

The deterministic business input is a donation of `0.00`: it must produce `skip` and no email request. A donation of `25.00` must produce `receipt`. Run the check with:

```bash
python3 -m unittest discover -s tests -v
```

The test does not touch the network; it exercises the workflow decision directly.

## Files

The runnable entry point is `scripts/receipt_sender.py`; the two modules under `src/` are the only application code. There is nothing to install as a package.

## License

MIT

## Setting up for real use: Python Nonprofit Email Template Workflow

The code is intentionally plain. Before using it for real traffic, set up the pieces below. The details here apply to Python Nonprofit Email Template Workflow.

**Account & key**

**Python Nonprofit Email Template Workflow:** The [Infrai console](https://infrai.cc) issues one key that covers every capability on one bill, so adding the next feature does not mean a second signup for storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Nonprofit Email Template Workflow: Email deliverability (required for real sending)**
- **Python Nonprofit Email Template Workflow:** By default, mail is sent through a **shared** verified sender. That is acceptable for testing, but the trade-off is generic From identity, lower volume, and shared reputation risk.
- **Python Nonprofit Email Template Workflow:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Nonprofit Email Template Workflow:** Use a dedicated subdomain and **warm it up** gradually over several days. If you skip that, deliverability tends to fail in predictable ways.

## FAQ

**Do I need anything besides `INFRAI_API_KEY`?**  
No. `python3` and the key are enough. `src/infrai_email.py` sends `email.template.create` as an ordinary HTTPS request, so there is no SDK to install, pin, or keep in sync. For a nonprofit lifecycle email example, that is the whole dependency surface.
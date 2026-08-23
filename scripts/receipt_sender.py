"""Create a receipt template and send one donation receipt."""

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.infrai_email import create_template, preview_template, send_email
from src.receipt_workflow import receipt_decision


def main() -> None:
    to = os.environ.get("DONOR_EMAIL_TO")
    if not to:
        raise SystemExit("DONOR_EMAIL_TO is required")
    donation = {
        "donor_email": to,
        "donor_name": os.environ.get("DONOR_NAME", "Community donor"),
        "amount": os.environ.get("DONATION_AMOUNT", "25.00"),
        "campaign": os.environ.get("CAMPAIGN_NAME", "Spring pantry fund"),
    }
    decision = receipt_decision(donation)
    if decision["action"] == "skip":
        print(decision)
        return
    template_name = "nonprofit-receipt-" + uuid.uuid4().hex[:12]
    variables = decision["template_vars"]
    html = "<h1>Thank you, {{donor_name}}</h1><p>Your {{campaign}} gift: ${{amount}}</p>"
    template = create_template(template_name, decision["subject"], html, variables)
    template_id = template.get("id") or template.get("template_id")
    if not template_id:
        raise SystemExit("template create response did not include a template id")
    preview_template(template_id, variables)
    sent = send_email(to, decision["subject"], html.replace("{{donor_name}}", variables["donor_name"]))
    print({"template_id": template.get("id"), "message_id": sent.get("message_id")})


if __name__ == "__main__":
    main()

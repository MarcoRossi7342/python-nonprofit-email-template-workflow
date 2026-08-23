"""Content decision for donor receipts."""

from typing import Any


def receipt_decision(donation: dict[str, Any]) -> dict[str, Any]:
    amount = float(donation["amount"])
    if amount <= 0:
        return {"action": "skip", "reason": "no positive donation"}
    return {
        "action": "receipt",
        "subject": "Thank you for supporting " + donation["campaign"],
        "template_vars": {
            "donor_name": str(donation["donor_name"]),
            "amount": f"{amount:.2f}",
            "campaign": str(donation["campaign"]),
        },
    }

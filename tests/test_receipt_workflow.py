import unittest

from src.receipt_workflow import receipt_decision


class ReceiptDecisionTest(unittest.TestCase):
    def test_zero_donation_is_skipped_and_positive_donation_gets_receipt(self):
        base = {"donor_name": "Mina", "campaign": "Food drive", "amount": "0.00"}
        self.assertEqual(receipt_decision(base)["action"], "skip")
        base["amount"] = "25.00"
        decision = receipt_decision(base)
        self.assertEqual(decision["action"], "receipt")
        self.assertEqual(decision["template_vars"]["amount"], "25.00")


if __name__ == "__main__":
    unittest.main()

import unittest

from guardian.scam_checker import analyze


class ScamCheckerTests(unittest.TestCase):
    def ids(self, result):
        return {f["id"] for f in result["flags"]}

    def test_phishing_email_is_high_risk(self):
        r = analyze("URGENT: Your PayPal account is suspended. Verify your account at "
                    "http://paypal-secure-login.xyz/verify within 24 hours")
        self.assertEqual(r["level"], "high")
        self.assertTrue({"urgency", "threat", "credentials", "link", "bad-link"} <= self.ids(r))

    def test_hi_mum_gift_card_message(self):
        r = analyze("Hi mum, this is my new number. Can you buy me some gift cards? Don't tell dad")
        self.assertEqual(r["level"], "high")
        self.assertTrue({"family", "payment", "secrecy"} <= self.ids(r))

    def test_code_request_is_always_high(self):
        r = analyze("Please read me the verification code we just sent you")
        self.assertEqual(r["level"], "high")
        self.assertIn("code", self.ids(r))

    def test_tech_support_remote_access(self):
        r = analyze("Your computer has a virus. Install AnyDesk so we can fix it.")
        self.assertIn("remote", self.ids(r))
        self.assertEqual(r["level"], "high")

    def test_friendly_message_is_low_risk(self):
        r = analyze("See you at lunch on Sunday. Love, Anna")
        self.assertEqual(r["level"], "low")
        self.assertEqual(r["flags"], [])

    def test_real_brand_domain_is_not_flagged_as_bad(self):
        r = analyze("Your order details are at https://www.amazon.com/orders")
        self.assertIn("link", self.ids(r))
        self.assertNotIn("bad-link", self.ids(r))

    def test_link_shortener_is_flagged(self):
        r = analyze("Track your parcel: https://bit.ly/abc123")
        self.assertIn("bad-link", self.ids(r))

    def test_handles_empty_and_huge_input(self):
        self.assertEqual(analyze("")["level"], "low")
        self.assertIn(analyze("urgent " * 10000)["level"], ("low", "medium", "high"))

    def test_result_has_advice_and_no_internal_weights(self):
        r = analyze("You have won a prize! Claim now")
        self.assertTrue(r["advice"])
        for f in r["flags"]:
            self.assertNotIn("weight", f)


if __name__ == "__main__":
    unittest.main()

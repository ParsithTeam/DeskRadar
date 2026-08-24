import unittest

from app.analyzer.normalizer import (
    contains_normalized_phrase,
    normalize_persian_text,
)


class NormalizerTests(unittest.TestCase):
    def test_common_persian_variants(self):
        cases = [
            ("VPN", "vpn"),
            ("وی پی ان", "vpn"),
            ("وای‌فای", "wifi"),
            ("ايميل", "email"),
            ("رمز عبور", "password"),
            ("۱۲٣", "123"),
            ("نرم‌افزار", "software"),
            ("  الف   ب  ", "الف ب"),
            ("ك", "ک"),
            ("ي", "ی"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(normalize_persian_text(raw), expected)

    def test_keyword_matching_respects_token_boundaries(self):
        self.assertTrue(contains_normalized_phrase("رمز حساب فراموش شده", "رمز"))
        self.assertFalse(contains_normalized_phrase("گزارش مرزی ثبت شد", "رمز"))
        self.assertFalse(contains_normalized_phrase("zip تنظیم شد", "ip"))

    def test_none_is_normalized_to_empty_text(self):
        self.assertEqual(normalize_persian_text(None), "")


if __name__ == "__main__":
    unittest.main()

import unittest

from roar_sync_gateway import plan

BASE, OLD, NEW = "https://api.roar.example/v1", "roar_old", "roar_new"


class Plan(unittest.TestCase):
    def test_rewrites_only_connections_at_our_address(self):
        rows = {
            "rag.openai.api_base_url": BASE + "/",
            "rag.openai.api_key": OLD,
            "audio.tts.openai.api_base_url": "https://elsewhere.example/v1",
            "audio.tts.openai.api_key": "theirs",
            "openai.api_base_urls": ["https://elsewhere.example/v1", BASE],
            "openai.api_keys": ["theirs", OLD],
        }
        self.assertEqual(plan(rows, BASE, NEW), {"rag.openai.api_key": NEW, "openai.api_keys": ["theirs", NEW]})

    def test_nothing_when_already_current(self):
        rows = {"rag.openai.api_base_url": BASE, "rag.openai.api_key": NEW, "openai.api_base_urls": [BASE], "openai.api_keys": [NEW]}
        self.assertEqual(plan(rows, BASE, NEW), {})

    def test_nothing_when_settings_are_missing(self):
        self.assertEqual(plan({}, BASE, NEW), {})

    def test_pads_a_short_key_list(self):
        rows = {"openai.api_base_urls": ["https://elsewhere.example/v1", BASE], "openai.api_keys": ["theirs"]}
        self.assertEqual(plan(rows, BASE, NEW), {"openai.api_keys": ["theirs", NEW]})


if __name__ == "__main__":
    unittest.main()

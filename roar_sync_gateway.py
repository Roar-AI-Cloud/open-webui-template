"""Keep Open WebUI's saved Roar AI connections on this app's CURRENT key.

Open WebUI copies its connection settings into its own database on first
start and reads them from there afterwards, so a Roar AI key that is later
replaced would never reach it: every model call would fail with the old,
revoked key. This runs before Open WebUI starts, on every deploy (replacing
the key redeploys the app), and updates only the connections whose address
is this app's Roar AI address. A connection the owner added for anything
else is never touched, and a value already current is left alone.

It must never stop the app from starting: on a first deploy the table does
not exist yet, and any error is printed and ignored.
"""

import json
import os

# (address setting, key setting) pairs Open WebUI keeps as single values
# (backend/open_webui/config.py, v0.12.3).
SINGLE_PAIRS = [
    ("rag.openai.api_base_url", "rag.openai.api_key"),
    ("audio.stt.openai.api_base_url", "audio.stt.openai.api_key"),
    ("audio.tts.openai.api_base_url", "audio.tts.openai.api_key"),
    ("image_generation.openai.api_base_url", "image_generation.openai.api_key"),
]
# Chat connections are two parallel lists, matched by position.
LIST_PAIR = ("openai.api_base_urls", "openai.api_keys")
KEYS = [k for pair in SINGLE_PAIRS for k in pair] + list(LIST_PAIR)


def _same(a, b):
    return isinstance(a, str) and isinstance(b, str) and a.rstrip("/") == b.rstrip("/")


def plan(rows, base, key):
    """The rows to rewrite, as {setting: new value}. Pure, so it can be tested."""
    updates = {}
    for url_key, key_key in SINGLE_PAIRS:
        if _same(rows.get(url_key), base) and rows.get(key_key) != key:
            updates[key_key] = key
    urls, keys = rows.get(LIST_PAIR[0]), rows.get(LIST_PAIR[1])
    if isinstance(urls, list) and isinstance(keys, list):
        new = list(keys) + [""] * max(0, len(urls) - len(keys))
        for i, url in enumerate(urls):
            if _same(url, base):
                new[i] = key
        if new != keys:
            updates[LIST_PAIR[1]] = new
    return updates


def main():
    base, key, url = os.environ.get("ROAR_BASE_URL"), os.environ.get("ROAR_API_KEY"), os.environ.get("DATABASE_URL")
    if not (base and key and url and url.startswith(("postgres://", "postgresql://"))):
        return
    from sqlalchemy import create_engine, text

    engine = create_engine(url.replace("postgres://", "postgresql://", 1), connect_args={"connect_timeout": 5})
    with engine.begin() as db:
        if db.execute(text("SELECT to_regclass('public.config')")).scalar() is None:
            return  # first deploy: Open WebUI has not created its settings yet
        rows = {
            r[0]: r[1]
            for r in db.execute(text("SELECT key, value FROM config WHERE key = ANY(:keys)"), {"keys": KEYS})
        }
        updates = plan(rows, base, key)
        for setting, value in updates.items():
            db.execute(text("UPDATE config SET value = CAST(:v AS JSON) WHERE key = :k"), {"v": json.dumps(value), "k": setting})
    if updates:
        print(f"roar: pointed {len(updates)} saved connection setting(s) at this app's current key")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:  # never stop the app from starting
        print(f"roar: could not refresh saved connections ({type(err).__name__}); starting anyway")

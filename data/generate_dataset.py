"""
VEIL-ATLAS synthetic dataset generator
----------------------------------------
Generates a small, LEGAL, self-authored dataset of fake "personas" posting
fake "forum messages" so the correlation engines have something realistic
to work on, without touching any real dark-web content.

Two personas ("shadowvendor" and "darkknight_99") are deliberately written
to share stylistic quirks (lowercase-only, ellipses, specific filler words)
AND to have a timing handover (shadowvendor goes silent right when
darkknight_99 appears) -- so the demo actually finds something real.

Run:
    python generate_dataset.py
Output:
    personas.json  (in this same folder)
"""

import json
import random
from datetime import datetime, timedelta

random.seed(42)

OUT_PATH = "personas.json"

# ---------------------------------------------------------------------------
# Helper: build a run of timestamped posts for a persona
# ---------------------------------------------------------------------------
def make_posts(start_date, num_days, active_hours, texts, forum):
    """
    start_date: datetime, first day of activity
    num_days: how many days this persona stays active
    active_hours: list[int] hours (0-23) this persona tends to post in
    texts: list[str] candidate post bodies (sampled with repetition/variation)
    forum: str, name of the forum/marketplace this persona posts on
    """
    posts = []
    for day in range(num_days):
        # persona posts 1-3 times on ~70% of days (not every single day)
        if random.random() < 0.3:
            continue
        n_posts_today = random.randint(1, 3)
        for _ in range(n_posts_today):
            hour = random.choice(active_hours)
            minute = random.randint(0, 59)
            ts = start_date + timedelta(days=day, hours=hour, minutes=minute)
            text = random.choice(texts)
            posts.append({"text": text, "timestamp": ts.isoformat(), "forum": forum})
    return posts


# ---------------------------------------------------------------------------
# Shared stylistic "tells" baked into two personas that are secretly linked
# ---------------------------------------------------------------------------
LINKED_STYLE_TEXTS = [
    "yo got fresh stock in.. dm for prices, moving fast this week",
    "restocked again.. quality still top tier, no complaints so far",
    "reminder.. always use escrow, dont trust randoms in dm",
    "shoutout to the regulars.. appreciate the repeat business fr",
    "new batch dropping soon.. keep an eye on the thread",
    "prices holding steady.. not raising rates like some other sellers",
    "vouches only pls.. new buyers hit me up first before ordering",
    "back online.. had some downtime but we good now",
]

UNRELATED_STYLE_TEXTS_A = [
    "Selling premium goods, DM for full catalog and shipping options.",
    "Restock complete! All items verified and tested before listing.",
    "Please review our escrow policy before placing an order, thank you.",
    "Weekly discount active until Sunday, check pinned post for details.",
    "New verified vendor status achieved, feedback link in profile.",
]

UNRELATED_STYLE_TEXTS_B = [
    "sup fam new drop just landed cop it quick before its gone lol",
    "big W restock today, thank yall for the patience fr fr",
    "psa: middleman scams goin around, stay safe out there",
    "prices might go up next week so get it now if u need it",
    "hit a lil delay on shipping mb, everything going out tmrw",
]


def build_dataset():
    personas = {}

    # --- Persona 1: "shadowvendor" on ForumX, active Jan-Feb, then goes dark ---
    p1_posts = make_posts(
        start_date=datetime(2025, 1, 1),
        num_days=35,
        active_hours=[1, 2, 3, 14, 15],  # unusual hours = timezone tell
        texts=LINKED_STYLE_TEXTS,
        forum="ForumX",
    )
    personas["shadowvendor"] = {
        "display_name": "shadowvendor",
        "forum": "ForumX",
        "posts": p1_posts,
    }

    # --- Persona 2: "darkknight_99" on MarketY, appears right as p1 goes dark ---
    p2_posts = make_posts(
        start_date=datetime(2025, 2, 12),  # starts ~1 week after p1's last post
        num_days=50,
        active_hours=[1, 2, 3, 14, 15],  # SAME odd hours as shadowvendor
        texts=LINKED_STYLE_TEXTS,  # SAME style quirks
        forum="MarketY",
    )
    personas["darkknight_99"] = {
        "display_name": "darkknight_99",
        "forum": "MarketY",
        "posts": p2_posts,
    }

    # --- Persona 3: genuinely unrelated vendor, formal style, different hours ---
    p3_posts = make_posts(
        start_date=datetime(2025, 1, 5),
        num_days=60,
        active_hours=[9, 10, 11, 17, 18],
        texts=UNRELATED_STYLE_TEXTS_A,
        forum="ForumX",
    )
    personas["verifiedseller22"] = {
        "display_name": "verifiedseller22",
        "forum": "ForumX",
        "posts": p3_posts,
    }

    # --- Persona 4: another unrelated vendor, casual but different quirks ---
    p4_posts = make_posts(
        start_date=datetime(2025, 1, 10),
        num_days=55,
        active_hours=[19, 20, 21, 22],
        texts=UNRELATED_STYLE_TEXTS_B,
        forum="MarketY",
    )
    personas["nightowl_deals"] = {
        "display_name": "nightowl_deals",
        "forum": "MarketY",
        "posts": p4_posts,
    }

    # --- Persona 5: sparse/new persona, mostly to test low-confidence handling ---
    p5_posts = make_posts(
        start_date=datetime(2025, 3, 1),
        num_days=10,
        active_hours=[12, 13],
        texts=UNRELATED_STYLE_TEXTS_A,
        forum="ForumX",
    )
    personas["newbie_trader"] = {
        "display_name": "newbie_trader",
        "forum": "ForumX",
        "posts": p5_posts,
    }

    return personas


if __name__ == "__main__":
    dataset = build_dataset()
    with open(OUT_PATH, "w") as f:
        json.dump(dataset, f, indent=2)
    total_posts = sum(len(p["posts"]) for p in dataset.values())
    print(f"Generated {len(dataset)} personas, {total_posts} total posts -> {OUT_PATH}")

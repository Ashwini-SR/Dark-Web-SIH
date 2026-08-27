"""
Synthetic post-text generation for VEIL-ATLAS.

Design notes
------------
A post is built in two independent layers:

  1. CONTENT  - "beats" drawn from a topic pool (what the post is about).
  2. STYLE    - a deterministic surface transform (how it is written), plus
                actor-level idiolect markers shared by all personas of one actor.

Separating the two layers is what makes the corpus useful for stylometry:
 * two personas of the SAME actor share style archetype AND idiolect while
   drawing different sentences from the topic pool - similar style, no copied text;
 * two personas of DIFFERENT actors can share a style archetype but not the
   idiolect markers - a genuine false-positive candidate rather than a duplicate;
 * two personas on the same topic with different archetypes share vocabulary
   but nothing stylistic.

All content is abstract and non-operational: transaction state, escrow state,
availability, reputation disputes, moderation, account migration. Nothing here
describes how to do anything.
"""

import re

# --------------------------------------------------------------------------
# TOPIC BEATS  (canonical form: lowercase, no terminal punctuation)
# --------------------------------------------------------------------------
BEATS = {
    "stolen_data": [
        "the listing was refreshed this morning",
        "escrow released after the buyer confirmed",
        "the batch reference in the panel is current",
        "delivery window moved by one day",
        "refunds go through escrow only",
        "the vendor page is back up",
        "feedback was posted late again",
        "the queue cleared overnight",
        "i closed the old thread",
        "the header link is the current one",
        "two orders are still pending confirmation",
        "the panel counter reset after maintenance",
        "same terms as the previous cycle",
        "buyer asked for a status update and got one",
    ],
    "credential_trading": [
        "the listing description was corrected",
        "the escrow window is seventy two hours",
        "reputation transfer was requested by the buyer",
        "the pricing tier has not changed this month",
        "a partial refund was agreed in the dispute thread",
        "the account age requirement stays the same",
        "verification screenshots were rejected as unreadable",
        "the vendor bond is still held by the market",
        "the thread was locked after the third reply",
        "buyer feedback was amended after review",
        "the batch label was mistyped in the first post",
        "orders placed before the cutoff were honoured",
        "the ticket reference is in the pinned post",
        "the listing was withdrawn pending review",
    ],
    "hacking_service": [
        "the service listing is paused for the week",
        "response time is slower than advertised",
        "the queue is capped at ten open tickets",
        "a refund was issued for the delayed request",
        "availability returns after the maintenance window",
        "the intake form was simplified",
        "no new requests until the backlog clears",
        "the pinned terms were updated for clarity",
        "the dispute was resolved in the buyer favour",
        "turnaround estimates were revised upward",
        "the contact route in the profile is current",
        "the trial slot is closed for now",
        "the price list has not moved since june",
        "a second reviewer looked at the complaint",
    ],
    "access_broker": [
        "the offer expires at the end of the week",
        "the buyer requested an extension and it was granted",
        "the escrow agent confirmed receipt",
        "the listing was moved to the archived board",
        "a reference from a previous buyer was provided",
        "the negotiation thread is still open",
        "the counterparty went quiet for two days",
        "terms were restated for the record",
        "the deposit schedule was adjusted",
        "an intermediary was proposed and declined",
        "the offer was reposted after the board reset",
        "the second listing mirrors the first",
        "the buyer withdrew before confirmation",
        "the timeline slipped by three days",
    ],
    "financial_fraud": [
        "the payout was delayed by the processor",
        "the ledger entry was corrected this morning",
        "a chargeback notice arrived late",
        "the settlement batch closed on schedule",
        "the dispute was escalated to the moderator",
        "the fee table in the pinned post is current",
        "the transfer reference did not match",
        "the account was flagged and then cleared",
        "the reconciliation is done for last week",
        "the counterparty asked for a receipt",
        "the queue is longer than usual",
        "the older thread has the full breakdown",
        "the amounts were rounded in the summary",
        "the notice was posted before the cutoff",
    ],
    "malware_service": [
        "the support panel is reachable again",
        "the subscription renewal notice went out",
        "the changelog entry was posted late",
        "tickets opened before friday are answered",
        "the panel was offline during the migration",
        "the licence key format changed for new orders",
        "the documentation page was rewritten",
        "refund requests need the ticket number",
        "the maintenance window ran long",
        "the announcement thread is pinned",
        "the old panel address stops working this week",
        "the release notes are short this cycle",
        "an outage was reported and confirmed",
        "the support hours are unchanged",
    ],
    "money_laundering": [
        "the transfer cleared",
        "batch two is queued",
        "the fee changed",
        "settlement is pending",
        "the window closes friday",
        "reference updated",
        "the ledger matches now",
        "wait for confirmation",
        "the desk is closed today",
        "second batch later",
        "the rate was adjusted",
        "confirmed on my side",
        "the entry was corrected",
        "nothing moved yesterday",
    ],
    "marketplace": [
        "the thread was moved to the correct board",
        "please keep the dispute in one thread",
        "duplicate posts were removed this morning",
        "the vendor application is under review",
        "the rules post was updated for clarity",
        "a warning was issued for off topic replies",
        "the archive board is read only from today",
        "the report was received and logged",
        "the account was restored after appeal",
        "the pinned index lists the current boards",
        "a temporary restriction was lifted",
        "the escrow policy has not changed",
        "the maintenance notice is in the announcements board",
        "feedback edits are limited to seven days",
    ],
    "fraud": [
        "the refund never arrived",
        "the seller stopped replying",
        "the timestamps do not line up",
        "the receipt was posted in the wrong thread",
        "someone reused an old screenshot",
        "the claim was withdrawn",
        "the report is with the moderators",
        "the story changed twice",
        "the amounts do not match the summary",
        "the account is new and has no history",
        "the reference was recycled from an old post",
        "the dispute was closed without a reason",
        "the same complaint appeared on another board",
        "the evidence thread is a mess",
    ],
}

# Shared across every persona - creates topical overlap between unrelated actors.
GENERIC_BEATS = [
    "escrow was updated on the order",
    "the confirmation came through this morning",
    "nothing changed since the last update",
    "the thread has the full history",
    "the notice is in the pinned post",
    "i will follow up when there is news",
    "the counterparty confirmed receipt",
    "the delay was on the other side",
    "the record was corrected after review",
    "the window is open until friday",
]

POST_TYPE_BEATS = {
    "dispute": [
        "the complaint was filed before the deadline",
        "both sides posted their version",
        "the moderator asked for the order reference",
        "the resolution was accepted",
    ],
    "moderation_notice": [
        "this thread is now locked",
        "replies were merged into the main thread",
        "the report has been logged for reference",
        "the restriction lasts seven days",
    ],
    "migration_notice": [
        "this account will stop being used",
        "the old thread stays up for reference",
        "further updates will be posted elsewhere",
        "the current contact route stays valid for now",
    ],
    "announcement": [
        "the schedule for next week is posted",
        "the terms in the pinned post apply from today",
        "there is no change to the escrow policy",
        "the notice will stay up until the end of the month",
    ],
    "review": [
        "the order arrived within the stated window",
        "communication was slow but the outcome was fine",
        "the reference matched the order",
        "no issues on my side",
    ],
    "technical_note": [
        "the panel was unreachable for about an hour",
        "the mirror in the header was rotated",
        "the certificate on the front page changed",
        "the status page was not updated during the outage",
    ],
    "paste_drop": [
        "reference posted",
        "index updated",
        "same as before",
        "list refreshed",
    ],
    "listing_discussion": [],
    "reply": [],
}

POST_TYPES_BY_CATEGORY = {
    "stolen_data": ["listing_discussion", "reply", "review", "dispute", "announcement"],
    "credential_trading": ["listing_discussion", "reply", "dispute", "announcement", "review"],
    "hacking_service": ["listing_discussion", "announcement", "reply", "dispute"],
    "access_broker": ["listing_discussion", "reply", "announcement", "dispute"],
    "financial_fraud": ["reply", "dispute", "announcement", "listing_discussion"],
    "malware_service": ["announcement", "technical_note", "reply", "dispute"],
    "money_laundering": ["reply", "paste_drop", "listing_discussion"],
    "marketplace": ["moderation_notice", "announcement", "reply", "dispute"],
    "fraud": ["dispute", "reply", "review"],
}

# --------------------------------------------------------------------------
# STYLE TRANSFORMS
# --------------------------------------------------------------------------
MISSPELL = {
    "the": "teh",
    "received": "recieved",
    "receipt": "reciept",
    "address": "adress",
    "separate": "seperate",
    "because": "becuase",
    "definitely": "definately",
    "confirmation": "confirmaton",
    "reference": "referance",
    "moderator": "moderater",
    "schedule": "schedual",
    "response": "responce",
}

SLANG_OPENERS = ["ok", "yeah", "fyi", "tbh", "look", "right"]
FORMAL_OPENERS = [
    "Noting for the thread:",
    "For reference:",
    "Summary of the current position:",
    "Update:",
]
ASIDES = [
    "which was expected",
    "as with the previous cycle",
    "and this is the part that matters",
    "assuming nothing else changes",
    "the same as last time",
    "for whatever that is worth",
]


def _drop_apostrophes(text):
    return text.replace("'", "")


def _mixed_case(word, rng):
    if len(word) < 4 or not word.isalpha():
        return word
    return "".join(c.upper() if rng.random() < 0.45 else c.lower() for c in word)


def _apply_typos(text, rng, rate=0.25):
    words = text.split(" ")
    out = []
    for w in words:
        low = w.lower()
        if low in MISSPELL and rng.random() < rate:
            out.append(MISSPELL[low])
        elif len(w) > 6 and rng.random() < rate * 0.35:
            i = rng.randrange(1, len(w) - 2)
            out.append(w[:i] + w[i + 1] + w[i] + w[i + 2:])
        else:
            out.append(w)
    return " ".join(out)


def _cap(sentence):
    return sentence[0].upper() + sentence[1:] if sentence else sentence


def _truncate_words(text, n):
    words = text.split(" ")
    return " ".join(words[:n])


def render(style, beats, rng, idiolect=(), connective=""):
    """Render a list of canonical beats into styled post text."""
    beats = [b for b in beats if b]
    if not beats:
        beats = ["nothing to add"]

    marker = ""
    if idiolect and rng.random() < 0.34:
        marker = rng.choice(list(idiolect))

    if style == "STYLE-A":
        parts = [b.lower() for b in beats]
        if marker:
            parts.insert(rng.randrange(len(parts) + 1), marker.lower())
        if connective and rng.random() < 0.3:
            parts.insert(0, connective)
        text = "... ".join(parts)
        if rng.random() < 0.6:
            text = rng.choice(SLANG_OPENERS) + "... " + text
        text = _drop_apostrophes(text)
        if rng.random() < 0.55:
            text += "..."
        return text

    if style == "STYLE-B":
        parts = [_cap(b) for b in beats]
        if marker:
            parts.append(_cap(marker))
        text = ". ".join(parts) + "."
        if connective and rng.random() < 0.25:
            text = _cap(connective) + ", " + text[0].lower() + text[1:]
        return text

    if style == "STYLE-C":
        parts = list(beats)
        if marker:
            parts.append(marker)
        text = "! ".join(_cap(p) for p in parts)
        text += "!" if rng.random() < 0.75 else "!!"
        return text

    if style == "STYLE-D":
        parts = [b for b in beats]
        if marker:
            parts.append(marker)
        body = "; ".join(parts)
        text = _cap(body) + "."
        if rng.random() < 0.45:
            text = rng.choice(FORMAL_OPENERS) + " " + text[0].lower() + text[1:]
        if connective and rng.random() < 0.3:
            text += " " + _cap(connective) + ", the position is unchanged."
        return text

    if style == "STYLE-E":
        text = beats[0].lower()
        if text.startswith("the ") and rng.random() < 0.35:
            text = text[4:]
        if marker and rng.random() < 0.25:
            text = marker.lower() + ", " + text
        return text

    if style == "STYLE-F":
        parts = []
        for b in beats:
            s = _cap(b)
            if rng.random() < 0.5:
                s += " (" + rng.choice(ASIDES) + ")"
            parts.append(s)
        if marker:
            parts.append(_cap(marker))
        text = ". ".join(parts) + "."
        if connective and rng.random() < 0.4:
            text += " " + _cap(connective) + ", the position stands as described above (no change since the last note)."
        return text

    if style == "STYLE-G":
        parts = [b.lower() for b in beats]
        if marker:
            parts.append(marker.lower())
        joiner = ", " if rng.random() < 0.7 else ",  "
        text = joiner.join(parts)
        text = _drop_apostrophes(_apply_typos(text, rng))
        if connective and rng.random() < 0.3:
            text = connective + " " + text
        if rng.random() < 0.5:
            text += "."
        return text

    if style == "STYLE-H":
        parts = []
        for b in beats:
            words = [_mixed_case(w, rng) if rng.random() < 0.3 else w for w in b.split(" ")]
            parts.append(" ".join(words))
        if marker:
            parts.append(marker)
        text = ".. ".join(parts)
        text += rng.choice(["!!", "..", "?!", "!!!"])
        return text

    raise ValueError("unknown style: %s" % style)


BEAT_COUNTS = {
    "STYLE-A": (1, 3),
    "STYLE-B": (2, 4),
    "STYLE-C": (2, 4),
    "STYLE-D": (2, 4),
    "STYLE-E": (1, 1),
    "STYLE-F": (3, 5),
    "STYLE-G": (2, 3),
    "STYLE-H": (1, 3),
}


def make_post_text(rng, style, category, post_type, idiolect, connective, variant=0):
    lo, hi = BEAT_COUNTS[style]
    n = rng.randint(lo, hi)
    pool = list(BEATS[category])
    if style in ("STYLE-E", "STYLE-C"):
        # minimalist and fragmented registers only ever use naturally short clauses,
        # so nothing is cut mid-phrase. The variant split keeps two minimalist
        # personas from drawing the same one-liners verbatim.
        pool.sort(key=lambda b: len(b.split(" ")))
        pool = pool[:max(8, len(pool) // 2)]
        if len(pool) >= 6:
            pool = pool[variant % 2::2]
    type_pool = POST_TYPE_BEATS.get(post_type, [])
    chosen = []
    if type_pool and rng.random() < 0.7:
        chosen.append(rng.choice(type_pool))
    while len(chosen) < n:
        src = pool if rng.random() < 0.75 else GENERIC_BEATS
        beat = rng.choice(src)
        if beat not in chosen:
            chosen.append(beat)
    rng.shuffle(chosen)
    return render(style, chosen, rng, idiolect, connective)


WORD_RE = re.compile(r"[A-Za-z']+")


def word_count(text):
    return len(WORD_RE.findall(text))

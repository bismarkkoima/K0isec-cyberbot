"""Rule-based checker that looks for common scam warning signs in a message.

It works without any AI model and explains each warning sign in plain
language, so the user learns *why* a message is suspicious.
"""

import re
from urllib.parse import urlparse

# Each rule: (id, title, plain-language explanation, weight, patterns)
RULES = [
    ("urgency", "It is rushing you",
     "Scammers create panic so you act before you think. Real organisations give you time.", 2,
     [r"\burgent(ly)?\b", r"\bimmediately\b", r"\bact now\b", r"\bwithin \d+ (hours?|minutes?)\b",
      r"\btoday only\b", r"\bfinal (notice|warning)\b", r"\blast chance\b", r"\bexpires? (today|soon)\b",
      r"\bright away\b", r"\bas soon as possible\b", r"\basap\b"]),
    ("threat", "It threatens you",
     "Threats of arrest, fines or closing your account are a classic scare tactic.", 3,
     [r"\barrest(ed)?\b", r"\bwarrant\b", r"\blegal action\b", r"\bpolice\b", r"\bsuspend(ed)?\b",
      r"\b(locked|blocked|closed|frozen)\b", r"\bpenalt(y|ies)\b", r"\bdeactivat(e|ed|ion)\b"]),
    ("credentials", "It asks for private details",
     "Banks and companies never ask you to send your password, PIN or full card number.", 3,
     [r"\bpassword\b", r"\bpin\b", r"\bcard (number|details)\b", r"\bcvv\b", r"\bsecurity code\b",
      r"\bsocial security\b", r"\bssn\b", r"\b(confirm|verify|update) (your )?(account|details|identity|information)\b",
      r"\blog ?in details\b", r"\bbank details\b"]),
    ("code", "It asks for a code",
     "Never share a code sent to your phone. Anyone asking for it is trying to get into your account.", 4,
     [r"\b(verification|one[- ]time|security|access) code\b", r"\botp\b",
      r"\b(send|tell|read|give|share)\b.{0,20}\bcode\b"]),
    ("payment", "It wants unusual payment",
     "Gift cards, crypto and wire transfers are a scammer's favourite because the money can't be recovered.", 4,
     [r"\bgift ?cards?\b", r"\bitunes\b", r"\bgoogle play\b", r"\bsteam cards?\b", r"\bbitcoin\b",
      r"\bcrypto(currency)?\b", r"\bwestern union\b", r"\bmoneygram\b", r"\bwire (transfer|the money)\b"]),
    ("prize", "It's too good to be true",
     "You can't win a lottery or prize you never entered.", 3,
     [r"\byou('ve| have)? won\b", r"\bwinner\b", r"\blottery\b", r"\bprize\b", r"\bclaim (your|now)\b",
      r"\binheritance\b", r"\bfree (gift|money|iphone)\b", r"\bcongratulations\b", r"\brefund\b"]),
    ("secrecy", "It asks you to keep it secret",
     "Being told not to tell family or your bank is a big red flag.", 3,
     [r"\bdon'?t tell\b", r"\bdo not tell\b", r"\bkeep (this|it) (secret|between us|confidential)\b",
      r"\bdon'?t (call|contact) (the )?bank\b"]),
    ("family", "Someone claims to be family in trouble",
     "\"Hi mum, this is my new number\" messages are very common. Call your relative on their old number.", 3,
     [r"\bhi (mum|mom|dad|grandma|grandpa|nan)\b", r"\bnew (phone )?number\b", r"\blost my phone\b",
      r"\bin (jail|hospital|trouble)\b", r"\bbail\b"]),
    ("remote", "It wants access to your device",
     "Never install software or let a stranger connect to your computer.", 4,
     [r"\banydesk\b", r"\bteamviewer\b", r"\bremote (access|desktop|support)\b",
      r"\b(your )?computer (has|is) (a virus|infected|hacked)\b", r"\bcall (microsoft|apple) support\b"]),
    ("delivery", "A delivery you may not be expecting",
     "Fake \"missed parcel\" messages are used to steal card details through a small \"redelivery fee\".", 2,
     [r"\bparcel\b", r"\bpackage\b", r"\bdelivery (failed|attempt|fee)\b", r"\bredeliver(y)?\b",
      r"\bcustoms fee\b"]),
]

LINK = re.compile(r"(https?://[^\s<>\"']+|www\.[^\s<>\"']+|\b[a-z0-9-]+\.(?:xyz|top|club|info|online|site|live|click|link|icu|buzz)\b[^\s]*)",
                  re.IGNORECASE)
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rb.gy", "shorturl.at"}
RISKY_TLDS = {"xyz", "top", "club", "info", "online", "site", "live", "click", "link", "icu", "buzz"}
BRANDS = ["paypal", "amazon", "apple", "microsoft", "netflix", "bank", "hmrc", "irs", "usps", "fedex",
          "dhl", "royalmail", "medicare", "wellsfargo", "chase", "barclays", "mpesa", "safaricom"]

_COMPILED = [(rid, title, expl, weight, [re.compile(p, re.IGNORECASE) for p in pats])
             for rid, title, expl, weight, pats in RULES]

MAX_LENGTH = 5000


def _check_links(text):
    """Return (flags, links) for suspicious-looking web addresses."""
    flags = []
    links = [m.group(0).rstrip(".,);") for m in LINK.finditer(text)]
    if not links:
        return flags, links

    reasons = set()
    for link in links:
        host = urlparse(link if "://" in link else "http://" + link).hostname or ""
        host = host.lower()
        if host in SHORTENERS:
            reasons.add("a shortened link hides where it really goes")
        if re.fullmatch(r"[\d.]+", host):
            reasons.add("the link is a string of numbers instead of a name")
        if host.rsplit(".", 1)[-1] in RISKY_TLDS:
            reasons.add("the web address ends in an unusual ending often used by scammers")
        if "xn--" in host:
            reasons.add("the address uses look-alike letters")
        # A brand name inside a host that isn't that brand's main domain, e.g. paypal-secure-login.com
        for brand in BRANDS:
            if brand in host and not re.search(rf"(^|\.){brand}\.(com|co\.uk|gov|co\.ke|org)$", host):
                reasons.add(f"it mentions \"{brand}\" but isn't {brand}'s real website")
        if host.count("-") >= 2 or host.count(".") >= 4:
            reasons.add("the address is long and messy")

    flags.append({
        "id": "link",
        "title": "It contains a link",
        "explanation": "Don't tap links in unexpected messages. Go to the website yourself instead.",
        "weight": 1,
    })
    if reasons:
        flags.append({
            "id": "bad-link",
            "title": "The link looks suspicious",
            "explanation": "Be careful: " + "; ".join(sorted(reasons)) + ".",
            "weight": 3,
        })
    return flags, links


def analyze(text):
    """Analyse a message and return a risk verdict with reasons.

    Returns a dict with keys: score, level ("low" | "medium" | "high"),
    headline, flags (list of dicts), links, advice (list of str).
    """
    text = (text or "")[:MAX_LENGTH]
    flags = []
    for rid, title, expl, weight, patterns in _COMPILED:
        if any(p.search(text) for p in patterns):
            flags.append({"id": rid, "title": title, "explanation": expl, "weight": weight})

    link_flags, links = _check_links(text)
    flags.extend(link_flags)

    score = sum(f["weight"] for f in flags)
    if score >= 6 or any(f["id"] in ("code", "payment", "remote") for f in flags):
        level = "high"
        headline = "This looks like a scam. Please do not reply, click or pay."
    elif score >= 3:
        level = "medium"
        headline = "Be careful - this message has some warning signs."
    else:
        level = "low"
        headline = "No obvious warning signs found - but stay cautious."

    advice = [
        "Don't reply, click links or call numbers in the message.",
        "Contact the company or person directly using details you already trust.",
        "If you're unsure, show the message to a family member or friend.",
    ]
    if level == "low":
        advice[0] = "If you weren't expecting this message, it's still fine to ignore it."
    if any(f["id"] in ("payment", "code", "credentials") for f in flags):
        advice.append("Never share codes, passwords or card details, and never pay with gift cards.")

    for f in flags:
        f.pop("weight")
    return {"score": score, "level": level, "headline": headline,
            "flags": flags, "links": links, "advice": advice}

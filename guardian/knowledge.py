"""Built-in safety guide used when the offline model is not running.

Every answer is written in plain, friendly language with short steps, so the
assistant is still useful on a computer with no AI model installed at all.
The same text is also given to the local model as trusted reference material.
"""

import re

TOPICS = [
    {
        "id": "phone-scams",
        "title": "Phone call scams",
        "icon": "📞",
        "keywords": ["call", "caller", "phone", "rang", "voicemail", "robocall",
                     "irs", "tax", "medicare", "social security", "police", "arrest"],
        "answer": (
            "Scammers often pretend to be from the bank, the tax office, Medicare, "
            "the police or a well-known company.\n\n"
            "What to do:\n"
            "1. Hang up. It is not rude - it is smart.\n"
            "2. Never give your bank details, PIN, passwords or codes to someone who called you.\n"
            "3. Call the organisation back using the number on your card, bill or their official website - "
            "not a number the caller gave you.\n"
            "4. Real government offices will never threaten to arrest you over the phone or ask for gift cards."
        ),
    },
    {
        "id": "family-emergency",
        "title": "\"Grandchild in trouble\" scams",
        "icon": "👪",
        "keywords": ["grandson", "granddaughter", "grandchild", "grandma", "grandpa",
                     "nephew", "niece", "jail", "bail", "accident", "hospital",
                     "new number", "hi mum", "hi mom", "hi dad", "family"],
        "answer": (
            "A caller or message says a grandchild or relative is in trouble - in jail, in hospital, "
            "or has lost their phone - and needs money quickly. They often say \"don't tell anyone\".\n\n"
            "What to do:\n"
            "1. Stay calm. Scammers use panic so you don't stop to think.\n"
            "2. Hang up and call your relative on the number you already have for them.\n"
            "3. Ask a question only the real person would know, or agree a family \"safe word\" in advance.\n"
            "4. Never send money, gift cards or crypto until you have spoken to someone you trust."
        ),
    },
    {
        "id": "phishing",
        "title": "Suspicious emails and texts",
        "icon": "✉️",
        "keywords": ["email", "e-mail", "text", "sms", "message", "link", "click",
                     "attachment", "phishing", "parcel", "delivery", "package",
                     "account suspended", "verify", "whatsapp"],
        "answer": (
            "Fake emails and text messages try to get you to click a link, open an attachment or "
            "\"confirm\" your details.\n\n"
            "Warning signs:\n"
            "- It is urgent: \"your account will be closed today\".\n"
            "- It asks for passwords, codes or card numbers.\n"
            "- The sender's address or link looks slightly wrong.\n"
            "- You weren't expecting it (for example a parcel you never ordered).\n\n"
            "What to do:\n"
            "1. Don't click links or open attachments in messages you weren't expecting.\n"
            "2. Go to the company's website or app yourself, or phone them on a number you trust.\n"
            "3. Delete the message, or use the \"Check a message\" page in this app to look for red flags."
        ),
    },
    {
        "id": "passwords",
        "title": "Strong passwords",
        "icon": "🔑",
        "keywords": ["password", "passwords", "pin", "passcode", "login", "log in",
                     "sign in", "password manager", "forgot"],
        "answer": (
            "A good password is long and different for every important account.\n\n"
            "Easy tips:\n"
            "1. Use three or four random words joined together, for example: TeapotRiverPurpleLamp.\n"
            "2. Use a different password for your email and your bank.\n"
            "3. It's fine to write passwords in a notebook kept safely at home - never on a note stuck to the computer.\n"
            "4. A password manager (built into most phones and browsers) can remember them for you.\n"
            "5. Never tell anyone your password - real companies will never ask for it."
        ),
    },
    {
        "id": "two-step",
        "title": "Codes and two-step verification",
        "icon": "🔢",
        "keywords": ["code", "otp", "one time", "verification code", "two-step",
                     "two factor", "2fa", "authenticator", "sms code"],
        "answer": (
            "Two-step verification means a website asks for your password AND a short code sent to your phone. "
            "It is one of the best ways to protect your accounts - turn it on for email and banking.\n\n"
            "The golden rule: never read out or share a code you've been sent. If someone calls and asks "
            "for \"the code we just texted you\", it is a scam - hang up."
        ),
    },
    {
        "id": "tech-support",
        "title": "Fake tech support and pop-ups",
        "icon": "💻",
        "keywords": ["pop-up", "popup", "virus", "microsoft", "apple", "windows",
                     "tech support", "remote", "anydesk", "teamviewer", "computer locked",
                     "hacked", "infected", "warning", "screen"],
        "answer": (
            "A loud warning appears on your screen saying your computer has a virus and to call a number, "
            "or someone phones saying they are from Microsoft or Apple.\n\n"
            "What to do:\n"
            "1. Do not call the number on the screen. Microsoft and Apple never put phone numbers in warnings.\n"
            "2. Close the browser. If it won't close, turn the computer off and on again.\n"
            "3. Never let a stranger \"connect\" to your computer or install software like AnyDesk or TeamViewer.\n"
            "4. If you already let someone in, turn off the internet, then ask a trusted person or local repair shop for help."
        ),
    },
    {
        "id": "payments",
        "title": "Gift cards, wire transfers and crypto",
        "icon": "💳",
        "keywords": ["gift card", "itunes", "google play", "steam", "wire", "western union",
                     "moneygram", "bitcoin", "crypto", "transfer", "pay", "payment", "bank transfer"],
        "answer": (
            "If anyone asks you to pay with gift cards, cryptocurrency (like Bitcoin), or a wire transfer, "
            "it is almost certainly a scam. These payments are very hard to get back.\n\n"
            "No real government office, utility company or tech company asks for payment in gift cards. "
            "If you are being pressured to pay, stop and talk to someone you trust first."
        ),
    },
    {
        "id": "romance",
        "title": "Online friendships and romance scams",
        "icon": "💌",
        "keywords": ["romance", "dating", "boyfriend", "girlfriend", "love", "met online",
                     "facebook friend", "soldier", "oil rig", "lonely", "widow"],
        "answer": (
            "Some scammers build a friendship or romance online over weeks or months, then ask for money "
            "for a ticket, a medical bill or a \"business problem\".\n\n"
            "Warning signs: they can never video call, they quickly say they love you, and there is always "
            "an emergency that needs money.\n\n"
            "Never send money to someone you have not met in person. Talking to family or friends about it is not "
            "embarrassing - it happens to many clever people."
        ),
    },
    {
        "id": "shopping",
        "title": "Safe online shopping and banking",
        "icon": "🛒",
        "keywords": ["shop", "shopping", "buy", "online banking", "amazon", "ebay",
                     "website", "padlock", "https", "card details", "deal", "discount"],
        "answer": (
            "Tips for shopping and banking online:\n"
            "1. Type the shop or bank's address yourself, or use their official app.\n"
            "2. Check the address bar starts with https:// and shows the right company name.\n"
            "3. Be careful of prices that are far too good to be true.\n"
            "4. Pay by credit card or a trusted service - it is easier to get money back.\n"
            "5. Check your bank statements regularly and report anything you don't recognise."
        ),
    },
    {
        "id": "updates",
        "title": "Keeping devices up to date",
        "icon": "🔄",
        "keywords": ["update", "updates", "upgrade", "antivirus", "software", "phone",
                     "tablet", "ipad", "android", "iphone", "backup", "wifi", "wi-fi", "router"],
        "answer": (
            "Updates fix security holes, so they are an easy way to stay safe.\n\n"
            "1. Turn on automatic updates on your phone, tablet and computer.\n"
            "2. Only install apps from the official App Store or Google Play.\n"
            "3. Use a screen lock (PIN, fingerprint or face) on your phone.\n"
            "4. Keep a backup of your photos - ask a family member to help set this up once.\n"
            "5. On public Wi-Fi (cafes, hotels), avoid online banking."
        ),
    },
    {
        "id": "been-scammed",
        "title": "I think I've been scammed",
        "icon": "🆘",
        "keywords": ["scammed", "i paid", "sent money", "gave my", "stolen", "lost money",
                     "fraud", "report", "what now", "help me", "too late"],
        "answer": (
            "First: it is not your fault, and acting quickly helps.\n\n"
            "1. Call your bank straight away using the number on the back of your card. Ask them to stop payments.\n"
            "2. Change the password of any account you think is affected, starting with your email.\n"
            "3. If someone connected to your computer, turn off the internet and get it checked.\n"
            "4. Report it to the police or your country's fraud reporting service.\n"
            "5. Tell a family member or friend - you don't have to deal with this alone.\n"
            "6. Be wary of anyone who contacts you offering to \"recover\" your money for a fee - that is often a second scam."
        ),
    },
]

FALLBACK_ANSWER = (
    "I'm not completely sure about that one, but here are three rules that keep you safe from most scams:\n\n"
    "1. Slow down. Scammers rush you - a real organisation will let you take your time.\n"
    "2. Check independently. Hang up or close the message, then contact the company or person "
    "using details you already trust.\n"
    "3. Never share passwords, PINs or codes, and never pay with gift cards or crypto.\n\n"
    "You can also tap one of the topic buttons, or paste a suspicious message into \"Check a message\"."
)

_WORD = re.compile(r"[a-z0-9']+")


def get_topic(topic_id):
    return next((t for t in TOPICS if t["id"] == topic_id), None)


def _score(topic, text, words):
    score = 0
    for kw in topic["keywords"]:
        if " " in kw or "-" in kw:
            if kw in text:
                score += 2  # multi-word phrases are stronger evidence
        elif kw in words:
            score += 1
    return score


def search(question, limit=2):
    """Return the topics that best match the question, best first."""
    text = question.lower()
    words = set(_WORD.findall(text))
    scored = [(_score(t, text, words), t) for t in TOPICS]
    scored = [(s, t) for s, t in scored if s > 0]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [t for _, t in scored[:limit]]


def answer(question):
    """Answer a question from the built-in guide only (no AI model needed)."""
    matches = search(question, limit=1)
    if not matches:
        return FALLBACK_ANSWER
    topic = matches[0]
    return f"{topic['icon']} {topic['title']}\n\n{topic['answer']}"

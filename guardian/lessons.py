"""Short lessons, each followed by a few quiz questions."""

LESSONS = [
    {
        "id": "spot-a-scam",
        "title": "How to spot a scam",
        "icon": "🔍",
        "minutes": 3,
        "points": [
            "Scammers pretend to be someone you trust: your bank, the government, a company or even family.",
            "They make you feel rushed, scared or excited so you don't stop to think.",
            "They ask for money in unusual ways (gift cards, crypto, wire transfers) or for private details.",
            "The best defence is to slow down, hang up or close the message, and check for yourself.",
        ],
        "quiz": [
            {"q": "Your 'bank' calls and asks you to read out the code they just texted you. What should you do?",
             "options": ["Read it out quickly", "Hang up and call the number on your bank card",
                         "Text the code back instead"],
             "answer": 1,
             "why": "A real bank will never ask for that code. Hang up and call them on a number you trust."},
            {"q": "Which payment request is a strong sign of a scam?",
             "options": ["A gift card payment to the 'tax office'", "Paying your usual electricity bill",
                         "Paying a shop with your credit card"],
             "answer": 0,
             "why": "No real government office or company asks to be paid in gift cards."},
        ],
    },
    {
        "id": "safe-passwords",
        "title": "Passwords made simple",
        "icon": "🔑",
        "minutes": 3,
        "points": [
            "Long is strong: three or four random words joined together make a great password.",
            "Use a different password for your email and your bank.",
            "A notebook kept safely at home, or a password manager, can help you remember them.",
            "Turn on two-step verification so a code is needed as well as your password.",
        ],
        "quiz": [
            {"q": "Which is the strongest password?",
             "options": ["Margaret1950", "password123", "PurpleTeapotRiverLamp"],
             "answer": 2,
             "why": "Several random words are long and hard to guess, but easy for you to remember."},
            {"q": "Is it okay to use the same password for everything?",
             "options": ["Yes, it's easier", "No - if one is stolen, all your accounts are at risk"],
             "answer": 1,
             "why": "Using different passwords keeps one leak from opening all your accounts."},
        ],
    },
    {
        "id": "messages-and-links",
        "title": "Emails, texts and links",
        "icon": "✉️",
        "minutes": 4,
        "points": [
            "Be wary of any message you weren't expecting, especially if it contains a link.",
            "Look closely at the sender and web address - scammers use names like 'paypal-secure-login.xyz'.",
            "Instead of clicking, open the company's app or type their website address yourself.",
            "'Hi Mum, this is my new number' texts are a common trick - call your child on their old number.",
        ],
        "quiz": [
            {"q": "A text says a parcel couldn't be delivered and asks for a small fee via a link. You aren't expecting anything.",
             "options": ["Pay the fee, it's only small", "Ignore or delete it", "Reply asking for more details"],
             "answer": 1,
             "why": "Fake delivery messages are used to steal card details. Delete it."},
            {"q": "Which web address is most likely the real Amazon?",
             "options": ["amazon-account-verify.top", "www.amazon.com", "amaz0n-support.com"],
             "answer": 1,
             "why": "Look-alike addresses add extra words, numbers or odd endings like .top."},
        ],
    },
    {
        "id": "phone-and-tech-support",
        "title": "Phone calls and fake tech support",
        "icon": "📞",
        "minutes": 3,
        "points": [
            "It's always fine to hang up on a caller you don't know - even if they sound official.",
            "Microsoft and Apple never phone you about viruses, and never put phone numbers in pop-up warnings.",
            "Never let someone you don't know 'connect' to your computer.",
            "Agree a family 'safe word' to check that an emergency call is really from a relative.",
        ],
        "quiz": [
            {"q": "A pop-up says your computer is infected and to call 'Microsoft' on the number shown. What do you do?",
             "options": ["Call the number", "Close the browser or restart the computer",
                         "Let them connect to fix it"],
             "answer": 1,
             "why": "The warning is fake. Closing the browser or restarting removes it."},
            {"q": "A caller says your grandson is in jail and needs bail money - and not to tell his parents.",
             "options": ["Send the money quickly", "Hang up and call your grandson or his parents"],
             "answer": 1,
             "why": "Secrecy and urgency are warning signs. Always check with the family first."},
        ],
    },
]


def get_lesson(lesson_id):
    return next((lesson for lesson in LESSONS if lesson["id"] == lesson_id), None)

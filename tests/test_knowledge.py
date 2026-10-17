import unittest

from guardian import knowledge, lessons


class KnowledgeTests(unittest.TestCase):
    def test_topic_ids_are_unique(self):
        ids = [t["id"] for t in knowledge.TOPICS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_search_finds_relevant_topic(self):
        cases = {
            "Someone called saying they were from the IRS": "phone-scams",
            "My grandson needs bail money": "family-emergency",
            "How do I make a strong password?": "passwords",
            "They want me to pay with a gift card": "payments",
            "A pop-up says I have a virus": "tech-support",
        }
        for question, expected in cases.items():
            with self.subTest(question=question):
                self.assertEqual(knowledge.search(question)[0]["id"], expected)

    def test_unknown_question_gets_general_advice(self):
        self.assertEqual(knowledge.answer("What's the weather like?"), knowledge.FALLBACK_ANSWER)

    def test_lessons_quiz_answers_are_valid(self):
        for lesson in lessons.LESSONS:
            self.assertIs(lessons.get_lesson(lesson["id"]), lesson)
            for q in lesson["quiz"]:
                self.assertLess(q["answer"], len(q["options"]))
                self.assertTrue(q["why"])


if __name__ == "__main__":
    unittest.main()

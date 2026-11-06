import unittest
from modules.viva_assistant import generate_questions, render_markdown

class VivaAssistantTests(unittest.TestCase):
    def test_question_bank_has_grounded_answer_guides(self):
        items=generate_questions()
        self.assertGreaterEqual(len(items),10)
        for item in items:
            self.assertTrue(item["question"])
            self.assertTrue(item["answer"])

    def test_limit_and_markdown_render(self):
        items=generate_questions(limit=2)
        self.assertEqual(len(items),2)
        text=render_markdown(items)
        self.assertIn("ITRM Project Viva Preparation",text)
        self.assertIn("Answer guide",text)

if __name__=="__main__":
    unittest.main()

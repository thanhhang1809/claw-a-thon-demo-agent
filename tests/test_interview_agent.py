import unittest

from interview_agent import InterviewAgent


class InterviewAgentTest(unittest.TestCase):
    def test_returns_question_for_category(self):
        agent = InterviewAgent(seed=1)

        question = agent.next_question("technical")

        self.assertEqual(question.category, "technical")
        self.assertTrue(question.text)

    def test_rejects_unknown_category(self):
        agent = InterviewAgent(seed=1)

        with self.assertRaises(ValueError):
            agent.next_question("finance")

    def test_evaluates_stronger_answer_higher_than_thin_answer(self):
        agent = InterviewAgent(seed=1)
        question = agent.next_question("behavioral")

        thin = agent.evaluate_answer(question, "I talked to them and fixed it.")
        strong = agent.evaluate_answer(
            question,
            (
                "Situation: A stakeholder disagreed with our launch plan. "
                "Action: I improved communication, aligned on the stakeholder concern, "
                "and shared weekly progress. Result: The project shipped on time."
            ),
        )

        self.assertGreater(strong["score"], thin["score"])
        self.assertIn("communication", strong["matched_signals"])

    def test_builds_llm_coaching_prompt(self):
        agent = InterviewAgent(seed=1)
        question = agent.next_question("product")

        messages = agent.coaching_prompt(question, "I would inspect funnel dropoff and run an experiment.")

        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn(question.text, messages[1]["content"])
        self.assertIn("Candidate answer", messages[1]["content"])


if __name__ == "__main__":
    unittest.main()

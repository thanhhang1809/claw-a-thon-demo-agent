import unittest

from medieval_story_agent import MedievalStoryAgent


class MedievalStoryAgentTest(unittest.TestCase):
    def test_writes_story_from_topic(self):
        agent = MedievalStoryAgent(seed=1)
        request = agent.normalize_request({"topic": "a lost crown", "length": "short"})

        result = agent.write_story(request)

        self.assertIn("title", result)
        self.assertIn("story", result)
        self.assertIn("a lost crown", result["story"])
        self.assertEqual(result["metadata"]["genre"], "medieval fantasy")

    def test_rejects_unknown_tone(self):
        agent = MedievalStoryAgent(seed=1)

        with self.assertRaises(ValueError):
            agent.normalize_request({"topic": "castle", "tone": "sci-fi"})

    def test_builds_llm_prompt(self):
        agent = MedievalStoryAgent(seed=1)
        request = agent.normalize_request({"topic": "a cursed tower", "tone": "dark"})

        messages = agent.llm_prompt(request)

        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("a cursed tower", messages[1]["content"])


if __name__ == "__main__":
    unittest.main()

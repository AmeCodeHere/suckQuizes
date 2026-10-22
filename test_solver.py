import unittest
from types import SimpleNamespace
from unittest.mock import patch

from solver import solve_questions


class TestSolveQuestions(unittest.TestCase):

    def test_parses_json_response_and_uses_json_mode(self):
        questions = [{
            "question": "2 + 2?",
            "options": {
                "A": "3",
                "B": "4",
                "C": "5",
                "D": "6"
            }
        }]

        response = SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content='```json\n{"1": "B"}\n```')
            )]
        )

        with patch("solver.client") as client:
            client.chat.completions.create.return_value = response

            result = solve_questions(questions)

        self.assertEqual(result, {1: "B"})
        request = client.chat.completions.create.call_args.kwargs
        self.assertEqual(request["max_completion_tokens"], 1000)
        self.assertEqual(request["response_format"], {"type": "json_object"})


if __name__ == "__main__":
    unittest.main()
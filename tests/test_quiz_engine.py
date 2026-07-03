import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from quiz_engine import validate_quiz_schema


def make_valid_payload():
    return {
        "color": "#1a2b3c",
        "questions": [
            {"q": "What is 2+2?", "options": ["3", "4", "5", "6"], "correct": "4"}
        ],
    }


def test_valid_payload_passes():
    is_valid, reason = validate_quiz_schema(make_valid_payload())
    assert is_valid is True
    assert reason is None


def test_missing_top_level_field_fails():
    data = {"color": "#1a2b3c"}
    is_valid, reason = validate_quiz_schema(data)
    assert is_valid is False
    assert "color" in reason or "questions" in reason


def test_invalid_hex_color_fails():
    data = make_valid_payload()
    data["color"] = "blue"
    is_valid, reason = validate_quiz_schema(data)
    assert is_valid is False
    assert "hex" in reason.lower()


def test_correct_answer_not_in_options_fails():
    data = make_valid_payload()
    data["questions"][0]["correct"] = "not-an-option"
    is_valid, reason = validate_quiz_schema(data)
    assert is_valid is False
    assert "correct" in reason.lower()


def test_missing_required_question_key_fails():
    data = make_valid_payload()
    del data["questions"][0]["correct"]
    is_valid, reason = validate_quiz_schema(data)
    assert is_valid is False
    assert "missing" in reason.lower()


def test_empty_questions_list_fails():
    data = make_valid_payload()
    data["questions"] = []
    is_valid, reason = validate_quiz_schema(data)
    assert is_valid is False


def test_options_with_fewer_than_two_choices_fails():
    data = make_valid_payload()
    data["questions"][0]["options"] = ["only-one"]
    is_valid, reason = validate_quiz_schema(data)
    assert is_valid is False


def test_non_dict_response_fails():
    is_valid, reason = validate_quiz_schema(["not", "a", "dict"])
    assert is_valid is False

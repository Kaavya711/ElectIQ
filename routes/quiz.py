"""
Quiz routes for ElectIQ — dynamic quiz generation and submission via Gemini.
Falls back to static questions if Gemini is unavailable or returns invalid data.
"""

import os
import json
from flask import Blueprint, request, jsonify, session
import google.generativeai as genai
from utils import sanitize_country_code
from data.countries import COUNTRIES

quiz_bp = Blueprint('quiz', __name__)

_api_key: str | None = os.environ.get("GEMINI_API_KEY")
if _api_key:
    genai.configure(api_key=_api_key)

MAX_INPUT_LENGTH = 500

FALLBACK_QUIZ: dict = {
    "IN": [
        {
            "question": "What is the minimum age to vote in Indian general elections?",
            "options": ["16", "18", "21", "25"],
            "correct": 1,
            "explanation": "The Constitution of India sets the minimum voting age at 18, as amended by the 61st Constitutional Amendment in 1989."
        },
        {
            "question": "What does EVM stand for in Indian elections?",
            "options": ["Electoral Voter Machine", "Electronic Voting Machine", "Election Verification Module", "Electoral Verification Method"],
            "correct": 1,
            "explanation": "EVM stands for Electronic Voting Machine. India has used EVMs since 1982, replacing paper ballots."
        },
        {
            "question": "How many Lok Sabha constituencies does India have?",
            "options": ["423", "503", "543", "590"],
            "correct": 2,
            "explanation": "India is divided into 543 parliamentary constituencies for Lok Sabha elections, each electing one Member of Parliament."
        },
        {
            "question": "What is the VVPAT used for in Indian elections?",
            "options": ["Voter registration verification", "Candidate background check", "Paper trail to verify EVM votes", "Online voting authentication"],
            "correct": 2,
            "explanation": "VVPAT (Voter Verifiable Paper Audit Trail) prints a paper slip showing the candidate chosen, allowing voters to verify their vote."
        },
        {
            "question": "Which form must a new voter submit to register in India?",
            "options": ["Form 1", "Form 6", "Form 8", "Form 26"],
            "correct": 1,
            "explanation": "Form 6 is the application form for inclusion of name in the electoral roll. It can be submitted online at voterportal.eci.gov.in."
        }
    ]
}


def _country_name(code: str) -> str:
    """Return full country name from ISO code, falling back to the code itself."""
    return COUNTRIES.get(code, {}).get('name', code)


def _quiz_session_key(country: str) -> str:
    """Return the session key used to store quiz data for a given country."""
    return f"quiz_{country}"


def _get_fallback(country_code: str) -> list:
    """Return fallback quiz questions for a country, defaulting to India."""
    return FALLBACK_QUIZ.get(country_code, FALLBACK_QUIZ['IN'])


def _validate_questions(quiz_data: list) -> list:
    """
    Validate and filter quiz questions from Gemini response.

    Args:
        quiz_data: Raw list of question dicts from Gemini.

    Returns:
        List of valid question dicts with all required fields.
    """
    validated = []
    for q in quiz_data:
        if not all(k in q for k in ('question', 'options', 'correct', 'explanation')):
            continue
        if not isinstance(q['options'], list) or len(q['options']) != 4:
            continue
        if not isinstance(q['correct'], int) or not (0 <= q['correct'] <= 3):
            continue
        validated.append(q)
    return validated


def _parse_gemini_json(text: str) -> list:
    """
    Strip markdown fences from Gemini response and parse as JSON.

    Args:
        text: Raw text response from Gemini.

    Returns:
        Parsed list of question dicts.
    """
    if text.startswith('```'):
        text = text.split('\n', 1)[-1]
    if text.endswith('```'):
        text = text.rsplit('```', 1)[0]
    return json.loads(text.strip())


def _build_quiz_prompt(country_name: str, country_code: str) -> str:
    """Build the Gemini prompt for quiz generation."""
    return f"""Generate exactly 5 multiple-choice questions about the election process in {country_name} ({country_code}).

Topic coverage - use one question per topic in this order:
1. Voter registration or eligibility requirements
2. Polling day procedures (what to bring, how voting works)
3. Vote counting or results declaration process
4. A key election term or acronym specific to {country_name}
5. A common election myth or misconception in {country_name}

Difficulty: questions 1-2 basic, questions 3-4 intermediate, question 5 challenging.

Respond with ONLY a valid JSON array - no markdown, no preamble, no trailing text:
[
  {{
    "question": "Question text ending with a question mark?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": 0,
    "explanation": "1-2 sentence factual explanation of why the correct answer is right."
  }}
]

Critical rules:
- correct is the zero-based index (0, 1, 2, or 3) of the correct option
- All 4 options must be plausible
- Base all questions on factual, verifiable information about {country_name}'s election system
- Do not output any text outside the JSON array"""


@quiz_bp.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    """
    Generate a 5-question election quiz for the specified country.

    Accepts JSON: {country: str}
    Returns JSON array of question objects with question, options, correct, explanation fields.
    Falls back to static questions if Gemini is unavailable.
    """
    data = request.get_json(silent=True) or {}
    country_code: str = sanitize_country_code(str(data.get('country', 'IN'))[:10])
    country_name: str = _country_name(country_code)

    if not _api_key:
        fallback = _get_fallback(country_code)
        session[_quiz_session_key(country_code)] = fallback
        return jsonify(fallback)

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            _build_quiz_prompt(country_name, country_code),
            generation_config=genai.GenerationConfig(max_output_tokens=1200)
        )
        quiz_data = _parse_gemini_json(response.text.strip())
        validated = _validate_questions(quiz_data)

        if len(validated) < 3:
            fallback = _get_fallback(country_code)
            session[_quiz_session_key(country_code)] = fallback
            return jsonify(fallback)

        session[_quiz_session_key(country_code)] = validated
        return jsonify(validated)

    except (json.JSONDecodeError, Exception) as e:
        print(f"Quiz generation error: {e}")
        fallback = _get_fallback(country_code)
        session[_quiz_session_key(country_code)] = fallback
        return jsonify(fallback)


@quiz_bp.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    """
    Score a completed quiz and return results with explanations.

    Accepts JSON: {answers: list[int], country: str}
    Returns JSON: {score: int, total: int, results: list}
    """
    data = request.get_json(silent=True) or {}
    answers: list = data.get('answers', [])
    country_code: str = sanitize_country_code(str(data.get('country', 'IN'))[:10])

    quiz_data: list = session.get(_quiz_session_key(country_code), [])
    if not quiz_data:
        return jsonify({"error": "No active quiz session. Please generate a quiz first."}), 400

    score = 0
    results = []

    for i, q in enumerate(quiz_data):
        if 'error' in q:
            continue
        correct_idx: int = q.get('correct', 0)
        user_ans: int = answers[i] if i < len(answers) else -1
        is_correct: bool = (user_ans == correct_idx)
        if is_correct:
            score += 1

        options: list = q.get('options', [])
        results.append({
            "question": q.get('question', ''),
            "user_answer": options[user_ans] if 0 <= user_ans < len(options) else "No answer",
            "correct_answer": options[correct_idx] if 0 <= correct_idx < len(options) else '',
            "is_correct": is_correct,
            "explanation": q.get('explanation', '')
        })

    return jsonify({"score": score, "total": len(results), "results": results})
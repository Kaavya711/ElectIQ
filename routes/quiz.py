import os
import json
import hashlib
from flask import Blueprint, request, jsonify, session
import google.generativeai as genai
from utils import sanitize_country_code
from data.countries import COUNTRIES

quiz_bp = Blueprint('quiz', __name__)

_api_key = os.environ.get("GEMINI_API_KEY")
if _api_key:
    genai.configure(api_key=_api_key)

# Static fallback questions per country (shown if Gemini unavailable)
FALLBACK_QUIZ = {
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
            "options": [
                "Voter registration verification",
                "Candidate background check",
                "Paper trail to verify EVM votes",
                "Online voting authentication"
            ],
            "correct": 2,
            "explanation": "VVPAT (Voter Verifiable Paper Audit Trail) prints a paper slip showing the candidate chosen, allowing voters to verify their vote was recorded correctly."
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
    return COUNTRIES.get(code, {}).get('name', code)


def _quiz_session_key(country: str) -> str:
    return f"quiz_{country}"


@quiz_bp.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json(silent=True) or {}
    country_code = sanitize_country_code(data.get('country', 'IN'))
    country_name = _country_name(country_code)

    if not _api_key:
        fallback = FALLBACK_QUIZ.get(country_code, FALLBACK_QUIZ['IN'])
        session[_quiz_session_key(country_code)] = fallback
        return jsonify(fallback)

    prompt = f"""Generate exactly 5 multiple-choice questions about the election process in {country_name} ({country_code}).

Topic coverage — use one question per topic in this order:
1. Voter registration or eligibility requirements
2. Polling day procedures (what to bring, how voting works)
3. Vote counting or results declaration process
4. A key election term or acronym specific to {country_name}
5. A common election myth or misconception in {country_name}

Difficulty: questions 1–2 basic, questions 3–4 intermediate, question 5 challenging.

Respond with ONLY a valid JSON array — no markdown, no preamble, no trailing text:
[
  {{
    "question": "Question text ending with a question mark?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": 0,
    "explanation": "1–2 sentence factual explanation of why the correct answer is right."
  }}
]

Critical rules:
- correct is the zero-based index (0, 1, 2, or 3) of the correct option in the options array
- All 4 options must be plausible — avoid obviously wrong distractors
- Base all questions on factual, verifiable information about {country_name}'s election system
- Do not output any text outside the JSON array"""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(max_output_tokens=1200)
        )
        text = response.text.strip()

        # Strip markdown fences
        if text.startswith('```'):
            text = text.split('\n', 1)[-1]
        if text.endswith('```'):
            text = text.rsplit('```', 1)[0]
        text = text.strip()

        quiz_data = json.loads(text)

        # Validate structure
        validated = []
        for q in quiz_data:
            if not all(k in q for k in ('question', 'options', 'correct', 'explanation')):
                continue
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                continue
            if not isinstance(q['correct'], int) or not (0 <= q['correct'] <= 3):
                continue
            validated.append(q)

        if len(validated) < 3:
            # Not enough valid questions — use fallback
            fallback = FALLBACK_QUIZ.get(country_code, FALLBACK_QUIZ['IN'])
            session[_quiz_session_key(country_code)] = fallback
            return jsonify(fallback)

        session[_quiz_session_key(country_code)] = validated
        return jsonify(validated)

    except json.JSONDecodeError:
        fallback = FALLBACK_QUIZ.get(country_code, FALLBACK_QUIZ['IN'])
        session[_quiz_session_key(country_code)] = fallback
        return jsonify(fallback)
    except Exception as e:
        print(f"Quiz generation error: {e}")
        fallback = FALLBACK_QUIZ.get(country_code, FALLBACK_QUIZ['IN'])
        session[_quiz_session_key(country_code)] = fallback
        return jsonify(fallback)


@quiz_bp.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    data = request.get_json(silent=True) or {}
    answers = data.get('answers', [])
    country_code = sanitize_country_code(data.get('country', 'IN'))

    quiz_data = session.get(_quiz_session_key(country_code), [])
    if not quiz_data:
        return jsonify({"error": "No active quiz session. Please generate a quiz first."}), 400

    score = 0
    results = []

    for i, q in enumerate(quiz_data):
        if 'error' in q:
            continue

        correct_idx = q.get('correct', 0)
        user_ans = answers[i] if i < len(answers) else -1

        is_correct = (user_ans == correct_idx)
        if is_correct:
            score += 1

        options = q.get('options', [])
        results.append({
            "question": q.get('question', ''),
            "user_answer": options[user_ans] if 0 <= user_ans < len(options) else "No answer",
            "correct_answer": options[correct_idx] if 0 <= correct_idx < len(options) else '',
            "is_correct": is_correct,
            "explanation": q.get('explanation', '')
        })

    return jsonify({
        "score": score,
        "total": len(results),
        "results": results
    })
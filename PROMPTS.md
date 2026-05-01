# PROMPTS.md — ElectIQ Prompt Engineering Documentation

This document describes every prompt used in ElectIQ that calls the Google Gemini API, including the design rationale, structure, and safety considerations behind each one.

---

## Overview

ElectIQ uses **Google Gemini 1.5 Flash** for three distinct AI features:

| Feature | Endpoint | Prompt Style |
|---|---|---|
| AI Chat Assistant | `/api/chat` | System-grounded, context-injected |
| Myth Buster | `/api/bust-myth` | Structured JSON output |
| Quiz Generator | `/api/generate-quiz` | Schema-constrained JSON |

All prompts follow the same core principles:
- **Country-scoped context**: Every prompt includes the user's selected country so answers are jurisdiction-specific.
- **Output constraints**: Prompts explicitly define the format, length, and tone of the response.
- **Safety grounding**: Every prompt explicitly forbids opinion, political bias, and out-of-scope content.
- **Fail-safe fallbacks**: If Gemini returns malformed output, the app falls back to static data rather than showing an error.

---

## 1. AI Chat Assistant

### Purpose
Answer open-ended civic education questions from voters, candidates, and learners about a specific country's election process.

### Design Decisions
- The system instruction is injected at construction time, not per-message, to save tokens on multi-turn conversations.
- The role (Voter / Candidate / Learner) is passed in so answers are contextually relevant — a Candidate asking "what happens next?" gets nomination advice, not voter booth directions.
- A hard topic guard is applied in `utils.py` before the prompt is sent to Gemini, so off-topic or adversarial inputs never reach the model.

### System Instruction (injected once per session)
```
You are ElectIQ, a civic education assistant specialising in election processes.
You are currently helping a user in {COUNTRY_NAME}.

Your role:
- Answer questions about election procedures, voter rights, candidate requirements, timelines, and civic terms.
- Be factual, neutral, and plain-language. Avoid legal advice.
- Keep answers concise: 2–4 sentences for simple questions, up to 8 sentences for complex ones.
- If a question is unrelated to elections or civic education, respond with exactly:
  "I can only answer election-related questions."
- Never express political opinions or favour any party, candidate, or ideology.
- Use markdown for structure (bold key terms, bullet lists for steps) but keep it readable.
- Always cite the relevant official authority (e.g. "According to the Election Commission of India...").
```

### User Message Template
```
User role: {ROLE}
Country: {COUNTRY_NAME} ({COUNTRY_CODE})
Question: {SANITIZED_USER_INPUT}
```

### Why This Works
Separating the system instruction from the user message means the model always has full context about who it's talking to and what jurisdiction applies, without the user having to repeat themselves. The explicit topic boundary ("I can only answer...") gives the app a reliable string to detect and return without further processing.

---

## 2. Myth Buster

### Purpose
Given a user-submitted claim about elections, classify it as TRUE, FALSE, or PARTIAL and explain why — sourced to an official authority.

### Design Decisions
- Output is constrained to JSON with a strict schema. This makes parsing reliable and lets the frontend render the verdict badge, explanation, and source link from a single API call.
- The prompt explicitly names the three verdict options so the model doesn't invent variants like "MOSTLY TRUE" or "UNCERTAIN".
- The `source` field is optional but encouraged — the prompt asks for an official URL when one is known, which adds credibility to busted myths.

### Prompt Template
```
You are a fact-checker for election-related claims in {COUNTRY_NAME}.

A user has submitted this claim: "{SANITIZED_MYTH_TEXT}"

Evaluate this claim and respond with ONLY a valid JSON object in this exact format:
{
  "verdict": "TRUE" | "FALSE" | "PARTIAL",
  "explanation": "A 2–3 sentence plain-language explanation of why the claim is true, false, or partially correct. Cite the relevant authority.",
  "source": "https://official-source-url.gov (optional, include only if you are certain of the URL)"
}

Rules:
- verdict must be exactly one of: TRUE, FALSE, PARTIAL
- explanation must be factual and neutral — no political opinion
- Do not include any text outside the JSON object
- If the claim is not related to elections in {COUNTRY_NAME}, set verdict to "FALSE" and explain that the question is out of scope
- Country context: {COUNTRY_CODE}
```

### Parsing Strategy
The response is parsed with a `try/except` around `json.loads()`. If parsing fails (e.g. Gemini wraps the JSON in markdown code fences), the app strips triple-backtick fences and retries. If it still fails, a static fallback object is returned:
```json
{ "verdict": "PARTIAL", "explanation": "Could not verify this claim automatically. Please check the official election authority website.", "source": null }
```

---

## 3. Quiz Generator

### Purpose
Generate 5 multiple-choice questions about a country's election process, with correct answers and explanations — dynamically, so every quiz is different.

### Design Decisions
- The entire quiz is generated in one call rather than question-by-question to minimise latency and API cost.
- Questions are asked at mixed difficulty: 2 basic, 2 intermediate, 1 hard. This is specified in the prompt rather than left to the model, ensuring the quiz is accessible to first-time users while still being interesting for knowledgeable ones.
- The `correct` field is an integer index (0–3) rather than a string, so the frontend can highlight the correct option without string matching.
- Topic coverage is seeded in the prompt to prevent the model from generating 5 questions about the same fact.

### Prompt Template
```
Generate a 5-question multiple-choice quiz about elections in {COUNTRY_NAME}.

Topic coverage (use one question per topic):
1. Voter registration or eligibility
2. Polling day procedures
3. Counting or results process
4. A key election term or acronym (e.g. EVM, FPTP, Electoral College)
5. A common election myth or misconception

Difficulty: questions 1–2 should be basic, 3–4 intermediate, question 5 challenging.

Respond with ONLY a valid JSON array of 5 objects, each in this exact format:
{
  "question": "The question text ending with a question mark?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct": 0,
  "explanation": "1–2 sentence explanation of why the correct answer is right."
}

Rules:
- correct is the zero-based index of the correct option in the options array
- All 4 options must be plausible — avoid obviously wrong distractors
- Do not include any text outside the JSON array
- Base all questions on factual, verifiable information about {COUNTRY_NAME}'s election system
- Country code: {COUNTRY_CODE}
```

### Fallback
If Gemini returns malformed JSON or the API call fails (e.g. quota exceeded), the app returns a static 5-question set pre-loaded in `data/` for that country. This ensures the quiz feature is always functional during a live demo.

---

## 4. Prompt Safety Architecture

All user inputs pass through `utils.py` before reaching any Gemini call:

```python
def sanitize_input(text):
    # 1. Strip HTML tags
    clean_text = re.sub(r'<.*?>', '', text)
    # 2. Bleach sanitization for XSS safety
    clean_text = bleach.clean(clean_text, tags=[], strip=True)
    # 3. Hard length cap
    clean_text = clean_text[:500]
    # 4. Prompt injection guard
    injection_patterns = [
        "ignore previous", "ignore all", "system prompt",
        "jailbreak", "disregard", "forget your instructions",
        "you are now", "act as", "roleplay as"
    ]
    for pattern in injection_patterns:
        if pattern in clean_text.lower():
            return "I can only answer election-related questions."
    return clean_text.strip()
```

This means Gemini never receives raw user input — it always receives sanitized, length-capped, injection-checked text.

---

## 5. Token and Cost Efficiency

| Feature | Avg. Input Tokens | Avg. Output Tokens | Calls Per User Session |
|---|---|---|---|
| Chat | ~180 | ~150 | ~5 |
| Myth Buster | ~120 | ~100 | ~2 |
| Quiz | ~200 | ~600 | ~1 |

To minimise cost:
- Chat uses `gemini-1.5-flash` (lowest cost, fastest latency) — appropriate since answers are short.
- Quiz uses the same model but with `max_output_tokens=1200` to give room for 5 full questions.
- Myth Buster caps output at `max_output_tokens=300` since the JSON response is compact.
- Flask-Caching caches quiz responses per country for 1 hour so repeat requests don't trigger new API calls.

---

## 6. Why Gemini Over Other Models

- **Gemini 1.5 Flash** is a Google-native model, directly integrated with the Google Cloud ecosystem — consistent with the competition's emphasis on Google Services.
- The `google-generativeai` SDK provides first-class Python support with streaming, system instructions, and safety settings built in.
- Gemini's built-in safety filters provide an additional layer of content moderation on top of ElectIQ's own input sanitization.
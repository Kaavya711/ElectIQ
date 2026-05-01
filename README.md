# ElectIQ 🗳️
### *Understand elections. Know your role.*

A smart, interactive civic education platform powered by Google Gemini — built for the Google Prompt Wars competition.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-ElectIQ-green)](https://electiq.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Google-Gemini%201.5%20Flash-orange)](https://deepmind.google/gemini)

---

## Chosen Vertical

**Civic Education Assistant** — ElectIQ helps voters, candidates, and civic learners understand election processes across 5 countries (India, USA, UK, Australia, Germany), with personalised guidance based on who they are and what they need to do.

The core problem: most people encounter elections passively. They don't know their rights, don't understand procedures, and can't easily fact-check what they read. ElectIQ solves this with a role-aware assistant that gives you the right information at the right time.

---

## Approach and Logic

### Role-Aware Architecture
ElectIQ centres on a three-role model: **Voter**, **Candidate**, and **Learner**. Every feature — the timeline, checklist, AI chat, quiz — adapts its content based on the user's selected role and country. A Candidate in India sees nomination deadlines and Form 26 requirements; a Voter in Australia sees compulsory voting rules and how-to-vote cards.

### Decision-Making Flow
```
User selects country → selects role → all content scopes to that context
         ↓
   Dashboard shows role-relevant quick links
         ↓
   Timeline shows role-specific notes per election milestone
         ↓
   Checklist shows only tasks relevant to that role and registration status
         ↓
   AI Chat answers questions in the context of that country and role
```

### AI Integration Strategy
Rather than using AI as a general chatbot, ElectIQ uses Gemini for three specific, bounded tasks where AI genuinely adds value over static content:
1. **Open-ended Q&A** — questions that don't fit a FAQ format
2. **Myth classification** — real-time fact-checking of any user-submitted claim
3. **Dynamic quiz generation** — fresh questions every session, covering different topics

All AI outputs pass through input sanitization before being sent to Gemini and output validation before being shown to users. See `PROMPTS.md` for full prompt engineering documentation.

---

## How the Solution Works

### Features

| Feature | Description | AI-Powered |
|---|---|---|
| 📅 Full Timeline | Interactive election timeline from announcement to results, with role-specific notes at each milestone | No |
| 🧭 Guided Flow | Step-by-step path tailored to the user's role and registration status | No |
| ✅ My Checklist | Role-specific task checklist with progress tracked in Firebase Realtime DB | No |
| 💡 Myth Buster | Submit any election claim and get a TRUE / FALSE / PARTIAL verdict with explanation | **Yes — Gemini** |
| 🤖 Ask AI | Conversational assistant for any election question, country-scoped and role-aware | **Yes — Gemini** |
| 📝 Quiz | 5-question dynamic quiz generated fresh per session, different every time | **Yes — Gemini** |
| 📖 Glossary | Searchable definitions for every election term, with examples | No |
| 🗺️ Polling Booth | Find polling locations by pincode using Google Maps (India) | No |

### Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | Flask 3.0 (Python) | Lightweight, easy to deploy, blueprint-based structure |
| AI | Google Gemini 1.5 Flash | Native Google SDK, fast, cost-efficient for short outputs |
| Database | Firebase Realtime DB | Real-time checklist state sync, serverless, Google-native |
| Maps | Google Maps JavaScript API | Polling booth finder with geocoding |
| Analytics | Google Analytics 4 | Page-level engagement tracking |
| Translation | Google Translate Widget | Multi-language support for regional users |
| Hosting | Render (production) | Zero-config Python deployment |

### Project Structure

```
ElectIQ/
├── app.py                  # Flask app factory, blueprints, security headers
├── utils.py                # Input sanitization, injection guards, bleach cleaning
├── requirements.txt        # All dependencies pinned
├── PROMPTS.md              # Gemini prompt engineering documentation
├── data/
│   ├── checklists.py       # Role × status × country checklist data
│   ├── countries.py        # Supported country definitions
│   ├── glossary.py         # Election term definitions per country
│   ├── myths.py            # Pre-loaded myth/fact pairs
│   └── timelines.py        # Election timeline data per country
├── routes/
│   ├── main.py             # Page routes, session management, country/role logic
│   ├── ai.py               # /api/chat and /api/bust-myth endpoints
│   ├── quiz.py             # /api/generate-quiz and /api/submit-quiz endpoints
│   └── maps.py             # /api/find-booths endpoint
├── static/
│   ├── css/                # main.css, chat.css, quiz.css, timeline.css
│   └── js/                 # chat.js, checklist.js, main.js, maps.js, quiz.js, timeline.js
├── templates/              # Jinja2 templates (base, dashboard, all feature pages)
└── tests/
    ├── test_routes.py      # Route smoke tests
    ├── test_checklist.py   # Checklist API and data tests
    └── test_ai.py          # AI endpoint and sanitization tests
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Git
- A Google Cloud project with Gemini API enabled
- Firebase project with Realtime Database enabled

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/Kaavya711/ElectIQ.git
cd ElectIQ

# 2. Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your API keys (see Environment Variables section below)

# 5. Run the development server
flask run
# App runs at http://127.0.0.1:5000
```

### Environment Variables

Create a `.env` file based on `.env.example`:

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google AI Studio API key — enables AI Chat, Myth Buster, Quiz |
| `FLASK_SECRET_KEY` | Yes | Random string for Flask session signing |
| `FIREBASE_DB_URL` | Yes | Firebase Realtime Database URL (e.g. `https://your-project.firebaseio.com`) |
| `GOOGLE_MAPS_API_KEY` | Optional | Enables the Polling Booth Finder map |
| `GA_MEASUREMENT_ID` | Optional | Google Analytics 4 measurement ID |
| `FLASK_ENV` | Optional | `development` or `production` (default: `production`) |

### Running Tests

```bash
pytest tests/ -v
```

Tests cover route smoke testing, checklist state API, AI endpoint response structure, and input sanitization.

---

## Google Services Used

### Google Gemini API
The core AI layer. Used for the Chat Assistant, Myth Buster, and Quiz Generator. Gemini 1.5 Flash was chosen for its speed and cost efficiency — appropriate for a civic education context where answers should be quick and accessible. See `PROMPTS.md` for full prompt design documentation.

### Firebase Realtime Database
Persists checklist progress across sessions without requiring user authentication. Each checklist state is stored under a session-scoped key so users can return to their progress. Firebase was chosen over a SQL database because it requires no schema migrations, scales automatically, and is deeply integrated with the Google Cloud ecosystem.

### Google Maps JavaScript API
Powers the Polling Booth Finder for India. Users enter a pincode and state to see nearby polling stations on an interactive map with walking directions. The map uses a custom cream-toned style to match ElectIQ's design system.

### Google Analytics 4
Tracks page views, feature usage (which sections users visit), and session duration. This data can help election authorities understand which parts of the process users find most confusing.

### Google Translate Widget
Embedded in the sidebar to allow multi-language access. Particularly important for India, where ElectIQ supports translation into Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, and Punjabi — reaching voters who may not be comfortable in English.

---

## Assumptions Made

1. **No authentication required**: ElectIQ is a civic education tool, not a voting platform. Users don't need accounts. Checklist progress is tied to the browser session and Firebase for persistence.
2. **Country data is static for now**: Election timelines, glossary terms, and checklists are curated data rather than live feeds from election commission APIs. This ensures the app works reliably even if external APIs change.
3. **India is the primary market**: The deepest data coverage (timelines, checklists, glossary, myths, polling booth finder) is for India. Other countries have the same feature set with proportionally less detail.
4. **Gemini responses are educational only**: All AI outputs include a disclaimer that they are not legal advice. The prompts explicitly instruct Gemini not to express political opinions.
5. **Single-branch deployment**: The repository maintains a single `main` branch as required by competition rules. All development and production code lives here.

---

## Security

- **Input sanitization**: All user inputs are passed through `utils.py` before reaching any Gemini call or database write. This includes HTML tag stripping (via `bleach`), length capping at 500 characters, and prompt injection pattern detection.
- **CSRF protection**: Flask-WTF CSRF tokens on all forms.
- **Security headers**: CSP, X-Frame-Options, X-Content-Type-Options, and Referrer-Policy set on all responses via `@app.after_request`.
- **Rate limiting**: Flask-Limiter enforces 200 requests/day and 50 requests/hour per IP to prevent API abuse.
- **Environment variables**: No secrets in source code. All API keys are loaded from environment variables.

---

## Accessibility

- Skip-to-main-content link on every page
- Semantic HTML landmarks (`<main>`, `<nav>`, `<aside>`)
- `aria-label` on all icon-only buttons (send button, bookmark, menu toggle)
- Keyboard-navigable sidebar and role toggles
- Colour contrast compliant with WCAG 2.1 AA on all text/background combinations
- Mobile-responsive layout with hamburger menu for small screens

---

*Built with Google Antigravity · Powered by Google Gemini · ElectIQ is for educational use only and does not constitute legal or electoral advice.*
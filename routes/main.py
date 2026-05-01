"""
Main routes for ElectIQ — page rendering, country/role selection, and checklist state.
"""

from typing import Any
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, abort, jsonify
from data.countries import COUNTRIES
from data.timelines import TIMELINES
from data.checklists import CHECKLISTS
from data.myths import MYTHS
from data.glossary import GLOSSARY

main_bp = Blueprint('main', __name__)

MAX_CUSTOM_COUNTRY_LENGTH = 100


def _get_role() -> str:
    """Return the current user role from session, defaulting to Voter."""
    return session.get('role', 'Voter')


def _validate_country(country_code: str) -> bool:
    """Return True if the country code exists in the supported countries dict."""
    return country_code in COUNTRIES


@main_bp.route('/')
def index():
    """Render the landing page with country selection."""
    session.permanent = False
    return render_template('index.html', countries=COUNTRIES)


@main_bp.route('/set-country', methods=['POST'])
def set_country():
    """
    Handle country selection form submission.

    Redirects to the dashboard for known countries,
    or to a custom dashboard for user-typed country names.
    """
    country_code: str = str(request.form.get('country_code', ''))[:10].upper()
    if _validate_country(country_code):
        return redirect(url_for('main.dashboard', country_code=country_code))

    custom_country: str = str(request.form.get('custom_country', ''))[:MAX_CUSTOM_COUNTRY_LENGTH].strip()
    if custom_country:
        return redirect(url_for('main.dashboard', country_code='custom', name=custom_country))

    return redirect(url_for('main.index'))


@main_bp.route('/set-role', methods=['POST'])
def set_role():
    """
    Set the user's role in the session.

    Accepts JSON: {role: str} — one of Voter, Candidate, Learner.
    Returns JSON: {status: str, role: str}
    """
    data = request.get_json(silent=True) or {}
    role: str = str(data.get('role', ''))
    allowed_roles = {'Voter', 'Candidate', 'Learner'}
    if role in allowed_roles:
        session['role'] = role
        return jsonify({"status": "success", "role": role})
    return jsonify({"status": "error", "message": "Invalid role"}), 400


@main_bp.route('/dashboard/<country_code>')
def dashboard(country_code: str):
    """
    Render the main dashboard for a given country.

    Args:
        country_code: ISO 2-letter country code, or 'custom' for user-typed countries.
    """
    if country_code == 'custom':
        name = str(request.args.get('name', 'Your Country'))[:MAX_CUSTOM_COUNTRY_LENGTH]
        return render_template('dashboard.html',
                               country={"code": "custom", "name": name, "emoji": "🌍"},
                               role=_get_role())
    if not _validate_country(country_code):
        abort(404)
    return render_template('dashboard.html', country=COUNTRIES[country_code], role=_get_role())


@main_bp.route('/dashboard/<country_code>/timeline')
def timeline(country_code: str):
    """Render the election timeline page for a given country."""
    if not _validate_country(country_code):
        abort(404)
    return render_template('timeline.html',
                           country=COUNTRIES[country_code],
                           timeline=TIMELINES.get(country_code, []),
                           role=_get_role())


@main_bp.route('/dashboard/<country_code>/guided-flow')
def guided_flow(country_code: str):
    """Render the guided flow page for a given country."""
    if not _validate_country(country_code):
        abort(404)
    return render_template('guided_flow.html', country=COUNTRIES[country_code], role=_get_role())


@main_bp.route('/dashboard/<country_code>/checklist')
def checklist(country_code: str):
    """Render the role-specific checklist for a given country."""
    if not _validate_country(country_code):
        abort(404)
    role = _get_role()
    checklist_data: dict = CHECKLISTS.get(country_code, {}).get(role, {})
    return render_template('checklist.html',
                           country=COUNTRIES[country_code],
                           checklist=checklist_data,
                           role=role)


@main_bp.route('/api/checklist-state', methods=['GET', 'POST'])
def checklist_state():
    """
    Read or write checklist progress state.

    Uses Firebase Firestore if enabled, otherwise falls back to session storage.
    POST accepts JSON body. GET returns saved state dict.
    """
    if not current_app.config.get('FIREBASE_ENABLED'):
        if request.method == 'POST':
            data: Any = request.get_json(silent=True) or {}
            if not isinstance(data, dict):
                return jsonify({"error": "Invalid data format"}), 400
            session['checklist_progress'] = data
            return jsonify({"status": "saved to session"})
        return jsonify(session.get('checklist_progress', {}))

    try:
        from firebase_admin import firestore
        db = firestore.client()
        session_id: str = session.get('_id', 'anonymous')
        key = f"{session_id}_{request.args.get('country', '')}_{request.args.get('role', '')}"
        doc_ref = db.collection('checklists').document(key)

        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            doc_ref.set(data)
            return jsonify({"status": "saved to firestore"})

        doc = doc_ref.get()
        return jsonify(doc.to_dict() if doc.exists else {})
    except Exception as e:
        print(f"Firebase error: {e}")
        return jsonify({"error": "Database error"}), 500


@main_bp.route('/dashboard/<country_code>/myths')
def myths(country_code: str):
    """Render the myth buster page with preloaded myths for a given country."""
    if not _validate_country(country_code):
        abort(404)
    return render_template('myth_buster.html',
                           country=COUNTRIES[country_code],
                           preloaded_myths=MYTHS.get(country_code, []))


@main_bp.route('/dashboard/<country_code>/chat')
def chat(country_code: str):
    """Render the AI chat page for a given country."""
    if not _validate_country(country_code):
        abort(404)
    return render_template('chat.html', country=COUNTRIES[country_code])


@main_bp.route('/dashboard/<country_code>/quiz')
def quiz(country_code: str):
    """Render the quiz page for a given country."""
    if not _validate_country(country_code):
        abort(404)
    return render_template('quiz.html', country=COUNTRIES[country_code])


@main_bp.route('/dashboard/<country_code>/glossary')
def glossary(country_code: str):
    """Render the glossary page for a given country."""
    if not _validate_country(country_code):
        abort(404)
    return render_template('glossary.html',
                           country=COUNTRIES[country_code],
                           terms=GLOSSARY.get(country_code, []))


@main_bp.route('/dashboard/<country_code>/resources')
def resources(country_code: str):
    """Render the resources page for a given country."""
    if not _validate_country(country_code):
        abort(404)
    return render_template('resources.html', country=COUNTRIES[country_code])


@main_bp.route('/dashboard/<country_code>/polling-booth')
def polling_booth(country_code: str):
    """Render the polling booth finder page for a given country."""
    if not _validate_country(country_code):
        abort(404)
    return render_template('polling_booth.html', country=COUNTRIES[country_code])
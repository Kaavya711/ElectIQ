from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, abort
from data.countries import COUNTRIES
from data.timelines import TIMELINES
from data.checklists import CHECKLISTS
from data.myths import MYTHS
from data.glossary import GLOSSARY
import firebase_admin
from firebase_admin import firestore

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html', countries=COUNTRIES)

@main_bp.route('/set-country', methods=['POST'])
def set_country():
    country_code = request.form.get('country_code', '').upper()
    if country_code in COUNTRIES:
        return redirect(url_for('main.dashboard', country_code=country_code))
    # Handle custom typed country gracefully
    custom_country = request.form.get('custom_country', '').strip()
    if custom_country:
        return redirect(url_for('main.dashboard', country_code='custom', name=custom_country))
    return redirect(url_for('main.index'))

@main_bp.route('/set-role', methods=['POST'])
def set_role():
    role = request.json.get('role')
    if role in ['Voter', 'Candidate', 'Learner']:
        session['role'] = role
        return {"status": "success", "role": role}
    return {"status": "error", "message": "Invalid role"}, 400

@main_bp.route('/dashboard/<country_code>')
def dashboard(country_code):
    if country_code == 'custom':
        name = request.args.get('name', 'Your Country')
        return render_template('dashboard.html', country={"code": "custom", "name": name, "emoji": "🌍"}, role=session.get('role', 'Voter'))
    if country_code not in COUNTRIES:
        abort(404)
    return render_template('dashboard.html', country=COUNTRIES[country_code], role=session.get('role', 'Voter'))

@main_bp.route('/dashboard/<country_code>/timeline')
def timeline(country_code):
    if country_code not in COUNTRIES:
        abort(404)
    timeline_data = TIMELINES.get(country_code, [])
    return render_template('timeline.html', country=COUNTRIES[country_code], timeline=timeline_data, role=session.get('role', 'Voter'))

@main_bp.route('/dashboard/<country_code>/guided-flow')
def guided_flow(country_code):
    if country_code not in COUNTRIES:
        abort(404)
    return render_template('guided_flow.html', country=COUNTRIES[country_code], role=session.get('role', 'Voter'))

@main_bp.route('/dashboard/<country_code>/checklist')
def checklist(country_code):
    if country_code not in COUNTRIES:
        abort(404)
    
    role = session.get('role', 'Voter')
    checklist_data = CHECKLISTS.get(country_code, {}).get(role, {})
    return render_template('checklist.html', country=COUNTRIES[country_code], checklist=checklist_data, role=role)

@main_bp.route('/api/checklist-state', methods=['GET', 'POST'])
def checklist_state():
    if not current_app.config.get('FIREBASE_ENABLED'):
        # Fallback to session
        if request.method == 'POST':
            data = request.json
            session['checklist_progress'] = data
            return {"status": "saved to session"}
        else:
            return session.get('checklist_progress', {})

    try:
        db = firestore.client()
        session_id = session.get('_id', 'anonymous') # Should ideally have a stronger ID
        key = f"{session_id}_{request.args.get('country')}_{request.args.get('role')}"
        doc_ref = db.collection('checklists').document(key)

        if request.method == 'POST':
            data = request.json
            doc_ref.set(data)
            return {"status": "saved to firestore"}
        else:
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return {}
    except Exception as e:
        print(f"Firebase error: {e}")
        return {"error": "Database error"}, 500

@main_bp.route('/dashboard/<country_code>/myths')
def myths(country_code):
    if country_code not in COUNTRIES:
        abort(404)
    country_myths = MYTHS.get(country_code, [])
    return render_template('myth_buster.html', country=COUNTRIES[country_code], preloaded_myths=country_myths)

@main_bp.route('/dashboard/<country_code>/chat')
def chat(country_code):
    if country_code not in COUNTRIES:
        abort(404)
    return render_template('chat.html', country=COUNTRIES[country_code])

@main_bp.route('/dashboard/<country_code>/quiz')
def quiz(country_code):
    if country_code not in COUNTRIES:
        abort(404)
    return render_template('quiz.html', country=COUNTRIES[country_code])

@main_bp.route('/dashboard/<country_code>/glossary')
def glossary(country_code):
    if country_code not in COUNTRIES:
        abort(404)
    terms = GLOSSARY.get(country_code, [])
    return render_template('glossary.html', country=COUNTRIES[country_code], terms=terms)

@main_bp.route('/dashboard/<country_code>/resources')
def resources(country_code):
    if country_code not in COUNTRIES:
        abort(404)
    return render_template('resources.html', country=COUNTRIES[country_code])

@main_bp.route('/dashboard/<country_code>/polling-booth')
def polling_booth(country_code):
    if country_code not in COUNTRIES:
        abort(404)
    return render_template('polling_booth.html', country=COUNTRIES[country_code])

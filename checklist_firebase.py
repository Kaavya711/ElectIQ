import os
import requests
from flask import Blueprint, request, jsonify, session

checklist_bp = Blueprint('checklist', __name__)

FIREBASE_URL = os.environ.get('FIREBASE_DB_URL', '')


def _firebase_path(session_id):
    return f"{FIREBASE_URL}/checklists/{session_id}.json"


@checklist_bp.route('/checklist', methods=['GET'])
def get_checklist():
    session_id = session.get('session_id', 'anonymous')
    if not FIREBASE_URL:
        return jsonify(session.get('checklist', {}))
    try:
        r = requests.get(_firebase_path(session_id), timeout=5)
        return jsonify(r.json() or {})
    except Exception:
        return jsonify(session.get('checklist', {}))


@checklist_bp.route('/checklist', methods=['POST'])
def save_checklist():
    session_id = session.get('session_id', 'anonymous')
    data = request.get_json(silent=True) or {}
    if not FIREBASE_URL:
        session['checklist'] = data
        return jsonify({'status': 'saved', 'storage': 'session'})
    try:
        requests.put(_firebase_path(session_id), json=data, timeout=5)
        return jsonify({'status': 'saved', 'storage': 'firebase'})
    except Exception:
        session['checklist'] = data
        return jsonify({'status': 'saved', 'storage': 'session_fallback'})
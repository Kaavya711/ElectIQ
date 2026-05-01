"""
Firebase Realtime Database–backed checklist persistence for ElectIQ.

Provides GET and POST endpoints to read and write checklist progress.
Falls back to Flask session storage when Firebase is not configured.
"""

import logging
import os

import requests
from flask import Blueprint, jsonify, request, session

logger = logging.getLogger(__name__)

checklist_bp = Blueprint("checklist", __name__)

_FIREBASE_URL: str = os.environ.get("FIREBASE_DB_URL", "")
_REQUEST_TIMEOUT: int = 5  # seconds


def _firebase_path(session_id: str) -> str:
    """
    Build the Firebase REST API URL for a session's checklist document.

    Args:
        session_id: Unique session identifier.

    Returns:
        Full Firebase REST endpoint URL string.
    """
    return f"{_FIREBASE_URL}/checklists/{session_id}.json"


def _get_session_id() -> str:
    """
    Return the current session ID, defaulting to 'anonymous'.

    Returns:
        Session ID string.
    """
    return str(session.get("session_id", "anonymous"))


@checklist_bp.route("/checklist", methods=["GET"])
def get_checklist():
    """
    Retrieve saved checklist progress for the current session.

    Reads from Firebase Realtime Database when configured,
    otherwise reads from Flask session storage.

    Returns:
        200 JSON dict of checklist item states {item_id: bool}.
    """
    session_id: str = _get_session_id()

    if not _FIREBASE_URL:
        return jsonify(session.get("checklist", {}))

    try:
        response = requests.get(
            _firebase_path(session_id), timeout=_REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return jsonify(response.json() or {})
    except requests.RequestException as exc:
        logger.warning("Firebase GET failed, falling back to session: %s", exc)
        return jsonify(session.get("checklist", {}))


@checklist_bp.route("/checklist", methods=["POST"])
def save_checklist():
    """
    Persist checklist progress for the current session.

    Writes to Firebase Realtime Database when configured,
    otherwise falls back to Flask session storage.

    Accepts JSON: {item_id: bool, ...}

    Returns:
        200 JSON with status and storage backend used.
        400 if request body is not a valid JSON object.
    """
    session_id: str = _get_session_id()
    data: dict = request.get_json(silent=True) or {}

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    if not _FIREBASE_URL:
        session["checklist"] = data
        return jsonify({"status": "saved", "storage": "session"})

    try:
        response = requests.put(
            _firebase_path(session_id),
            json=data,
            timeout=_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return jsonify({"status": "saved", "storage": "firebase"})
    except requests.RequestException as exc:
        logger.warning("Firebase PUT failed, falling back to session: %s", exc)
        session["checklist"] = data
        return jsonify({"status": "saved", "storage": "session_fallback"})
"""灵感生成 API"""
from flask import Blueprint, request, jsonify
from app.services.deepseek import generate_ideas
from app.services import db

ideas_bp = Blueprint('ideas', __name__)


@ideas_bp.route('/ideas/generate', methods=['POST'])
def api_generate_ideas():
    try:
        episodes = db.list_episodes(1, 100)
        existing = [ep['topic'] for ep in episodes['episodes']]
        ideas = generate_ideas(existing)
        return jsonify({'ideas': ideas, 'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

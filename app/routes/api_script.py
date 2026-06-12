"""剧本生成/优化/重新生成 API"""
from flask import Blueprint, request, jsonify
from app.services.deepseek import generate_script, optimize_section, regenerate_script

script_bp = Blueprint('script', __name__)


@script_bp.route('/generate', methods=['POST'])
def api_generate():
    data = request.get_json()
    topic = data.get('topic', '').strip()
    if not topic:
        return jsonify({'error': '请输入一句话梗概'}), 400
    try:
        content = generate_script(topic)
        return jsonify({'content': content, 'topic': topic, 'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@script_bp.route('/optimize', methods=['POST'])
def api_optimize():
    data = request.get_json()
    content = data.get('content', '').strip()
    section = data.get('section', '').strip()
    keywords = data.get('keywords', '').strip()
    if not content or not section or not keywords:
        return jsonify({'error': '缺少参数'}), 400
    try:
        new_content = optimize_section(content, section, keywords)
        return jsonify({'content': new_content, 'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@script_bp.route('/regenerate', methods=['POST'])
def api_regenerate():
    data = request.get_json()
    topic = data.get('topic', '').strip()
    previous = data.get('previous', '').strip()
    if not topic:
        return jsonify({'error': '缺少梗概'}), 400
    try:
        content = regenerate_script(topic, previous)
        return jsonify({'content': content, 'topic': topic, 'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

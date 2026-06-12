"""剧集管理 API"""
from flask import Blueprint, request, jsonify
from app.services import db

episodes_bp = Blueprint('episodes', __name__)


@episodes_bp.route('/episodes/add', methods=['POST'])
def api_add_episode():
    """添加空白剧集"""
    data = request.get_json()
    title = data.get('title', '').strip()
    topic = data.get('topic', '').strip()
    if not topic:
        return jsonify({'error': '缺少梗概'}), 400
    if not title:
        title = topic[:20]
    try:
        ep = db.add_episode(title, topic)
        return jsonify({'episode': ep, 'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@episodes_bp.route('/episodes/create_with_script', methods=['POST'])
def api_create_with_script():
    """一步创建剧集并保存剧本（推荐使用）"""
    data = request.get_json()
    title = data.get('title', '').strip()
    topic = data.get('topic', '').strip()
    script_content = data.get('script_content', '')

    if not topic:
        return jsonify({'error': '缺少梗概（topic）'}), 400
    if not title:
        title = topic[:20]

    try:
        ep = db.create_with_script(title, topic, script_content)
        return jsonify({'episode': ep, 'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ⚠️ 注意：/episodes/list 必须放在 /episodes/<int:episode_id> 之前，
# 否则 "list" 会被当作 episode_id 匹配
@episodes_bp.route('/episodes/list')
def api_list_episodes():
    """分页列出剧集"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    result = db.list_episodes(page, per_page)
    return jsonify(result)


@episodes_bp.route('/episodes/save_script', methods=['POST'])
def api_save_script():
    """更新已有剧集的剧本内容"""
    data = request.get_json()
    episode_id = data.get('episode_id')
    script_content = data.get('script_content', '')
    if not episode_id:
        return jsonify({'error': '缺少剧集 ID'}), 400
    try:
        db.update_script(episode_id, script_content)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@episodes_bp.route('/episodes/<int:episode_id>', methods=['GET'])
def api_get_episode(episode_id):
    """获取单个剧集详情（含完整剧本内容）"""
    ep = db.get_episode(episode_id)
    if not ep:
        return jsonify({'error': '剧集不存在'}), 404
    return jsonify({'episode': ep, 'ok': True})


@episodes_bp.route('/episodes/<int:episode_id>', methods=['DELETE'])
def api_delete_episode(episode_id):
    """删除剧集"""
    try:
        db.delete_episode(episode_id)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

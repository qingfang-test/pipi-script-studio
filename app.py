"""
皮皮剧本工坊 — Flask 后端
提供剧本生成、优化、重新生成、灵感生成、剧集管理 API
"""

from flask import Flask, render_template, request, jsonify
from deepseek_client import generate_script, optimize_section, regenerate_script, generate_ideas
import db

app = Flask(__name__)


@app.route("/")
def index():
    """主页"""
    return render_template("index.html")


# ========== 剧本生成 ==========

@app.route("/api/generate", methods=["POST"])
def api_generate():
    """生成完整剧本"""
    data = request.get_json()
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "请输入一句话梗概"}), 400

    try:
        content = generate_script(topic)
        return jsonify({"content": content, "topic": topic, "ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/optimize", methods=["POST"])
def api_optimize():
    """根据关键字优化剧本的某个部分"""
    data = request.get_json()
    content = data.get("content", "").strip()
    section = data.get("section", "").strip()
    keywords = data.get("keywords", "").strip()

    if not content or not section or not keywords:
        return jsonify({"error": "缺少参数"}), 400

    try:
        new_content = optimize_section(content, section, keywords)
        return jsonify({"content": new_content, "ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/regenerate", methods=["POST"])
def api_regenerate():
    """重新生成剧本"""
    data = request.get_json()
    topic = data.get("topic", "").strip()
    previous = data.get("previous", "").strip()

    if not topic:
        return jsonify({"error": "缺少梗概"}), 400

    try:
        content = regenerate_script(topic, previous)
        return jsonify({"content": content, "topic": topic, "ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========== 灵感生成 ==========

@app.route("/api/ideas/generate", methods=["POST"])
def api_generate_ideas():
    """生成随机一句话梗概"""
    try:
        # 获取已有梗概以避免重复
        episodes = db.list_episodes(1, 100)
        existing = [ep["topic"] for ep in episodes["episodes"]]

        ideas = generate_ideas(existing)
        return jsonify({"ideas": ideas, "ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========== 剧集管理 ==========

@app.route("/api/episodes/add", methods=["POST"])
def api_add_episode():
    """将灵感加入剧集列表"""
    data = request.get_json()
    title = data.get("title", "").strip()
    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({"error": "缺少梗概"}), 400
    if not title:
        title = topic[:20]

    try:
        ep = db.add_episode(title, topic)
        return jsonify({"episode": ep, "ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/episodes/save_script", methods=["POST"])
def api_save_script():
    """保存剧本到已有剧集"""
    data = request.get_json()
    episode_id = data.get("episode_id")
    script_content = data.get("script_content", "")

    if not episode_id:
        return jsonify({"error": "缺少剧集 ID"}), 400

    try:
        db.update_script(episode_id, script_content)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/episodes/list")
def api_list_episodes():
    """分页列出剧集"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = db.list_episodes(page, per_page)
    return jsonify(result)


@app.route("/api/episodes/<int:episode_id>", methods=["DELETE"])
def api_delete_episode(episode_id):
    """删除剧集"""
    try:
        db.delete_episode(episode_id)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"🐷 皮皮剧本工坊启动成功！")
    print(f"   本机访问: http://127.0.0.1:8080")
    print(f"   本机访问: http://localhost:8080")
    print(f"   局域网IP: http://{local_ip}:8080")
    app.run(debug=False, host="0.0.0.0", port=8080)

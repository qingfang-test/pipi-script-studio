"""
皮皮剧本工坊 — SQLite 数据库模块
剧集持久化存储，方便将来迁移到 PostgreSQL
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")


def get_db():
    """获取数据库连接（自动创建表）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _init_tables(conn)
    return conn


def _init_tables(conn):
    """初始化表结构"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_num INTEGER NOT NULL,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            script_content TEXT DEFAULT '',
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


# ========== 剧集 CRUD ==========

def add_episode(title: str, topic: str) -> dict:
    """新增一集（自动分配集数）"""
    conn = get_db()
    row = conn.execute("SELECT COALESCE(MAX(episode_num), 0) + 1 FROM episodes").fetchone()
    next_num = row[0]

    conn.execute(
        "INSERT INTO episodes (episode_num, title, topic) VALUES (?, ?, ?)",
        (next_num, title, topic),
    )
    conn.commit()
    ep_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return {"id": ep_id, "episode_num": next_num, "title": title, "topic": topic}


def update_script(episode_id: int, script_content: str):
    """更新剧集的剧本内容"""
    conn = get_db()
    conn.execute(
        "UPDATE episodes SET script_content = ?, status = 'completed', updated_at = ? WHERE id = ?",
        (script_content, datetime.now().isoformat(), episode_id),
    )
    conn.commit()
    conn.close()


def get_episode(episode_id: int) -> dict | None:
    """获取单集"""
    conn = get_db()
    row = conn.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_episodes(page: int = 1, per_page: int = 10) -> dict:
    """分页列出剧集（按集数倒序）"""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]

    offset = (page - 1) * per_page
    rows = conn.execute(
        "SELECT * FROM episodes ORDER BY episode_num DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()
    conn.close()

    total_pages = max(1, (total + per_page - 1) // per_page)
    return {
        "episodes": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


def delete_episode(episode_id: int):
    """删除一集"""
    conn = get_db()
    conn.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
    conn.commit()
    conn.close()

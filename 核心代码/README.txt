========================================
  皮皮剧本工坊 — 核心代码说明
  更新日期：2026-06-13
========================================

项目路径：C:\Users\Dingxiaojia\hermes-workspace\pipi-script-studio\
服务器部署：47.238.77.221 /opt/pipi-script-studio/
访问地址：https://www.happy2sjb2026.fun

========================================
  文件结构与说明
========================================

1. app/__init__.py — Flask 应用工厂
   - create_app() 函数，注册蓝图，加载配置
   - 生产级应用入口

2. app/config.py — 配置文件
   - BaseConfig / ProductionConfig
   - 从 .env 读取 DEEPSEEK_API_KEY 和 DB_PATH

3. app/services/deepseek.py — DeepSeek AI 核心模块 ★
   - SYSTEM_PROMPT：剧本生成系统提示词（固定角色/风格/输出格式）
   - IDEAS_SYSTEM_PROMPT：灵感生成系统提示词
   - generate_script()：根据梗概生成完整剧本
   - optimize_section()：根据关键字优化指定部分
   - regenerate_script()：重新生成不同版本
   - generate_ideas()：随机生成5个创意梗概

4. app/services/db.py — SQLite 数据库模块
   - 剧集表 episodes（id/episode_num/title/topic/script_content/status）
   - add_episode() / update_script() / get_episode() / list_episodes()
   - create_with_script()：一步创建剧集并保存剧本

5. app/routes/main.py — 主页路由
   - GET / → 渲染 index.html

6. app/routes/api_script.py — 剧本 API
   - POST /api/generate — 生成剧本
   - POST /api/optimize — 优化剧本
   - POST /api/regenerate — 重新生成

7. app/routes/api_ideas.py — 灵感 API
   - POST /api/ideas/generate — 生成5个随机梗概

8. app/routes/api_episodes.py — 剧集管理 API
   - POST /api/episodes/create_with_script — 创建剧集+保存剧本
   - POST /api/episodes/save_script — 更新剧本
   - GET /api/episodes/list — 分页列表
   - GET /api/episodes/<id> — 单集详情
   - DELETE /api/episodes/<id> — 删除剧集

9. app/templates/index.html — 前端页面 ★
   - 完整 UI：输入框/灵感生成器/剧集列表/结果展示/编辑弹窗
   - 复制按钮：场景图/角色/剧情段/互动段/全部
   - 解析 Markdown 并按视频段独立展示

10. wsgi.py — Gunicorn 入口
    - from app import create_app; app = create_app()

11. deploy/ — 部署配置
    - nginx.conf — Nginx 反向代理配置
    - pipi-studio.service — Systemd 服务单元
    - deploy.sh — 一键部署脚本

12. .env（不入库） — 环境变量
    - DEEPSEEK_API_KEY=sk-xxx

========================================
  视频结构（当前版本）
========================================

总时长：20秒
- 0-15秒：剧情段（强钩子→小冲突→小反转）
- 0-5秒：互动段（皮皮正对镜头，引导点赞关注）

固定角色：小猪皮皮/小玥玥/猪妈妈/猪爸爸
固定风格：3D萌系卡通，毛绒质感，暖色调，电影级打光

========================================
  常用命令
========================================

本地开发：
  cd pipi-script-studio
  python app.py  （启动开发服务器 :8080）

服务器管理：
  systemctl status pipi-studio  查看状态
  systemctl restart pipi-studio 重启服务
  journalctl -u pipi-studio -f  查看日志

代码保存：
  git add -A && git commit -m "描述" && git push

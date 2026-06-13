"""
皮皮剧本工坊 — 应用工厂
生产级 Flask 应用，支持蓝图模块化扩展
"""
from flask import Flask
import os


def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # 配置
    app.config.from_object('app.config.ProductionConfig')
    if config_name:
        app.config.from_object(config_name)

    # 注册蓝图
    from app.routes.main import main_bp
    from app.routes.api_script import script_bp
    from app.routes.api_ideas import ideas_bp
    from app.routes.api_episodes import episodes_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(script_bp, url_prefix='/api')
    app.register_blueprint(ideas_bp, url_prefix='/api')
    app.register_blueprint(episodes_bp, url_prefix='/api')

    return app

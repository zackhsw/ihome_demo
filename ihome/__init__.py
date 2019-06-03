import os
from logging.handlers import RotatingFileHandler

import redis
import logging
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import config_map

# 数据库
from ihome.utils.commons import ReConverter

db = SQLAlchemy()

# 创建redis连接对象
redis_store = None
csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.WARNING)
file_log_handler = RotatingFileHandler(os.path.abspath(os.path.dirname(__file__))+"\logs\log", maxBytes=1024 * 1024 * 100, backupCount=10)
#                                 日志登级     输出日志信息文件名  行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
file_log_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """
    创建flask应用对象
    :param config_name: str  配置模式名称 ("develop","product")
    :return:
    """
    app = Flask(__name__)
    conf = config_map[config_name]
    app.config.from_object(conf)

    # 使用app初始化db
    db.init_app(app)

    # 初始化redis
    global redis_store
    redis_store = redis.StrictRedis(host=conf.REDIS_HOST, port=conf.REDIS_PORT)

    # 利用flask-session,将session数据保存到redis中
    Session(app)

    # 为flask补充csrf防护
    csrf.init_app(app)

    # 为flask添加自定义的转换器
    app.url_map.converters['re'] = ReConverter

    # 注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

    # 注册提供静态文件的蓝图
    from ihome import web_html
    app.register_blueprint(web_html.html)

    return app

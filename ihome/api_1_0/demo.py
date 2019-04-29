from flask import logging, current_app

from . import api


@api.route('/index')
def index():
    current_app.logger.error("xxx严重错误")  # 错误级别
    current_app.logger.warn("警告")  # 警告级别
    current_app.logger.info("info")  # 消息提示级别
    current_app.logger.debug("debug")  # 调试级别
    return "index page"

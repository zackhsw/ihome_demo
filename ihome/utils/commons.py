# coding:utf-8
import functools

from flask import session, jsonify, g
from werkzeug.routing import BaseConverter

# 定义正则转换器
from ihome.utils.response_code import RET


class ReConverter(BaseConverter):
    """"""

    def __init__(self, url_map, regex):
        super(ReConverter, self).__init__(url_map)
        self.regex = regex


# 定义的验证登录状态的装饰器
def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get('user_id')
        # 如果用户是登录的，执行视图函数
        if user_id is not None:
            # 将user_id保存到g,在视图函数中通过g对象获取保存数据
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 如果未登录，返回未登录信息
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    return wrapper

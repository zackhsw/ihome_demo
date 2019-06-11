#coding:utf8
import re

from flask import request, jsonify, current_app, session
from pymysql import IntegrityError

from ihome import redis_store, db
from ihome.constants import LOGIN_ERROR_MAX_TIMES, LOGIN_ERROR_FORBID_TIME
from ihome.utils.response_code import RET
from . import api, User


@api.route('/users', methods=['POST'])
def register():
    """
    regiter
    请求参数：手机号，密码，短信验证码
    参数格式：json
    :return:
    """
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')

    # 校验参数
    if not all([mobile,  password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不对')

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='两次密码不对')

    # # 从redis中取出短信验证码
    # try:
    #     real_sms_code = redis_store.get('sms_code_%s' % mobile)
    # except Exception as e:
    #     current_app.logger.error(e)
    #
    # # 判断短信验证码是否过期
    # if real_sms_code is None:
    #     return jsonify(errno=RET.NODATA, errmsg='短信验证码失效')
    #
    # # 删除redis中短信验证码，防止重复使用
    # try:
    #     redis_store.delete('sms_code_%s' % mobile)
    # except Exception as e:
    #     current_app.logger.error(e)
    #
    # # 判断用户填写短信验证码的正确性
    # if real_sms_code != sms_code:
    #     return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')
    # 判断用户的额手机号是否注册过
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg='数据库异常')
    # else:
    #     if user is not None:
    #         return jsonify(errno=RET.DATAEXIST, errmsg='手机号已存在')
    # 保存用户的注册数据到数据库中
    user = User(name=mobile, mobile=mobile)
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后的回滚
        db.session.rollback()
        # 表示手机号出现重复，即手机注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号已存在')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    # 保存登录状态session中
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='注册成功')


@api.route("/sessions", methods=['POST'])
def login():
    """登录
    参数：手机号、密码"""
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')
    # 校验参数
    # 参数完整校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    # 手机号格式
    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    # 判断错误次数是否超过限制，如果超过限制，则返回
    # redis记录："access_nums_请求的ip":次数
    user_ip = request.remote_addr  # 用户的ip地址
    try:
        access_nums = redis_store.get('access_nums_%s' % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) > LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多，请稍后重试")

    # 从数据库中根据手机号查询用户的数据对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 用数据库的密码与用户填写的密码进行对比验证
    if user is None or not user.check_password(password):
        # 如果验证失败，记录错误次数，返回信息
        try:
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, LOGIN_ERROR_FORBID_TIME)  # 一定时间 消除access_num_%s
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR, errmsg="用户或密码错误")

    # 如果验证相同成功，保存登录状态，在session中
    session['name'] = user.name
    session['mobile'] = user.mobile
    session['user_id'] = user.id


@api.route('/session', methods=['GET'])
def check_login():
    """检查登录状态"""
    # 尝试从session中获取用户的名字
    name = session.get('name')
    # 如果session中数据name名字存在，则表示用户已登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg='true', data={'name': name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg='false')


@api.route('/session', methods=['DELETE'])
def logout():
    # 清除session数据
    csrf_token = session.get("csrf_token")
    session.clear()
    session["csrf_token"] = csrf_token
    return jsonify(errno=RET.OK, errmsg="OK")

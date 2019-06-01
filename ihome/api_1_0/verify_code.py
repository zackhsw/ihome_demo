# coding:utf-8
import random

from flask import current_app, jsonify, make_response, request

from ihome.libs.yuntongxun.sms import CCP
from ihome.models import User
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from . import api
from ihome import redis_store, constants
from ihome.tasks.task_sms import send_sms


@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :return: 验证码图片, 异常时 返回json
    """
    # 业务逻辑处理
    # 生成验证码图片
    # 名字，真实文本，图片数据
    name, text, image_data = captcha.generate_captcha()
    # 将验证码真实值与编号保存到redis中，设置有效期
    # redis: 字符串  列表   哈希   set  zset
    # "key":xxx
    # 使用哈希维护有效期的时候只能整体设置
    # "image_codes":{"编号1","真实文本1"}

    # 单条维护记录，选用字符串
    # "image_code_编号1":"真实值"
    # "image_code_编号2":"真实值"
    # redis_store.set("image_code_%s" % image_code_id,text)
    # redis_store.expire("image_code_%s" % image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES)
    try:
        # 设置值 同时设置有效期            记录名称                                              记录值
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="save image code id failed")

    # 返回图片
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


# GET /api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id=xxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    # 获取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get('image_code_id')
    # 校验参数
    if not all([image_code_id, image_code]):
        # 表示参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 业务逻辑处理
    # 从redis取出真实值的图片验证码
    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)  # 返回的类型 bytes
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    # 判断图片验证码是否过期
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码失败')

    # 与用户填写的值进行对比
    if str(real_image_code, encoding='utf8').lower() != image_code.lower():
        # 表示用户填写错误
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')

    # 判断对于这个手机号的操作，在60秒之前是否有记录，有 被认为操作频繁，不接受处理
    try:
        send_flag = redis_store.get('send_sms_code_%' % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            return jsonify(errno=RET.REQERR, errmsg='请求过于频繁，请60秒后重试')

    # 删除redis中的图片验证码，防治用户使用同一个图片验证码 验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAERR, errmsg='手机号已存在')
    # 如果手机号不存在，则生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # 保存真实的短信验证码
    try:
        redis_store.setex('sms_code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户在60s再次发送短信的操作
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存短信验证码异常')

    # 发送短信
    # try:
    #     ccp = CCP()
    #     result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送异常")

    # 使用celery异步发送短信,delay函数调用后立即返回
    send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)

    # 返回值
    # if result == 0:
    #     return jsonify(errno=RET.OK, errmsg="发送成功")
    # else:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送失败")
    return jsonify(errno=RET.OK, errmsg="发送成功")

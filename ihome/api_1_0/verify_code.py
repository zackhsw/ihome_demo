# coding:utf-8
from flask import current_app, jsonify, make_response

from ihome.utils.captcha import captcha
from ihome.utils.response_code import RET
from . import api
from ihome import redis_store, constants


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

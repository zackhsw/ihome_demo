# coding:utf-8
from ihome.utils.captcha import captcha
from . import api


@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :return: 验证码图片
    """
    # 业务逻辑处理
    # 生成验证码图片
    # 名字，真是文本，图片数据
    name,text,image_data = captcha.generate_captcha()
    # 将验证码真实值与编号保存到redis中，设置有效期
    # redis: 字符串  列表   哈希   set  zset
    # "key":xxx
    # "image_codes":{"}
    # 返回值

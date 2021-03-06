# coding:utf-8
from celery import Celery

# 定义celery对象
from ihome.libs.yuntongxun.sms import CCP

celery_app = Celery("ihome", broker="redis://127.0.0.1:6379")


@celery_app.task
def send_sms(to, datas, temp_id):
    """发送短信异步任务"""
    ccp = CCP()
    try:
        result = ccp.send_template_sms(to, datas, temp_id)
    except Exception as e:
        result = -2
    return result

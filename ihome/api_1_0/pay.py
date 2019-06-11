import os

from flask import current_app, jsonify, g

from ihome.api_1_0 import api, constants
from ihome.models import Order
from ihome.utils.response_code import RET
from alipay import AliPay


@api.route('/orders/<int:roder_id>/payment', methods=["POST"])
def order_pay(order_id):
    user_id = g.user_id
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id,
                                   Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单数据有误")

    alipay_client = AliPay(
        appid="",
        app_notify_url=None,
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/app_public_key.pem"),
        sign_type="RSA2",
        debug=False
    )

    order_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no=order.id,
        total_amount=str(order.amount / 100.0),
        subject=u'租房 %s' % order.id,
        return_url="http://127.0.0.1:5000/orders.html",
        notify_url=None
    )

    pay_url = constants.ALIPAY_URL_PREFIX + order_string
    return jsonify(errno=RET.OK, errmsg="OK", data={"pay_url": pay_url})

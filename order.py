from flask import Blueprint

# 创建蓝图对象
app_orders = Blueprint("app_orders", __name__)


@app_orders.route("/get_orders")
def get_orders():
    return "get"

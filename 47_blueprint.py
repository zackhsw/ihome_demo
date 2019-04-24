from flask import Flask
from order import app_orders

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(app_orders)

if __name__ == '__main__':
    app.run()
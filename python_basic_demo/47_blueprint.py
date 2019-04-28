from flask import Flask
from python_basic_demo.order import app_orders

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(app_orders)

# 在__init__.py文件被执行的时候，把视图加载进来，让蓝图与应用程序知道有视图的存在
if __name__ == '__main__':
    app.run()
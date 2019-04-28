# coding:utf-8
import json

from flask import Flask, session

app = Flask(__name__)
# flask的session需要用到的秘钥字符串
app.config['SECRET_KEY'] = "secret a key"

# flask默认吧session保存到cookies中，
@app.route("/login")
def login():
    # 设置session数据
    session['name'] = 'python'
    session['mobile'] = '13111111111'
    return "login success"


@app.route("/index")
def index():
    # 获取session数据
    name = session.get('name')
    return "hello %s" % name


if __name__ == '__main__':
    app.run(debug=True)

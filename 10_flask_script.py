# coding:utf-8
from flask import Flask, session, request, url_for
from flask_script import Manager

app = Flask(__name__)

# 创建Manager管理类对象
manager = Manager(app)


@app.route("/index")
def index():
    return "index page"


if __name__ == '__main__':
    # app.run(debug=True)
    # app.run()
    manager.run()

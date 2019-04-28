# coding:utf-8
import json

from flask import Flask, session, request, url_for

app = Flask(__name__)


@app.route("/hello")
def index():
    print("index 被执行")
    # a = 1/0
    return "index page"


@app.before_first_request
def handle_before_first_request():
    print("handle_before_first_request")


@app.before_request
def handle_before_request():
    print("before_request")


@app.after_request
def handle_after_request(response):
    print("after_request")


@app.teardown_request
def handle_teardown_request(response):
    print("teardown_request")
    path = request.path
    if path in [url_for("index"), url_for("login")]:
        print("在请求钩子中判断请求的视图逻辑：index")
    elif path == url_for("hello"):
        print("在请求苟子仲判断请求的视图逻辑：hello")
    return response


if __name__ == '__main__':
    # app.run(debug=True)
    app.run()

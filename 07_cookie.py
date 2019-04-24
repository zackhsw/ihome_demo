# coding:utf-8
import json

from flask import Flask, request, abort, Response, make_response, jsonify

app = Flask(__name__)


@app.route("/set_cookie", methods=["GET"])
def set_cookie():
    resp = make_response("success")
    # 设置cookie,默认有效期是临时cookie，浏览器关闭就失效
    resp.set_cookie("itally", "996icu")
    # max_age设置有效期，单位：秒
    resp.set_cookie("i_tools", "python3.x", max_age=3600)
    resp.headers['Set-Cookie']="i_tools=python3.x.x; Expires=Wed, 24-Apr-2019 04:12:06 GMT; Max-Age=3600; Path=/"
    return resp


@app.route('/get_cookie')
def get_cookie():
    co = request.cookies.get('i_tools')
    return co


@app.route('/delete_cookie')
def delete_cookie():
    resp = make_response("del success")
    # 删除cookies
    resp.delete_cookie("i_tools")
    return resp


if __name__ == '__main__':
    app.run(debug=True)

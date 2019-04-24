# coding:utf-8

from flask import Flask, request, abort, Response, make_response

app = Flask(__name__)


@app.route("/index", methods=["GET"])
def login():
    # 1.使用元组 返回自定义的信息
    #         响应体     状态码    响应头
    # return "index page", 400, [("ITCAST", "python"), ("city", "beijing")]
    # return "index page", 400, {"ITCAST":"python", "city":"beijing"}
    # 2.使用make_response来构造相应信息
    resp = make_response("index page2")
    resp.status = '996 icu' # 设置状态码
    resp.headers['cit']='cd'  # 设置响应头
    return resp



if __name__ == '__main__':
    app.run(debug=True)

# coding:utf-8

from flask import Flask, request, abort, Response

app = Flask(__name__)


@app.route("/login", methods=["GET"])
def login():
    # name = request.form.get()
    # pwd = request.form.get()
    name = ""
    pwd = ""
    if name == 'user_name' and pwd == 'pwd_str':
        return "login success"
    else:
        # 使用abort函数立即终止视图函数，并返回给前端特定信息
        # 1.传递状态吗
        abort(404)
        # 2.传递响应体信息
        # resp = Response('login abort')
        # abort(resp)


@app.errorhandler(404)
def handle_404_error(err):
    """自定义处理错误方法"""
    # 这个函数的返回值是前端用户看到的最终结果
    return u"出现404错误，错误信息：%s" % err


if __name__ == '__main__':
    app.run(debug=True)

import hashlib

from flask import Flask, request, abort

WECHAT_TOKEN = ""
app = Flask(__name__)


@app.route("/wechat8080")
def wechat():
    """对接微信公众号服务器"""
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    echostr = request.args.get("echostr")

    # 校验参数
    if not all([signature, timestamp, nonce, echostr]):
        abort(400)

    li = [WECHAT_TOKEN, timestamp, nonce]  # 按照微信文档进行计算签名
    li.sort()  # 排序
    tmp_str = "".join(li)  # 拼接
    sign = hashlib.sha1(tmp_str).hexdigest()  # sha1加密，得到签名
    if signature != sign:
        abort(403)
    else:
        return echostr


if __name__ == "__main__":
    app.run(debug=True, port=8080)

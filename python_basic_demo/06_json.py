# coding:utf-8
import json

from flask import Flask, request, abort, Response, make_response, jsonify

app = Flask(__name__)


@app.route("/index", methods=["GET"])
def login():
    # json
    data = {
        'name': 'python',
        'age': 18
    }
    # return json.dumps(data), 200, {"Content-Type": "application/json"}
    # jsonify帮助转换为json数据，并设置响应头Content-Type 为application/json
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)

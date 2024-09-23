import logging
from flask import Flask, jsonify
from qq_slide import get_ticket

# 创建一个服务，赋值给APP
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


# 指定接口访问的路径（set_response是API名称），支持什么请求方式get，post
@app.route('/get_ticket', methods=['GET'])
async def set_response():
    res = await get_ticket()
    logging.info(res)
    return jsonify(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

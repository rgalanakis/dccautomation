from flask import Flask, jsonify, request


app = Flask(__name__)


@app.route('/eval', methods=['POST'])
def eval_():
    eval_result = '2'#eval(request.args['s'])
    result = {'result': eval_result}
    return 200, jsonify(result)


if __name__ == '__main__':
    app.run(host='localhost', port=8081, debug=True)

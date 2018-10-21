from flask import Flask, request, jsonify
import src
app = Flask(__name__)


@app.route("/",  methods=['GET'])
def prime():
    event = {
        'httpMethod': 'GET',
        'queryStringParameters': request.args
    }
    context = None
    results = src.lambda_handler(event, context)
    print(results)
    return app.make_response((results['body'], results['statusCode'], results['headers']))


if __name__ == "__main__":
    app.run()

from flask import Flask, request

app = Flask(__name__)

@app.route('/hello')
def index():
    name = request.args.get('name')
    return '你好，' + name

if __name__ == '__main__':
    app.run()
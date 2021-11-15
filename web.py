import os
import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/empty')
def empty():
    return flask.render_template('empty.html')

@app.route('/lixcraft')
def lixcraft():
    return flask.render_template('lixcraft.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
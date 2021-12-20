import os
import flask

app = flask.Flask(__name__)

def default_rendering():
    return 

@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/<a>')
def layer_a(a):
    return flask.render_template(f'{a}.html')

@app.route('/<a>/<b>')
def layer_b(a, b):
    return flask.render_template(f'{a}/{b}.html')

@app.route('/<a>/<b>/<c>')
def layer_c(a, b, c):
    return flask.render_template(f'{a}/{b}/{c}.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2021, debug=True)
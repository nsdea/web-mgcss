import os
import flask

app = flask.Flask(__name__)

def default_rendering():
    return 

for page in os.listdir('public/templates'):
    if page.startswith('__'):
        app.add_url_rule(page.replace('.html', '').replace('__', '/'), page, lambda page=page: flask.render_template(page) , methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2021, debug=True)
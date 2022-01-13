import os
import re
import time
import flask
import distro
import psutil
import random
import string
import minestat
import jinja2.exceptions

from datetime import datetime
from html import escape, unescape
from flask import request, jsonify

app = flask.Flask(__name__)

view_urls = {}

def default_rendering():
    return 

@app.route('/')
def home():
    return flask.render_template('index.html')

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(error):
    return flask.render_template(f'error.html', title='Page not found!', description=f'Couldn\'t find this website: {error.name}')

@app.errorhandler(404)
def error_404(error):
    return flask.render_template(f'error.html', title='File not found!', description=f'Couldn\'t find this file: {error.name}')

@app.route('/<path:subpath>')
def page_returner(subpath):
    return flask.render_template(f'{escape(subpath)}.html')

@app.route('/view-create', methods=['GET', 'POST'])
def create_page():
    global view_urls
    
    if request.method == 'GET':
        return flask.render_template(f'error.html', title='Unsupported request method!', description=f'This website can\'t be viewed with GET, as it\'s supposed to be POSTed.')

    code = ''.join(random.sample(string.ascii_lowercase + string.ascii_uppercase + string.digits, 5))
    view_urls[code] = request.get_json()
    

    return f'https://onlix.me/view/{code}'

def fix_formatting(text: str):
    return text.replace('  ', '&nbsp;').replace('\n', '\n<br>\n')

@app.route('/view/<code>')
def view_page(code):
    global view_urls

    if not view_urls.get(code):
        return flask.render_template(f'error.html', title='View page not found!', description=f'Couldn\'t find this code: {code}')

    return flask.render_template(f'view.html', title=fix_formatting(unescape(view_urls[code]['title'])), text=fix_formatting(unescape(view_urls[code]['text'])))

def readable_size(size):
    return round(size/1000000000, 1)

@app.route('/status')
def file_path():
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    try:
        mc = minestat.MineStat('onlix.me', 25565)
    except:
        mc = None

    return flask.render_template(f'status.html',
        cpu=psutil.cpu_percent(),
        cpus=psutil.cpu_count(),
        threads=psutil.cpu_count(logical=False),
        ram=f'{readable_size(ram[3])}/{readable_size(ram[0])} GB ({ram[2]}%)',
        disk=f'{readable_size(disk[1])}/{readable_size(disk[0])} GB ({disk[3]}%)',

        pids=len(psutil.pids()),
        boot_days=round((time.time()-psutil.boot_time())/86400),
        os=f'{distro.linux_distribution()[0]} {distro.linux_distribution()[1]}',
        mc_players=f'{mc.current_players}/{mc.max_players}' if mc else '',
        mc_version=mc.version if mc else '',
        mc_motd=mc.stripped_motd.strip('Ä') if mc else '',
        mc_ping=mc.latency if mc else '',
        mc_protocol=mc.slp_protocol if mc else ''
    )

@app.route('/mc-console-log')
def mc_console_log():
    log = []
    server_name = 'paper'
    lines = open(f'/home/minecraft/{server_name}/.console_history').read().split('\n')[:-1]

    for line in lines:
        line_date = line.split(':')[0]
        line_command = line.split(':')[1]
        
        for x in ['w', 'msg', 'teammsg', 'tell']:
            if line_command.startswith(x):
                line_command = f'{x} [CENSORED]'
        
        if line_command.startswith('ban-ip '):
            line_command = 'ban-ip [CENSORED IP]'
        
        if line_command.startswith('pardon-ip'):
            line_command = 'pardon-ip [CENSORED IP]'

        line_date = datetime.fromtimestamp(int(line_date)//1000).strftime('%d.%m.%y %H:%M:%S')
        
        log.append({'time': line_date, 'command': line_command})
    
    log.reverse()

    return flask.render_template(f'mcclog.html', log=log, server_name=server_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2021, debug=True)
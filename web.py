import os
import re
import json
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
SERVER_NAME = 'paper'

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
    page = escape(subpath)
    if os.path.exists(f'templates/{page}.hidden.html'):
        page = f'{page}.hidden'
    
    template = f'{page}.html'
    return flask.render_template(template)

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

    ops = [x['name'] for x in json.loads(open(f'/home/minecraft/{SERVER_NAME}/ops.json').read())]
    bans = [x['name'] for x in json.loads(open(f"/home/minecraft/{SERVER_NAME}/banned-players.json").read())]
    ip_bans = [x['name'] for x in json.loads(open(f"/home/minecraft/{SERVER_NAME}/banned-ips.json").read())]
    whitelist = [x['name'] for x in json.loads(open(f'/home/minecraft/{SERVER_NAME}/whitelist.json').read())]
    last_players = [x['name'] for x in json.loads(open(f'/home/minecraft/{SERVER_NAME}/usercache.json').read())[:5]]

    return flask.render_template(f'status.html',
        cpu=psutil.cpu_percent(),
        cpus=psutil.cpu_count(),
        threads=psutil.cpu_count(logical=False),
        ram=f'{readable_size(ram[3])}/{readable_size(ram[0])} GB ({ram[2]}%)',
        disk=f'{readable_size(disk[1])}/{readable_size(disk[0])} GB ({disk[3]}%)',

        pids=len(psutil.pids()),
        boot_days=round((time.time()-psutil.boot_time())/86400),
        os=f'{distro.linux_distribution()[0]} {distro.linux_distribution()[1]}',
        
        mc_player_count=f'{mc.current_players}/{mc.max_players}' if mc else '0/0',
        mc_version=mc.version if mc else 'Offline',
        mc_motd=mc.stripped_motd.replace('Â', '') if mc else 'Server is not avaiable',
        mc_ping=mc.latency if mc else '?',
        mc_protocol=mc.slp_protocol if mc else '?',
        mc_last_player=last_players,
        mc_last_players=len(last_players),
        mc_whitelist=whitelist,
        mc_whitelisted=len(whitelist),
        mc_op=ops,
        mc_ops=len(ops),
        mc_normal_ban=bans,
        mc_ip_ban=ip_bans,
        mc_normal_bans=len(bans),
        mc_ip_bans=len(ip_bans)
    )

@app.route('/mc-console-log')
def mc_console_log():
    log = []
    lines = open(f'/home/minecraft/{SERVER_NAME}/.console_history').read().split('\n')[:-1]

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

@app.route('/sitemap')
def sitemap():
    return 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2021, debug=True)
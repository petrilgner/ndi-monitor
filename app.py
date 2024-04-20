import threading
import yaml

from flask import Flask, render_template, redirect, flash, request
from flask_bootstrap import Bootstrap5

import ndi_discover as ndi
import presenter
import sysmon

app = Flask(__name__)
bootstrap = Bootstrap5(app)
configs = {}

app.secret_key = 'BJBNDIRc'
app.config['current_scene'] = '(auto)'


@app.before_request
def check_access():
    if 'allow_ips' in configs and configs['allow_ips']:
        if request.remote_addr not in configs['allow_ips']:
            return "Access denied", 403


@app.route('/')
def index():
    page_scenes = {'(auto)': {'name': '(Auto)', 'style': 'bg-dark'}}
    page_scenes.update(presenter.scenes)

    return render_template('index.html',
                           scenes=page_scenes,
                           last_switch=presenter.last_scene_switch,
                           current=app.config['current_scene'],
                           ndi_sources=ndi.last_detected_sources,
                           sys_stats=sysmon.sys_stats,
                           tv_control='tv_control' in configs and configs['tv_control'].get('enabled', False)
                           )


@app.route('/tvcontrol/<state>')
def tv_control(state: bool):
    if state == 'on':
        if presenter.turn_on_tv():
            flash("TV turned on from sleep!", "success")
    elif state == 'off':
        if presenter.turn_off_tv():
            flash("TV turned off!", "success")

    return redirect('/')


@app.route('/scene/<scene>')
def scene_switch(scene: str):
    if scene == '(auto)':
        ndi.auto_switch = True
        ndi.last_switched_scene = None
        app.config['current_scene'] = '(auto)'

    elif scene in presenter.scenes:
        ndi.auto_switch = False
        try:
            presenter.switch_scene(scene, manual=True)
            app.config['current_scene'] = scene
        except Exception as e:
            print("[EXCEPT] {}".format(e))
            flash("Scene switching error: {}".format(e), category='danger')

    return redirect('/')


def load_configs():
    global configs
    print("Loading configuration files")
    # Load app config
    with open('config/main.yaml', 'r') as file:
        print("App configs loaded successfully")
        configs = yaml.safe_load(file)

    presenter.load_config()
    presenter.init_tv_control(configs.get('tv_control', {}))

    sysmon.config_temp_sensor = configs.get('temp_sensor', None)

    if 'ndi_discover_interval' in configs:
        ndi.config_ndi_discover_interval = configs.get('ndi_discover_interval')


if __name__ == '__main__':
    load_configs()
    ndi.init_ndi_discover()

    for key, scene in presenter.scenes.items():
        print("Registering {}".format(key))
        ndi.register_scene(key, default=scene.get('default', False),
                           ndi_name=scene.get('ndi_name', None),
                           switch_fn=lambda k=key: presenter.switch_scene(k))

    ndi_thread = threading.Thread(target=ndi.discover_ndi)
    ndi_thread.daemon = True
    ndi_thread.start()

    sysmon_thread = threading.Thread(target=sysmon.update)
    sysmon_thread.daemon = True
    sysmon_thread.start()

    app.run(host=configs.get('http_host', '0.0.0.0'),
            port=configs.get('http_port', 5050))

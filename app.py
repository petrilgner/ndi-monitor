import threading

from flask import Flask, render_template, redirect, flash
from flask_bootstrap import Bootstrap5

import ndi_discover as ndi
import presenter
import sysmon

app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.secret_key = 'BJBNDIRc'
app.config['current_scene'] = '(auto)'


@app.route('/')
def index():
    page_scenes = {'(auto)': {'name': '(Auto)', 'style': 'bg-dark'}}
    page_scenes.update(presenter.scenes)

    return render_template('index.html',
                           scenes=page_scenes,
                           last_switch=presenter.last_scene_switch,
                           current=app.config['current_scene'],
                           ndi_sources=ndi.last_detected_sources,
                           sys_stats=sysmon.sys_stats
                           )


@app.route('/scene/<scene>')
def scene_switch(scene: str):
    if scene == '(auto)':
        ndi.auto_switch = True
        ndi.last_switched_scene = None
        app.config['current_scene'] = '(auto)'

    elif scene in presenter.scenes:
        ndi.auto_switch = False
        try:
            presenter.switch_scene(scene)
            app.config['current_scene'] = scene
        except Exception as e:
            print("[EXCEPT] {}".format(e))
            flash("Scene switching error: {}".format(e), category='danger')

    return redirect('/')


if __name__ == '__main__':
    presenter.load_config()
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

    app.run(host="0.0.0.0", port=5050)

import yaml
import os
import subprocess
from typing import Optional

scenes = {}
current_process: Optional[subprocess.Popen] = None
pwd = os.getcwd()
last_scene_switch: Optional[str] = None

chromium_base_params = ["chromium", "--kiosk", "--noerrors", "--disable-infobars", "--disable-session-crashed-bubble"]
ffmpeg_base_params = ["ffplay", "-fs", "-alwaysontop", "-fflags", "nobuffer", "-f", "libndi_newtek", "-bandwidth"]


def load_config():
    global scenes

    with open('config/scenes.yaml', 'r') as file:
        scenes = yaml.safe_load(file)


def close_all_players():
    global current_process
    print("[Presenter] Closing last player")
    if current_process:
        current_process.kill()


def switch_scene(scene_name: str):
    global current_process, last_scene_switch

    scene = scenes.get(scene_name)

    print("[Presenter] Switching scene {}".format(scene_name))
    last_scene_switch = scene_name
    close_all_players()

    if "ndi_name" in scene:
        # Run NDI viewer
        low_latency = scene.get("low_latency", False)
        low_bandwidth = scene.get("low_bandwidth", False)

        # ffplay -fs -alwaysontop -fflags nobuffer -f libndi_newtek -bandwidth 0 -i 'NDI-SOURCE (Stream 1)' LLat:
        # ffplay -fs -alwaysontop -fflags nobuffer -flags low_delay -framedrop -analyzeduration 0 -max_probe_packets
        # 1 -max_delay 0 -probesize 100000 -f libndi_newtek -bandwidth 0 -i 'NDI-SOURCE (Stream 1)'
        additional_params = ['1' if low_bandwidth else '0']
        if low_latency:
            additional_params += ['-flags', 'low_delay', '-framedrop', '-analyzeduration', '0',
                                  '-max-probe-packets', '1', '-max_delay', '0', '-probesize', '100000']

        additional_params += ['-i', scene["ndi_name"]]
        current_process = subprocess.Popen(ffmpeg_base_params + additional_params)
        print(current_process.args)

    elif "browser" in scene:
        # Run Chromium browser
        current_process = subprocess.Popen(chromium_base_params +
                                           ["file://{}/html/{}".format(pwd, scene['browser'])])

    elif "web" in scene:
        # Run Chromium browser
        current_process = subprocess.Popen(chromium_base_params + ["{}".format(scene['web'])])

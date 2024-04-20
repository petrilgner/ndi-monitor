import yaml
import os
import subprocess
from typing import Optional
from android_tv_rc import AndroidTVController

scenes = {}
current_process: Optional[subprocess.Popen] = None
pwd = os.getcwd()
last_scene_switch: Optional[str] = None
current_scene_turn_off_tv = False

# Remote TV
tv_controller: Optional[AndroidTVController] = None
tv_hdmi_number: Optional[int] = None

chromium_base_params = ["chromium", "--kiosk", "--noerrors", "--disable-infobars", "--disable-session-crashed-bubble"]
ffmpeg_base_params = ["ffplay", "-fs", "-alwaysontop", "-fflags", "nobuffer", "-f", "libndi_newtek", "-bandwidth"]


def load_config():
    global scenes

    with open('config/scenes.yaml', 'r') as file:
        scenes = yaml.safe_load(file)


def init_tv_control(config: dict):
    global tv_controller, tv_hdmi_number
    if config.get("enabled", False):

        print("Initializing TV control")
        print(config)
        adb_ip = config.get('adb_ip', None)
        if adb_ip:
            tv_controller = AndroidTVController(config['adb_ip'])
            tv_hdmi_number = config.get('hdmi_number', None)


def turn_on_tv() -> bool:
    if tv_controller:
        try:
            tv_controller.connect()
            if not tv_controller.is_connected():
                print("[TV] ERROR! Not connected")
                return False

            if tv_hdmi_number:
                print("[TV] Switching to HDMI {}".format(tv_hdmi_number))
                tv_controller.switch_hdmi(tv_hdmi_number)

            if not tv_controller.is_powered_on():
                print("[TV] Turing on from sleep")
                tv_controller.press_power()
                return True

        except Exception as e:
            print("[TV] ERROR! {}".format(e))


def turn_off_tv() -> bool:
    if tv_controller:
        try:
            tv_controller.connect()
            if not tv_controller.is_connected():
                print("[TV] ERROR! Not connected")
                return False

            if tv_controller.is_powered_on():
                print("[TV] Turing off screen")
                tv_controller.press_power()
                return True

        except Exception as e:
            print("[TV] ERROR! {}".format(e))


def close_all_players():
    global current_process
    print("[Presenter] Closing last player")
    if current_process:
        current_process.kill()


def switch_scene(scene_name: str, manual: bool = False):
    global current_process, last_scene_switch, current_scene_turn_off_tv

    scene = scenes.get(scene_name)

    print("[Presenter] Switching scene {}".format(scene_name))
    last_scene_switch = scene_name

    scene_turn_on_tv = scene.get("turn_on_tv", False)

    # Turn Off TV if current scene should do it (but only if new scene won't Turn On tv)
    # manual - do not turn off TV when changing scene manually (via Control web)
    if current_scene_turn_off_tv and not scene_turn_on_tv and not manual:
        turn_off_tv()

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
                                  '-max_probe_packets', '1', '-max_delay', '0', '-probesize', '100000']

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

    # Turn ON TV if required, remember if Turn Off after scene is required
    current_scene_turn_off_tv = scene.get("turn_off_tv", False)
    if scene_turn_on_tv:
        turn_on_tv()

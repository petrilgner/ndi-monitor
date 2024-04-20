import re
import psutil
import subprocess

config_temp_sensor = None

sys_stats = {
    'cpu': 0.0,
    'memory': 0.0
}


def update():

    if config_temp_sensor:
        pattern = r'{}:\s*\+(.*?)\s*°C'.format(config_temp_sensor)
        try:
            output = subprocess.check_output(['sensors']).decode('utf-8')
            match = re.search(pattern, output)
            if match:
                sys_stats['temp'] = match.group(1).strip()

        except subprocess.CalledProcessError as e:
            print(f"[SYSMON] Error: Failed to run sensors command: {e}")

    sys_stats['memory'] = psutil.virtual_memory().percent
    sys_stats['cpu'] = psutil.cpu_percent(interval=15)


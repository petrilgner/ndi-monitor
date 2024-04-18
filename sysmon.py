import psutil
import time

sys_stats = {
    'cpu': 0.0,
    'memory': 0.0,
}


def update():
    sys_stats['memory'] = psutil.virtual_memory().percent
    sys_stats['cpu'] = psutil.cpu_percent(interval=15)



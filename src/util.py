import psutil
import time
import threading

def limit_cpu_usage(max_cpu_percent):
    def decorator(func):
        def wrapper(*args, **kwargs):
            def monitor_cpu():
                while True:
                    cpu_usage = psutil.cpu_percent(interval=1)
                    if cpu_usage > max_cpu_percent:
                        time.sleep(0.1)  # Sleep to reduce CPU load

            monitor_thread = threading.Thread(target=monitor_cpu)
            monitor_thread.start()
            result = func(*args, **kwargs)
            monitor_thread.join()
            return result
        return wrapper
    return decorator
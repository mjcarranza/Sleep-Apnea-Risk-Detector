import psutil
import time
import GPUtil

PROCESS_NAME = "python3"  # nombre del proceso de tu app
INTERVAL = 2  # segundos entre mediciones

def get_process_usage():
    cpu_total = psutil.cpu_percent()
    mem_total = psutil.virtual_memory().percent

    # Buscar el proceso de la app
    for proc in psutil.process_iter(["name", "cpu_percent", "memory_percent"]):
        if proc.info["name"] == PROCESS_NAME:
            cpu_proc = proc.info["cpu_percent"]
            mem_proc = proc.info["memory_percent"]
            break
    else:
        cpu_proc = 0.0
        mem_proc = 0.0

    # GPU
    gpus = GPUtil.getGPUs()
    gpu_usage = gpus[0].load * 100 if gpus else 0
    gpu_mem = gpus[0].memoryUtil * 100 if gpus else 0

    print(f"""
==============================
 App Resource Monitor (Jetson)
==============================
CPU Total:       {cpu_total:.1f}%
RAM Total:       {mem_total:.1f}%
CPU App:         {cpu_proc:.1f}%
RAM App:         {mem_proc:.1f}%
GPU Load:        {gpu_usage:.1f}%
GPU Memory:      {gpu_mem:.1f}%
""")

def main():
    while True:
        get_process_usage()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

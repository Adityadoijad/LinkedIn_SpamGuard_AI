import psutil
import sys

def kill_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"Killing process {proc.pid} on port {port}")
                    proc.kill()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

if __name__ == "__main__":
    kill_port(8000)

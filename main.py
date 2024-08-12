import os
import requests
import re
import subprocess
import time
import json
import signal
import ctypes
import platform
import threading
import sys
import threading
import importlib.util
from colorama import Fore
from threading import Timer, Thread
from colorama import init, Fore, Style

ctypes.windll.kernel32.SetConsoleTitleW("Paper Manager")

def is_connected():
    try:
        response = requests.get('https://www.google.com', timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def install_requirements(requirements_url):
    try:
        response = requests.get(requirements_url)
        response.raise_for_status()
        requirements = response.text

        # Write the requirements to a local file
        with open('requirements.txt', 'w') as file:
            file.write(requirements)

        # Install the requirements
        subprocess.check_call([os.sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        os.remove('requirements.txt')  # Clean up the file after installation
        print("Requirements installed successfully.")
    except requests.RequestException as e:
        print(f"Error downloading requirements: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")

def load_module_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        code = response.text
        
        # Create a new module spec
        module_name = 'dynamic_module'
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        module = importlib.util.module_from_spec(spec)
        
        # Execute the code in the new module
        exec(code, module.__dict__)
        
        # List functions in the module
        functions = [attr for attr in dir(module) if callable(getattr(module, attr))]
        print("Available functions in the module:", functions)
        
        # Call the function if it exists
        if 'menu' in functions:
            print("Calling 'menu' function...")
            module.menu()
        else:
            print("Module does not contain 'menu' function.")
        return module
    except requests.RequestException as e:
        print(f"Error downloading module: {e}")
        return None
    except Exception as e:
        print(f"Error loading module: {e}")
        return None

def check_internet_connection():
    print("Checking internet connection...")
    try:
        requests.get('https://www.google.com/', timeout=5)
        return True
    except requests.ConnectionError:
        return False

if __name__ == "__main__":
    if check_internet_connection():
        print("Internet connection detected. Please wait to sync script on GitHub page...")
        time.sleep(1)
        print("Done! Enjoy using PaperMC-Manager.")
        time.sleep(1.5)
    else:
        print("No internet connection detected. Please check your internet connection and try again.")
        time.sleep(1.5)
    
    # Load and use the module
    module = load_module_from_github('https://raw.githubusercontent.com/sang765/PaperMC-Manager/main/paper_manager.py')

def main():
    try:
        requirements_url = 'https://raw.githubusercontent.com/sang765/PaperMC-Manager/main/requirements.txt'
        module_url = 'https://raw.githubusercontent.com/sang765/PaperMC-Manager/main/paper_manager.py'
        
        if is_connected():
            print("Internet connection detected. Please wait...")
            install_requirements(requirements_url)
            module = load_module_from_github(module_url)
            
            if module:
                print("Module loaded successfully.")
                # You can now use functions or classes from the module
                # For example, if the module has a function `main`, you can call it:
                if hasattr(module, 'main'):
                    module.main()
                else:
                    print("Module does not contain 'main' function.")
            else:
                print("Failed to load module.")
        else:
            print("No internet connection.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

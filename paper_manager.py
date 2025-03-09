import os
import requests
import re
import subprocess
import time
import json
import signal
import platform
import sys
import shutil
import traceback
import datetime
import tkinter as tk
from tkinter import filedialog
from colorama import Fore, init, Style

init(autoreset=True)

projects_url = "https://api.papermc.io/v2/projects/paper"
builds_url_template = f"https://api.papermc.io/v2/projects/paper/versions/{{version}}/builds"
download_url_template = "https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build_number}/downloads/{file_name}"

CHANGELOG_URL = "https://raw.githubusercontent.com/sang765/PaperMC-Manager/refs/heads/main/changelogs/CHANGELOG.md"
ERROR_LOG_FILE = "./logs/error.log"

config_file = "server_config.json"
GRAY = '\033[1;30m'
BOLD = '\033[1m'
ITALIC = '\033[3m'
RESET = '\033[0m'

default_config = {
    "ram": "4G",
    "nogui": True,
    "auto_update": False,
    "server_path": "",
    "webhook_url": ""
}

def get_latest_changelog_from_github():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(CHANGELOG_URL, timeout=5)
            if response.status_code == 200:
                content = response.text.splitlines()
                latest_section = []
                in_latest_section = False
                
                for line in content:
                    if line.startswith("## [") and not line.startswith("## [Unreleased]"):
                        if in_latest_section:
                            break
                        in_latest_section = True
                    if in_latest_section and line.strip():
                        latest_section.append(line)
                
                if not latest_section:
                    return Fore.YELLOW + "No changelog entries found in CHANGELOG.md yet."
                
                colored_content = []
                for line in latest_section:
                    if line.startswith("## ["):
                        colored_content.append(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                    elif line.startswith("### Added"):
                        colored_content.append(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                    elif line.startswith("### Changed"):
                        colored_content.append(f"{Fore.YELLOW}{line}{Style.RESET_ALL}")
                    elif line.startswith("### Removed"):
                        colored_content.append(f"{Fore.RED}{line}{Style.RESET_ALL}")
                    elif line.strip().startswith("-"):
                        colored_content.append(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
                    else:
                        colored_content.append(f"{Fore.MAGENTA}{line}{Style.RESET_ALL}")
                
                return "\n".join(colored_content)
            elif response.status_code == 404:
                return Fore.YELLOW + "CHANGELOG.md not found on GitHub. Please create it in the repository."
            else:
                return Fore.RED + f"Failed to fetch CHANGELOG.md (HTTP {response.status_code})."
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return Fore.RED + f"Error fetching changelog after {max_retries} attempts: {e}"

def select_server_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Choose folder have PaperMC JAR file")
    return folder_path

def check_papermc_folder(folder_path):
    for file in os.listdir(folder_path):
        match = re.match(r'paper-(\d+(?:\.\d+){1,2})-(\d+)\.jar', file)
        if match:
            return True
    return False

def load_config():
    try:
        with open('server_config.json', 'r') as f:
            content = f.read()
            if not content:
                print("File server_config.json trống")
                return {}
            config = json.loads(content)
            return config
    except FileNotFoundError:
        print("File server_config.json không tồn tại")
        return {}
    except json.JSONDecodeError as e:
        print("File server_config.json không đúng định dạng JSON: ", str(e))
        return {}

def save_config(config):
    with open('server_config.json', 'w') as f:
        f.write(json.dumps(config))
    print(Fore.GREEN + "Configuration saved successfully.")

config = load_config()

text_art = """
██████╗░░█████╗░██████╗░███████╗██████╗░███╗░░░███╗░█████╗░  ███╗░░░███╗░█████╗░███╗░░██╗░█████╗░░██████╗░███████╗██████╗░
██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗████╗░████║██╔══██╗  ████╗░████║██╔══██╗████╗░██║██╔══██╗██╔════╝░██╔════╝██╔══██╗
██████╔╝███████║██████╔╝█████╗░░██████╔╝██╔████╔██║██║░░╚═╝  ██╔████╔██║███████║██╔██╗██║███████║██║░░██╗░█████╗░░██████╔╝
██╔═══╝░██╔══██║██╔═══╝░██╔══╝░░██╔══██╗██║╚██╔╝██║██║░░██╗  ██║╚██╔╝██║██╔══██║██║╚████║██╔══██║██║░░╚██╗██╔══╝░░██╔══██╗
██║░░░░░██║░░██║██║░░░░░███████╗██║░░██║██║░╚═╝░██║╚█████╔╝  ██║░╚═╝░██║██║░░██║██║░╚███║██║░░██║╚██████╔╝███████╗██║░░██║
╚═╝░░░░░╚═╝░░╚═╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝╚═╝░░░░░╚═╝░╚════╝░  ╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░╚═╝░╚═════╝░╚══════╝╚═╝░░╚═╝
"""

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def log_error(error_message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {error_message}\n")
        traceback_str = traceback.format_exc()
        if traceback_str.strip() != "NoneType: None":
            f.write(f"Traceback: {traceback_str}\n")
    print(Fore.RED + f"Error logged: {error_message}")

def read_latest_error():
    if not os.path.exists(ERROR_LOG_FILE):
        return "No errors logged yet."
    with open(ERROR_LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return "No errors logged yet."
        last_error = []
        for line in reversed(lines):
            if line.strip().startswith("["):
                last_error.append(line)
                break
            elif last_error:
                last_error.append(line)
        return "".join(reversed(last_error)).strip()

def send_webhook(webhook_url, message, embed_title=None, embed_color=0x00FF00, error_log=None, execution_time=None):
    if not webhook_url:
        print(Fore.YELLOW + "❌ Webhook URL not set. Skipping webhook notification.")
        return
    
    data = {
        "username": "PaperMC Manager",
        "avatar_url": "https://i.imgur.com/GzfsT2w.png"
    }
    
    if embed_title:
        embed = {
            "title": embed_title,
            "description": message,
            "color": embed_color,
            "author": {
                "name": "PaperMC Manager",
                "icon_url": "https://i.imgur.com/GzfsT2w.png"
            },
            "footer": {
                "text": f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "icon_url": "https://github.com/sang765.png"
            }
        }
        if execution_time is not None:
            embed["footer"]["text"] += f" | Done ({execution_time:.3f}s)"
        if error_log:
            embed["fields"] = [{
                "name": "Error Details",
                "value": f"```\n{error_log}\n```",
                "inline": False
            }]
        data["embeds"] = [embed]
    else:
        data["content"] = message
    
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print(Fore.GREEN + "✅ Webhook sent successfully.")
        else:
            print(Fore.RED + f"❌ Failed to send webhook: HTTP {response.status_code}")
    except requests.RequestException as e:
        log_error(f"Error sending webhook: {e}")
        print(Fore.RED + f"Error sending webhook: {e}")

def get_versions():
    try:
        print(Fore.CYAN + "Fetching available versions...")
        response = requests.get(projects_url)
        response.raise_for_status()
        versions_data = response.json()
        versions = versions_data['versions']
        print(Fore.GREEN + f"Available versions:" + Fore.YELLOW + f" {versions}")
        return versions
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to fetch versions. Error: {e}")
        return []

def get_builds_for_version(version):
    try:
        print(Fore.CYAN + f"Fetching all builds for version" + Fore.GREEN + f" {version}...")
        builds_url = builds_url_template.format(version=version)
        response = requests.get(builds_url)
        response.raise_for_status()
        builds_data = response.json()
        builds = builds_data['builds']
        if builds:
            print(Fore.GREEN + f"Available builds for version {Fore.YELLOW}{version}{Fore.GREEN}: {Fore.CYAN}{[build['build'] for build in builds]}")
            return builds
        else:
            print(Fore.RED + "No builds found for this version.")
            return []
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to fetch builds. Error: {e}")
        return []

def get_current_version(server_path):
    for file in os.listdir(config['server_path']):
        if file.endswith('.jar'):
            match = re.match(r'paper-(\d+(?:\.\d+){1,2})-(\d+)\.jar', file)
            if match:
                return file
    return None

def delete_old_version(file_name):
    os.remove(os.path.join(folder_path, file_name))

def get_latest_version_url(version):
    builds = get_builds_for_version(version)
    if not builds:
        return None, None, None
    
    latest_build = max(builds, key=lambda b: b['build'])
    build_number = latest_build['build']
    file_name = f"paper-{version}-{build_number}.jar"
    
    if os.path.exists(os.path.join(config['server_path'], file_name)):
        return None, None, None
    
    download_url = download_url_template.format(version=version, build_number=build_number, file_name=file_name)
    print(Fore.GREEN + f"URL fetched successfully: {Fore.YELLOW}{download_url}")
    return version, build_number, file_name

def run_server(file_name, server_path_abs):
    if not shutil.which("java"):
        error_msg = "Java not found in PATH. Please install Java or add it to your system PATH."
        log_error(error_msg)
        send_webhook(config.get("webhook_url"), error_msg, "Server Error", 0xFF0000, read_latest_error())
        raise FileNotFoundError(error_msg)
    
    ram = config["ram"]
    nogui_option = "--nogui" if config["nogui"] else ""
    java_flags = [
        f'-Xms{ram}', f'-Xmx{ram}',
        '--add-modules=jdk.incubator.vector',
        '-XX:+UseG1GC',
        '-XX:+ParallelRefProcEnabled',
        '-XX:MaxGCPauseMillis=200',
        '-XX:+UnlockExperimentalVMOptions',
        '-XX:+DisableExplicitGC',
        '-XX:+AlwaysPreTouch',
        '-XX:G1HeapWastePercent=5',
        '-XX:G1MixedGCCountTarget=4',
        '-XX:InitiatingHeapOccupancyPercent=15',
        '-XX:G1MixedGCLiveThresholdPercent=90',
        '-XX:G1RSetUpdatingPauseTimePercent=5',
        '-XX:SurvivorRatio=32',
        '-XX:+PerfDisableSharedMem',
        '-XX:MaxTenuringThreshold=1',
        '-Dusing.aikars.flags=https://mcflags.emc.gs',
        '-Daikars.new.flags=true',
        '-XX:G1NewSizePercent=30',
        '-XX:G1MaxNewSizePercent=40',
        '-XX:G1HeapRegionSize=8M',
        '-XX:G1ReservePercent=20',
        '-jar', file_name
    ]
    
    if nogui_option:
        java_flags.append(nogui_option)

    return subprocess.Popen(['java'] + java_flags, cwd=server_path_abs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def read_input_with_timeout(prompt, timeout):
    if platform.system() == 'Windows':
        return read_input_windows(prompt, timeout)
    else:
        return read_input_unix(prompt, timeout)

def read_input_windows(prompt, timeout):
    import msvcrt
    print(prompt, end='', flush=True)
    start_time = time.time()
    input_chars = []
    
    while time.time() - start_time < timeout:
        if msvcrt.kbhit():
            ch = msvcrt.getch().decode('utf-8')
            if ch == '\r' or ch == '\n':
                break
            input_chars.append(ch)
        time.sleep(0.01)
    
    return ''.join(input_chars).strip().lower()

def read_input_unix(prompt, timeout):
    import select
    print(prompt, end='', flush=True)
    fd = sys.stdin.fileno()
    start_time = time.time()
    
    input_chars = []
    while time.time() - start_time < timeout:
        if select.select([sys.stdin], [], [], 0.1)[0]:
            ch = sys.stdin.read(1)
            if ch == '\n' or ch == '\r':
                break
            input_chars.append(ch)
    
    return ''.join(input_chars).strip().lower()

def handle_interrupt(signal, frame):
    print(Fore.RED + "Detected interruption signal. Back to main menu...")
    time.sleep(1)
    menu()

signal.signal(signal.SIGINT, handle_interrupt)

def start_server(jar_file, server_path_abs, webhook_url):
    start_time = time.time()
    current_version = os.path.basename(jar_file)
    jdk_version = get_jdk_version()
    
    send_webhook(webhook_url, 
                 f"Server starting with {current_version}\nJDK: {jdk_version}", 
                 "Server Starting", 0x00FF00,
                 execution_time=time.time() - start_time)
    print(Fore.GREEN + f"=================== STARTING SERVER ==================")
    print(Fore.GREEN + f"Starting server with: " + Fore.YELLOW + f"{current_version}")
    print(Fore.GREEN + f"======================================================")
    
    try:
        eula_file = os.path.join(server_path_abs, "eula.txt")
        if not os.path.exists(eula_file):
            with open(eula_file, "w") as f:
                f.write("eula=true")
            print(Fore.YELLOW + "Created eula.txt with eula=true")
        else:
            with open(eula_file, "r") as f:
                content = f.read()
                if "eula=false" in content.lower():
                    with open(eula_file, "w") as f:
                        f.write("eula=true")
                    print(Fore.YELLOW + "Changed eula=false to eula=true in eula.txt")
                elif "eula=true" not in content.lower():
                    with open(eula_file, "a") as f:
                        f.write("\neula=true")
                    print(Fore.YELLOW + "Added eula=true to eula.txt")

        server_process = run_server(jar_file, server_path_abs)
        
        while server_process.poll() is None:
            stdout_line = server_process.stdout.readline().strip()
            if stdout_line:
                print(stdout_line)
                if "Done" in stdout_line and "For help, type" in stdout_line:
                    send_webhook(webhook_url,
                                 f"Server {current_version} has finished starting up.",
                                 "Starting Done", 0x00FFFF,
                                 execution_time=time.time() - start_time)
        
        stderr_output = server_process.stderr.read().strip()
        if server_process.returncode != 0:
            error_msg = f"Server stopped with error (return code: {server_process.returncode}).\nStderr:\n{stderr_output}"
            log_error(error_msg)
            send_webhook(webhook_url, 
                         error_msg, 
                         "Server Error", 0xFF0000, 
                         read_latest_error(),
                         execution_time=time.time() - start_time)
            raise Exception(error_msg)
        
        stop_time = time.time()
        uptime_seconds = stop_time - start_time
        uptime_str = f"{uptime_seconds:.1f} seconds" if uptime_seconds < 60 else f"{uptime_seconds / 60:.1f} minutes"
        send_webhook(webhook_url, 
                     f"Server has stopped.\n**Uptime**: {uptime_str}", 
                     "Server Stopped", 0xFF0000,
                     execution_time=stop_time - start_time)
        return server_process, start_time
    except Exception as e:
        error_msg = f"Failed to start server: {e}"
        log_error(error_msg)
        send_webhook(webhook_url, 
                     error_msg, 
                     "Server Error", 0xFF0000, 
                     read_latest_error(),
                     execution_time=time.time() - start_time)
        raise

def start_server_no_loop():
    clear_terminal()
    config = load_config()
    server_path = config['server_path']
    project_dir = os.getcwd()
    server_path_abs = os.path.join(project_dir, server_path)
    current_version = get_current_version(server_path)

    if server_path:
        if config.get("auto_update", False):
            check_for_update_auto_mode()
        if current_version:
            jar_file = os.path.join(server_path_abs, current_version)
            if os.path.exists(jar_file):
                try:
                    server_process, start_time = start_server(jar_file, server_path_abs, config.get("webhook_url"))
                    server_process.wait()
                    print(Fore.RED + f"====================== SERVER STOPED =====================")
                    print(Fore.YELLOW + "NOTE: IF " + Fore.WHITE + "PAPER" + Fore.YELLOW + " HAS BEEN UPDATE FRIST TIME. SERVER AUTOMATIC STOPPED.")
                    print(Fore.RED + f"==========================================================")
                    print(Fore.YELLOW + "Back to menu...")
                    time.sleep(1)
                    menu()
                except Exception as e:
                    print(Fore.RED + f"Error occurred: {e}")
                    print(Fore.YELLOW + "Back to menu...")
                    time.sleep(1)
                    menu()
            else:
                error_msg = f"File jar {current_version} does not exist at path {server_path_abs}"
                log_error(error_msg)
                send_webhook(config.get("webhook_url"), error_msg, "Error", 0xFF0000, read_latest_error())
                print(Fore.YELLOW + error_msg)
        else:
            error_msg = "No Paper file found. Please configure a Paper version."
            log_error(error_msg)
            send_webhook(config.get("webhook_url"), error_msg, "Warning", 0xFFFF00, read_latest_error())
            print(Fore.YELLOW + error_msg)
    else:
        error_msg = "Server path not set. Please configure config."
        log_error(error_msg)
        send_webhook(config.get("webhook_url"), error_msg, "Error", 0xFF0000, read_latest_error())
        print(error_msg)

def start_server_loop():
    clear_terminal()
    config = load_config()
    server_path = config['server_path']
    project_dir = os.getcwd()
    server_path_abs = os.path.join(project_dir, server_path)
    current_version = get_current_version(server_path)

    if server_path:
        while True:
            current_version = get_current_version(server_path)
            if config.get("auto_update", False):
                check_for_update_auto_mode()
            if current_version:
                jar_file = os.path.join(server_path_abs, current_version)
                if os.path.exists(jar_file):
                    try:
                        server_process, start_time = start_server(jar_file, server_path_abs, config.get("webhook_url"))
                        server_process.wait()
                        print(Fore.RED + f"====================== SERVER STOPED =====================")
                        print(Fore.RED + "Server has stopped. Click " + Fore.GREEN + "\"Ctrl + C\"" + Fore.RED + " in 5 seconds to go back" + Fore.YELLOW + " to main menu.")
                        print(Fore.YELLOW + "NOTE: IF " + Fore.WHITE + "PAPER" + Fore.YELLOW + " HAS BEEN UPDATE FRIST TIME. SERVER AUTOMATIC STOPPED.")
                        print(Fore.GREEN + "If you wanna restart? Please " + Fore.RED + "don't touch" + Fore.GREEN + " anything.")
                        print(Fore.RED + f"==========================================================")
                        print()
                        time.sleep(5)
                    except Exception as e:
                        print(Fore.RED + f"Error occurred: {e}")
                        print(Fore.YELLOW + "Back to menu...")
                        time.sleep(1)
                        break
                else:
                    error_msg = f"File jar {current_version} does not exist at path {server_path_abs}"
                    log_error(error_msg)
                    send_webhook(config.get("webhook_url"), error_msg, "Error", 0xFF0000, read_latest_error())
                    print(Fore.YELLOW + error_msg)
                    break
            else:
                error_msg = "No Paper file found. Please configure a Paper version."
                log_error(error_msg)
                send_webhook(config.get("webhook_url"), error_msg, "Warning", 0xFFFF00, read_latest_error())
                print(Fore.YELLOW + error_msg)
                break
    else:
        error_msg = "Server path not set. Please configure config."
        log_error(error_msg)
        send_webhook(config.get("webhook_url"), error_msg, "Error", 0xFF0000, read_latest_error())
        print(error_msg)

def check_server_path():
    config = load_config()
    server_path = config.get('server_path', '')
    if not server_path or not os.path.exists(server_path):
        print(Fore.RED + "Server path not set or does not exist. Please choose a folder with PaperMC JAR file.")
        new_server_path = select_server_folder()
        if not check_papermc_folder(new_server_path):
            print(Fore.RED + "The selected folder does not contain a PaperMC JAR file. Do you want download it? (y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                change_paper_version()
            else:
                print(Fore.RED + "Back to main menu...")
                return menu()
        config['server_path'] = new_server_path
        save_config(config)
    elif not check_papermc_folder(server_path):
        print(Fore.RED + "The server path does not contain a PaperMC JAR file. Please choose another folder.")
        new_server_path = select_server_folder()
        config['server_path'] = new_server_path
        save_config(config)
    return config

def check_for_update_auto_mode():
    print(Fore.CYAN + "Checking for updates...")
    current_version = get_current_version(config['server_path'])
    if current_version:
        current_version_match = re.match(r'paper-(\d+\.\d+)-(\d+)\.jar', current_version) or re.match(r'paper-(\d+\.\d+\.\d+)-(\d+)\.jar', current_version)
        if current_version_match:
            current_version_number = current_version_match.group(1)
            current_build_number = int(current_version_match.group(2))
            version, build_number, file_name = get_latest_version_url(current_version_number)

            if version:
                latest_build_number = build_number
                if latest_build_number > current_build_number:
                    send_webhook(config.get("webhook_url"), f"Updating to new build {latest_build_number} from {current_build_number}", "Update Available", 0x00FFFF)
                    print(Fore.GREEN + f"Newer build available: {latest_build_number} (current: {current_build_number})")
                    delete_old_version(current_version)
                    download_latest_version(download_url_template.format(version=version, build_number=build_number, file_name=file_name), file_name)
                    send_webhook(config.get("webhook_url"), f"Updated to {file_name}", "Update Completed", 0x00FF00)
                else:
                    print(Fore.GREEN + "You are already using the latest version.")
            else:
                send_webhook(config.get("webhook_url"), "Failed to fetch the latest version URL.", "Error", 0xFF0000)
                print(Fore.RED + "Failed to fetch the latest version URL.")
    else:
        send_webhook(config.get("webhook_url"), "No current version found, nothing to update.", "Warning", 0xFFFF00)
        print(Fore.YELLOW + "No current version found, nothing to update.")

def download_latest_version(download_url, file_name):
    print(f"Downloading latest version from {download_url}...")
    response = requests.get(download_url)
    with open(os.path.join(config['server_path'], file_name), 'wb') as f:
        f.write(response.content)
    print(f"Download complete. Saved to {config['server_path']}/{file_name}")

def check_for_update():
    clear_terminal()
    versions = get_versions()
    if not versions:
        return
    
    minecraft_version = versions[-1]
    version, build_number, latest_version_file = get_latest_version_url(minecraft_version)
    if not version:
        return
    
    current_version = get_current_version(server_path=config['server_path'])
    
    if current_version == latest_version_file:
        print(Fore.GREEN + "====================================")
        print(Fore.GREEN + "You already have the latest version. Returning to menu...")
        print(Fore.GREEN + "====================================")
        time.sleep(3)
        return
    
    print(Fore.YELLOW + "=============================================================================")
    print(Fore.CYAN + f"New version available: " + Fore.MAGENTA + f"{latest_version_file}" + Fore.CYAN + ". Do you want to update? (" + Fore.GREEN + "yes" + Fore.CYAN + "/" + Fore.RED + "no" + Fore.CYAN + ")")
    print(Fore.YELLOW + "=============================================================================")
    user_input = input().strip().lower()

    if user_input in ['yes', 'y']:
        if current_version:
            print(Fore.GREEN + "====================================")
            print(Fore.RED + f"Deleting old version: " + Fore.YELLOW + f"{current_version}")
            delete_old_version(current_version)

        print(Fore.BLUE + f"Downloading latest version: " + Fore.MAGENTA + f"{latest_version_file}")
        print(Fore.GREEN + "====================================")
        download_latest_version(download_url_template.format(version=version, build_number=build_number, file_name=latest_version_file), latest_version_file)
        clear_terminal()
    else:
        print(Fore.YELLOW + "====================================")
        print(Fore.YELLOW + "Update skipped. Returning to menu...")
        print(Fore.YELLOW + "====================================")
        time.sleep(3)

def add_indent(text, indent_length):
    lines = text.split('\n')
    if len(lines) > 1:
        first_line = lines[0]
        rest_lines = [ ' ' * indent_length + line for line in lines[1:] ]
        return '\n'.join([first_line] + rest_lines)
    return text

def select_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Select Server Folder")
    return folder_path

def change_paper_version():
    def validate_server_path():
        server_path = config.get('server_path', "")
        if not server_path or not os.path.exists(server_path):
            print(Fore.RED + "Server path is not set or invalid.")
            print(Fore.CYAN + "Please select the folder where your PaperMC server is located.")
            new_path = select_folder()
            if new_path and os.path.exists(new_path):
                config['server_path'] = new_path
                save_config(config)
                print(Fore.GREEN + f"Server path updated to: {new_path}")
                return new_path
            else:
                print(Fore.RED + "No valid folder selected. Returning to main menu.")
                return None
        return server_path

    clear_terminal()
    versions = get_versions()
    if not versions:
        return

    server_path = validate_server_path()
    if not server_path:
        return

    clear_terminal()
    print(Fore.MAGENTA + text_art)
    S = (Fore.RED + "<===== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ======>")
    x = S.center(150)
    print(x)
    print("")
    print("")
    print("")
    print(Fore.CYAN + "Available Minecraft versions:")
    for idx, version in enumerate(versions, 1):
        print(Fore.YELLOW + f"{idx}." + Fore.GREEN + f" Minecraft" + Fore.CYAN + f" {version}")

    try:
        choice = int(input(Fore.WHITE + "Type " + Fore.YELLOW + "'yellow'" + Fore.WHITE + " number to select Minecraft version" + Fore.RED + " '0 = Back to main menu'" + Fore.WHITE + ": " + Fore.YELLOW))
        if choice == 0:
            return
        if choice < 1 or choice > len(versions):
            print(Fore.RED + "Invalid choice.")
            return

        clear_terminal()
        selected_version = versions[choice - 1]
        builds = get_builds_for_version(selected_version)
        if not builds:
            print(Fore.RED + "No builds available for the selected version.")
            return

        clear_terminal()
        print(Fore.MAGENTA + text_art)
        S = (Fore.RED + "<===== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ======>")
        x = S.center(150)
        print(x)
        print("")
        print("")
        print("")
        print(Fore.CYAN + "Available builds:")
        print("Please wait a moment for the changelog to be fetched...")
        print("")

        build_summaries = []
        for build in builds:
            build_number = build['build']
            message = get_changelog_for_build(selected_version, build_number)
            build_summaries.append((build, message))

        for idx, (build, message) in enumerate(build_summaries, 1):
            build_number = build['build']
            print(Fore.YELLOW + f"{idx}. " + Fore.GREEN + f"Paper Build " + Fore.CYAN + f"{build_number}")
            if message:
                indented_message = add_indent(message.strip(), 17)
                print(Fore.YELLOW + f"    - Changelog: " + Fore.WHITE + indented_message)
            else:
                print(Fore.YELLOW + "    - Changelog: " + GRAY + ITALIC + "No changes" + RESET)

        choice = int(input(Fore.WHITE + "Type " + Fore.YELLOW + "'yellow'" + Fore.WHITE + " number to select Paper build" + Fore.RED + " '0 = Back to main menu'" + Fore.WHITE + ": " + Fore.YELLOW))
        if choice == 0:
            return
        if choice < 1 or choice > len(build_summaries):
            print(Fore.RED + "Invalid choice.")
            return

        selected_build, message = build_summaries[choice - 1]
        build_number = selected_build['build']
        file_name = f"paper-{selected_version}-{build_number}.jar"
        download_url = download_url_template.format(version=selected_version, build_number=build_number, file_name=file_name)

        clear_terminal()
        print(Fore.MAGENTA + text_art)
        S = (Fore.RED + "<===== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ======>")
        x = S.center(150)
        print(x)
        print("")
        print("")

        if message:
            print(Fore.CYAN + "Changelog for build " + Fore.GREEN + f"{build_number}" + Fore.CYAN + ":")
            indented_message = add_indent(message.strip(), 0)
            print(Fore.WHITE + indented_message)
        else:
            print(Fore.CYAN + "Changelog for build " + Fore.GREEN + f"{build_number}" + Fore.CYAN + ":")
            print(GRAY + ITALIC + "No changes")

        print("")
        print("")
        print(Fore.CYAN + f"Do you want to download build " + Fore.GREEN + f"{build_number}" + Fore.CYAN + f" for Minecraft version" + Fore.GREEN + f" {selected_version}" + Fore.CYAN + f"? (" + Fore.GREEN + "yes" + Fore.CYAN + "/" + Fore.RED + "no" + Fore.CYAN + ")")
        user_input = input().strip().lower()

        if user_input in ['yes', 'y']:
            current_version = get_current_version(server_path)
            if current_version:
                print(Fore.YELLOW + f"Deleting old version: " + Fore.RED + f"{current_version}")
                delete_old_version(current_version)

            print(Fore.BLUE + f"Downloading selected version:" + Fore.GREEN + f" {file_name}")
            download_latest_version(download_url, file_name)
            print(Fore.GREEN + f"Version updated to:" + Fore.YELLOW + f" {file_name}")
            clear_terminal()
        else:
            clear_terminal()
            print(Fore.YELLOW + "Update skipped. Returning to menu.")
    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a number.")

def get_changelog_for_build(version, build_number):
    changelog_url = f"https://papermc.io/api/v2/projects/paper/versions/{version}/builds/{build_number}"
    try:
        response = requests.get(changelog_url)
        if response.status_code == 200:
            data = response.json()
            changes = data.get("changes", [])
            messages = [change.get("message", "").strip() for change in changes]
            return '\n'.join(messages)
    except requests.RequestException as e:
        print(Fore.RED + f"Error fetching changelog: {e}")
        return None

def reload_script():
    clear_terminal()
    print(Fore.MAGENTA + text_art)
    S = (Fore.RED + "<===== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ======>")
    x = S.center(150)
    print(x)
    print("")
    print(Fore.CYAN + "Reloading script from GitHub...")

    script_url = "https://raw.githubusercontent.com/sang765/PaperMC-Manager/main/paper_manager.py"
    try:
        response = requests.get(script_url)
        response.raise_for_status()

        script_path = __file__
        with open(script_path, "w") as f:
            f.write(response.text)
        
        print(Fore.GREEN + "Script reloaded successfully.")
        print(Fore.CYAN + "Restarting the script...")
        os.execv(sys.executable, ['python'] + [script_path])
    
    except requests.RequestException as e:
        print(Fore.RED + f"Error reloading script: {e}")
    except IOError as e:
        print(Fore.RED + f"File error: {e}")

    input(Fore.CYAN + "Press Enter to return to menu.")

def configure_server():
    clear_terminal()
    global config
    while True:
        print(Fore.MAGENTA + text_art)
        S = (Fore.RED + "<===== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ======>")
        x = S.center(150)
        print(x)
        print("")
        print("")
        print("")
        print(Fore.CYAN + "Current configuration:")
        print(f"1. RAM: {config['ram']}")
        print(f"2. GUI Mode: {Fore.GREEN + 'Enabled' if not config['nogui'] else Fore.RED + 'Disabled'}")
        print(f"3. Server Path: {config.get('server_path', 'Not set')}")
        print(f"4. Webhook URL: {config.get('webhook_url', 'Not set')}")

        print(Fore.CYAN + "Options:")
        print("1. Set RAM Limit")
        print("2. Toggle GUI Mode")
        print("3. Set Server Path")
        print("4. Set Webhook URL")
        print("5. Save and Return to Menu")
        S = "====="
        x = S.center(60)
        print(x)

        choice = input("Select an option: ").strip()

        if choice == '1':
            clear_terminal()
            ram_limit = input("Enter RAM limit (e.g., 4, 6): ").strip()
            config["ram"] = f"{ram_limit}G"
        elif choice == '2':
            clear_terminal()
            config["nogui"] = not config["nogui"]
            print(f"GUI Mode is now {'Enabled' if not config['nogui'] else 'Disabled'}.")
        elif choice == '3':
            clear_terminal()
            server_path = select_server_folder()
            config["server_path"] = server_path
            print(f"Server path set to {server_path}.")
        elif choice == '4':
            clear_terminal()
            webhook_url = input("Enter Discord Webhook URL (or leave blank to disable): ").strip()
            config["webhook_url"] = webhook_url
            print(f"Webhook URL set to {webhook_url or 'Not set'}.")
        elif choice == '5':
            clear_terminal()
            save_config(config)
            print(Fore.YELLOW + "Configuration saved. Returning to menu...")
            time.sleep(3)
            break
        else:
            print(Fore.RED + "Invalid option. Please try again.")

def get_jdk_version():
    try:
        result = subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stderr

        if "Amazon Corretto" in output:
            runtime = "Amazon Corretto"
        elif "Zulu" in output:
            runtime = "Azul Zulu"
        elif "Temurin" in output:
            runtime = "Eclipse Adoptium's Temurin"
        elif "IBM Semeru" in output:
            runtime = "IBM Semeru Runtimes"
        elif "Microsoft" in output:
            runtime = "Microsoft Build of OpenJDK"
        elif "GraalVM" in output:
            runtime = "Oracle GraalVM"
        elif "Oracle" in output:
            runtime = "Oracle Java SE"
        elif "Red Hat" in output:
            runtime = "Red Hat build of OpenJDK"
        elif "SapMachine" in output:
            runtime = "SapMachine"
        elif "OpenJDK" in output:
            runtime = "OpenJDK"
        else:
            runtime = "Unknown JDK"

        version_line = next((line for line in output.splitlines() if "version" in line), None)
        if version_line:
            version = version_line.split('"')[1]
        else:
            version = "Unknown Version"

        return f"{runtime} {version}"
    except Exception as e:
        return f"Unable to detect JDK version: {e}"

def on_exit():
    global active_processes
    if any(proc.poll() is None for proc in active_processes):
        print(Fore.RED + "Detected active processes. Exiting gracefully...")

def menu():
    global active_processes
    active_processes = []
    
    while True:
        clear_terminal()
        print(Fore.MAGENTA + text_art)
        S = (Fore.RED + "<===== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ======>")
        x = S.center(150)
        print(x)
        print("")
        print("")
        print("OPTIONS:")
        S = (Fore.YELLOW + "1. Start Minecraft Server\n" +
             Fore.LIGHTGREEN_EX + "2. Check for Update Your Paper Build\n" +
             Fore.LIGHTRED_EX + "3. Change Paper Version\n" +
             Fore.CYAN + "4. Configure Server Settings\n" +
             Fore.LIGHTCYAN_EX + "5. Reload Script (Sync from GitHub raw)\n" +
             Fore.RED + "6. Quit")
        x = S.center(0)
        print(x)
        S = "====="
        x = S.center(60)
        print(x)
        
        print(f"\n{Fore.CYAN}Latest Changelog:")
        print(Fore.WHITE + "-" * 50)
        print(get_latest_changelog_from_github())
        print(Fore.WHITE + "-" * 50)
        
        choice = input("Select an option: ").strip()

        if choice == '1':
            clear_terminal()
            config = check_server_path()
            while True:
                print(Fore.MAGENTA + text_art)
                S = (Fore.RED + "<===== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ======>")
                x = S.center(150)
                print(x)
                print("")
                print("")
                print(f"{Fore.CYAN}Paper Directory: {Fore.GREEN}{config['server_path'] or Fore.RED + 'NONE'}")
                print(f"{Fore.CYAN}Curent File: {Fore.GREEN}{get_current_version(server_path = config['server_path']) or Fore.RED + 'NOT FOUND'}")
                jdk_version = get_jdk_version()
                print(f"{Fore.CYAN}JDK Runtime: {Fore.GREEN}{jdk_version or Fore.RED + 'NOT FOUND'}")
                print("")
                print("")
                print(Fore.CYAN + "Choose a start option:")
                print(Fore.YELLOW + "1. Start (Without Restart)")
                print(Fore.GREEN + "2. Start (Auto Restart)")
                print(f"3. Auto Update Paper: {Fore.GREEN + 'Enabled' if config.get('auto_update', False) else Fore.RED + 'Disabled'}")
                print(Fore.CYAN + "4. Go Back")
                S = "====="
                x = S.center(60)
                print(x)
                
                sub_choice = input("Select an option: ").strip()

                S = "====="
                x = S.center(60)
                print(x)

                if sub_choice == '1':
                    clear_terminal()
                    start_server_no_loop()
                elif sub_choice == '2':
                    clear_terminal()
                    start_server_loop()
                elif sub_choice == '3':
                    clear_terminal()
                    config["auto_update"] = not config.get("auto_update", False)
                    print(f"Auto Update is now {'Enabled' if config['auto_update'] else 'Disabled'}.")
                    save_config(config)
                elif sub_choice == '4':
                    break
                else:
                    print(Fore.RED + "Invalid option. Please select a valid option.")
        elif choice == '2':
            clear_terminal()
            check_for_update()
        elif choice == '3':
            clear_terminal()
            change_paper_version()
        elif choice == '4':
            clear_terminal()
            configure_server()
        elif choice == '5':
            clear_terminal()
            reload_script()
        elif choice == '6':
            on_exit()
            clear_terminal()
            print(Fore.MAGENTA + "Thank you for using this script. If you like this script don't forgot leave a star on " + GRAY + "GitHub" + RESET + Fore.MAGENTA + " page: " + GRAY + BOLD + "\nhttps://github.com/sang765/PaperMC-Manager" + RESET + Fore.MAGENTA + "\nGoodbye and have a nice day!")
            time.sleep(5)
            sys.exit()
        else:
            print(Fore.RED + "Invalid option. Please try again.")

if __name__ == "__main__":
    menu()
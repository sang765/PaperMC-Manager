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
from colorama import Fore
from threading import Timer, Thread
from colorama import init, Fore, Style

init(autoreset=True)

folder_path = "./"
projects_url = "https://api.papermc.io/v2/projects/paper"
builds_url_template = f"https://api.papermc.io/v2/projects/paper/versions/{{version}}/builds"
download_url_template = "https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build_number}/downloads/{file_name}"

config_file = "server_config.json"

default_config = {
    "ram": "4G",
    "nogui": True,
    "auto_update": False
}

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        save_config(default_config)
        return default_config

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
        print(Fore.GREEN + "Configuration saved successfully.")

config = load_config()

text_art = """
██████╗  █████╗ ██████╗ ███████╗██████╗     ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗ 
██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗    ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗
██████╔╝███████║██████╔╝█████╗  ██████╔╝    ██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝
██╔═══╝ ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗    ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗
██║     ██║  ██║██║     ███████╗██║  ██║    ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║  ██║
╚═╝     ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
"""

def clear_terminal():
    """Clear terminal content."""
    os.system('cls' if os.name == 'nt' else 'clear')

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

def get_latest_version_url(version):
    builds = get_builds_for_version(version)
    if not builds:
        return None, None
    
    latest_build = max(builds, key=lambda b: b['build'])
    build_number = latest_build['build']
    file_name = f"paper-{version}-{build_number}.jar"
    download_url = download_url_template.format(version=version, build_number=build_number, file_name=file_name)
    print(Fore.GREEN + f"URL fetched successfully: {Fore.YELLOW}{download_url}")
    return download_url, file_name

def get_current_version():
    for file in os.listdir(folder_path):
        match = re.match(r'paper-(\d+\.\d+)-(\d+)\.jar', file)
        if match:
            return file
    return None

def delete_old_version(file_name):
    os.remove(os.path.join(folder_path, file_name))

def download_latest_version(url, file_name):
    try:
        print(Fore.CYAN + f"Downloading the latest version from:" + Fore.YELLOW + f" {url}")
        response = requests.get(url)
        response.raise_for_status()
        with open(os.path.join(folder_path, file_name), 'wb') as file:
            file.write(response.content)
        print(Fore.GREEN + "Download completed.")
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to download the latest version. Error: {e}")

def run_server(file_name):
    ram = config["ram"]
    nogui_option = "" if not config["nogui"] else "nogui"
    return subprocess.Popen(['java', f'-Xmx{ram}', '-jar', file_name, nogui_option], cwd=folder_path)

def start_server_no_loop():
    clear_terminal()
    current_version = get_current_version()
    
    if config.get("auto_update", False):
        check_for_update_auto_mode()
    
    if current_version:
        print(Fore.GREEN + f"=================== STARTING SERVER ==================")
        print(Fore.GREEN + f"Starting server with: " + Fore.YELLOW + f"{current_version}")
        server_process = run_server(current_version)
        server_process.wait()
        print(Fore.RED + f"====================== SERVER STOPED =====================")
        print(Fore.YELLOW + "Back to menu...")
        time.sleep(1)
        menu()
    else:
        print(Fore.YELLOW + "No Paper file found. Please configure a Paper version.")

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

def start_server_loop():
    clear_terminal()
    while True:
        current_version = get_current_version()
        
        if config.get("auto_update", False):
            check_for_update_auto_mode()
        
        if current_version:
            print(Fore.GREEN + f"=================== STARTING SERVER ==================")
            print(Fore.GREEN + f"Starting server with: " + Fore.YELLOW + f"{current_version}")
            server_process = run_server(current_version)
            server_process.wait()
            print(Fore.RED + f"====================== SERVER STOPED =====================")
            print(Fore.RED + "Server has stopped. Kill terminal in 5 seconds to stop.")
            print(Fore.GREEN + "If you wanna restart? Please " + Fore.RED + "don't touch" + Fore.GREEN + " anything.")
            print(Fore.RED + f"==========================================================")
            print()
            time.sleep(5)
        else:
            print(Fore.YELLOW + "No Paper file found. Please configure a Paper version.")
            break

def handle_interrupt(signal, frame):
    print(Fore.RED + "Detected interruption signal. Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

def check_for_update_auto_mode():
    print(Fore.CYAN + "Checking for updates...")
    current_version = get_current_version()
    if current_version:
        current_version_match = re.match(r'paper-(\d+\.\d+)-(\d+)\.jar', current_version)
        current_version_number = current_version_match.group(1)
        current_build_number = int(current_version_match.group(2))
        download_url, file_name = get_latest_version_url(current_version_number)
        
        if download_url:
            latest_build_match = re.match(r'paper-(\d+\.\d+)-(\d+)\.jar', file_name)
            latest_build_number = int(latest_build_match.group(2))
            
            if latest_build_number > current_build_number:
                print(Fore.GREEN + f"Newer build available: {latest_build_number} (current: {current_build_number})")
                delete_old_version(current_version)
                download_latest_version(download_url, file_name)
                get_changelog_for_build(current_version_number, latest_build_number)
            else:
                print(Fore.GREEN + "You are already using the latest version.")
        else:
            print(Fore.RED + "Failed to fetch the latest version URL.")
    else:
        print(Fore.YELLOW + "No current version found, nothing to update.")

def check_for_update():
    clear_terminal()
    versions = get_versions()
    if not versions:
        return

    minecraft_version = versions[-1]
    latest_version_url, latest_version_file = get_latest_version_url(minecraft_version)
    if not latest_version_url:
        return

    current_version = get_current_version()

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
            print(Fore.YELLOW + f"Deleting old version: " + Fore.YELLOW + f"{current_version}")
            delete_old_version(current_version)

        print(Fore.BLUE + f"Downloading latest version: " + Fore.MAGENTA + f"{latest_version_file}")
        download_latest_version(latest_version_url, latest_version_file)
        clear_terminal()
    else:
        print(Fore.YELLOW + "====================================")
        print(Fore.YELLOW + "Update skipped. Returning to menu...")
        print(Fore.YELLOW + "====================================")
        time.sleep(3)

def change_paper_version():
    clear_terminal()
    versions = get_versions()
    if not versions:
        return
    
    clear_terminal()
    print(Fore.MAGENTA + text_art)
    print(Fore.RED + "========================================== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ==========================================")
    print("")
    print("")
    print("")
    print(Fore.CYAN + "Available Minecraft versions:")
    for idx, version in enumerate(versions, 1):
        print(Fore.YELLOW + f"{idx}." + Fore.GREEN + f" Minecraft" + Fore.CYAN + f" {version}")

    try:
        choice = int(input(Fore.WHITE + "Type " + Fore.YELLOW + "'yellow'" + Fore.WHITE + " number to select Minecraft version: " + Fore.YELLOW))
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
        print(Fore.RED + "========================================== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ==========================================")
        print("")
        print("")
        print("")
        print(Fore.CYAN + "Available builds:")
        print("Please wait a moment for the changelog to be fetched...")
        print("")
        
        build_summaries = []
        for build in builds:
            build_number = build['build']
            summary = get_changelog_for_build(selected_version, build_number)
            build_summaries.append((build, summary))
            
        for idx, (build, summary) in enumerate(build_summaries, 1):
            build_number = build['build']
            print(Fore.YELLOW + f"{idx}. " + Fore.GREEN + f"Paper Build " + Fore.CYAN + f"{build_number}")
            if summary:
                print(Fore.YELLOW + f"  - Changelog: " + Fore.WHITE + f"{summary}")
            else:
                print(Fore.YELLOW + "  - Changelog:" + Fore.RED + " No changelog available")

        choice = int(input(Fore.WHITE + "Type " + Fore.YELLOW + "'yellow'" + Fore.WHITE + " number to select Paper build version: " + Fore.YELLOW))
        if choice < 1 or choice > len(build_summaries):
            print(Fore.RED + "Invalid choice.")
            return
        
        selected_build, summary = build_summaries[choice - 1]
        build_number = selected_build['build']
        file_name = f"paper-{selected_version}-{build_number}.jar"
        download_url = download_url_template.format(version=selected_version, build_number=build_number, file_name=file_name)
        
        clear_terminal()
        print(Fore.MAGENTA + text_art)
        print(Fore.RED + "========================================== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ==========================================")
        print("")
        print("")
        
        if summary:
            print(Fore.CYAN + "Changelog for build " + Fore.GREEN + f"{build_number}" + Fore.CYAN + ":")
            print(Fore.WHITE + summary)
        else:
            print(Fore.RED + "No changelog available for this build.")
        
        print("")
        print("")
        print(Fore.CYAN + f"Do you want to download build " + Fore.GREEN + f"{build_number}" + Fore.CYAN + f" for Minecraft version" + Fore.GREEN + f" {selected_version}" + Fore.CYAN + f"? (yes/no)")
        user_input = input().strip().lower()
        
        if user_input in ['yes', 'y']:
            current_version = get_current_version()
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
    """
    Get changelog for the specified version and build number.
    """
    changelog_url = f"https://papermc.io/api/v2/projects/paper/versions/{version}/builds/{build_number}"
    try:
        response = requests.get(changelog_url)
        if response.status_code == 200:
           data = response.json()
           changes = data.get("changes", [])
        for change in changes:
            summary = change.get("summary", "")
            return summary
    except requests.RequestException as e:
        print(Fore.RED + f"Error fetching changelog: {e}")
        return None

def reload_script():
    clear_terminal()
    print(Fore.MAGENTA + text_art)
    print(Fore.RED + "========================================== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ==========================================")
    print("")
    print(Fore.CYAN + "Reloading script from GitHub...")

    script_url = "https://raw.githubusercontent.com/sang765/Paper-Manager/main/paper_manager.py"
    try:
        response = requests.get(script_url)
        response.raise_for_status()  # Check for HTTP errors

        # Write the content to the current script file
        script_path = __file__  # Path to the current script
        with open(script_path, "w") as f:
            f.write(response.text)
        
        print(Fore.GREEN + "Script reloaded successfully.")
        
        # Optional: Restart the script after reloading
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
        print(Fore.RED + "========================================== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ==========================================")
        print("")
        print("")
        print("")
        print(Fore.CYAN + "Current configuration:")
        print(f"1. RAM: {config['ram']}")
        print(f"2. GUI Mode: {Fore.GREEN + 'Enabled' if not config['nogui'] else Fore.RED + 'Disabled'}")
        print(f"3. Server Port: {config.get('port', 25565)}")
        print(f"4. Server IP: {config.get('ip', '')}")
        print(f"5. Max Players: {config.get('max_players', 20)}")
        print(f"6. Difficulty: {config.get('difficulty', 'normal')}")
        print(f"7. View Distance: {config.get('view_distance', 10)}")
        print(f"8. Allow Nether: {Fore.GREEN + 'Yes' if config.get('allow_nether', True) else Fore.RED + 'No'}")
        print(f"9. Spawn Animals: {Fore.GREEN + 'Yes' if config.get('spawn_animals', True) else Fore.RED + 'No'}")
        print(f"10. Spawn Monsters: {Fore.GREEN + 'Yes' if config.get('spawn_monsters', True) else Fore.RED + 'No'}")
        print(f"11. Max Build Height: {config.get('max_build_height', 256)}")
        print(f"12. Server Message: {config.get('server_message', 'Welcome to the server!')}")
        print(f"13. World Name: {config.get('world_name', 'world')}")
        print(f"14. Whitelist: {Fore.GREEN + 'Enabled' if config.get('whitelist', False) else Fore.RED + 'Disabled'}")
        print(f"15. Enable Command Blocks: {Fore.GREEN + 'Yes' if config.get('enable_command_blocks', True) else Fore.RED + 'No'}")
        print(f"16. Hardcore Mode: {Fore.GREEN + 'Yes' if config.get('hardcore', False) else Fore.RED + 'No'}")
        print(f"17. Allow Flight: {Fore.GREEN + 'Yes' if config.get('allow_flight', False) else Fore.RED + 'No'}")
        print(f"18. Online Mode: {Fore.GREEN + 'Enabled' if config.get('online_mode', True) else Fore.RED + 'Disabled'}")
        print(f"19. GC Options: {config.get('gc_options', '-XX:+UseG1GC')}")
        print(f"20. VM Options: {config.get('vm_options', '')}")

        print(Fore.CYAN + "Options:")
        print("1. Set RAM Limit")
        print("2. Toggle GUI Mode")
        print("3. Set Server Port")
        print("4. Set Server IP")
        print("5. Set Max Players")
        print("6. Set Difficulty")
        print("7. Set View Distance")
        print("8. Toggle Allow Nether")
        print("9. Toggle Spawn Animals")
        print("10. Toggle Spawn Monsters")
        print("11. Set Max Build Height")
        print("12. Set Server Message")
        print("13. Set World Name")
        print("14. Toggle Whitelist")
        print("15. Toggle Command Blocks")
        print("16. Toggle Hardcore Mode")
        print("17. Toggle Allow Flight")
        print("18. Toggle Online Mode")
        print("19. Set GC Options")
        print("20. Set VM Options")
        print("21. Save and Return to Menu")

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
            port = int(input("Enter server port: ").strip())
            config["port"] = port
        elif choice == '4':
            clear_terminal()
            ip = input("Enter server IP (leave blank for all IPs): ").strip()
            config["ip"] = ip
        elif choice == '5':
            clear_terminal()
            max_players = int(input("Enter maximum number of players: ").strip())
            config["max_players"] = max_players
        elif choice == '6':
            clear_terminal()
            difficulty = input("Enter difficulty (peaceful, easy, normal, hard): ").strip()
            if difficulty in ["peaceful", "easy", "normal", "hard"]:
                config["difficulty"] = difficulty
            else:
                print(Fore.RED + "Invalid difficulty. Defaulting to 'normal'.")
                config["difficulty"] = "normal"
        elif choice == '7':
            clear_terminal()
            view_distance = int(input("Enter view distance (default is 10): ").strip())
            config["view_distance"] = view_distance
        elif choice == '8':
            clear_terminal()
            config["allow_nether"] = not config.get("allow_nether", True)
            print(f"Allow Nether is now {'Enabled' if config['allow_nether'] else 'Disabled'}.")
        elif choice == '9':
            clear_terminal()
            config["spawn_animals"] = not config.get("spawn_animals", True)
            print(f"Spawn Animals is now {'Enabled' if config['spawn_animals'] else 'Disabled'}.")
        elif choice == '10':
            clear_terminal()
            config["spawn_monsters"] = not config.get("spawn_monsters", True)
            print(f"Spawn Monsters is now {'Enabled' if config['spawn_monsters'] else 'Disabled'}.")
        elif choice == '11':
            clear_terminal()
            max_build_height = int(input("Enter max build height (default is 256): ").strip())
            config["max_build_height"] = max_build_height
        elif choice == '12':
            clear_terminal()
            server_message = input("Enter server message: ").strip()
            config["server_message"] = server_message
        elif choice == '13':
            clear_terminal()
            world_name = input("Enter world name: ").strip()
            config["world_name"] = world_name
        elif choice == '14':
            clear_terminal()
            config["whitelist"] = not config.get("whitelist", False)
            print(f"Whitelist is now {'Enabled' if config['whitelist'] else 'Disabled'}.")
        elif choice == '15':
            clear_terminal()
            config["enable_command_blocks"] = not config.get("enable_command_blocks", True)
            print(f"Command Blocks are now {'Enabled' if config['enable_command_blocks'] else 'Disabled'}.")
        elif choice == '16':
            clear_terminal()
            config["hardcore"] = not config.get("hardcore", False)
            print(f"Hardcore Mode is now {'Enabled' if config['hardcore'] else 'Disabled'}.")
        elif choice == '17':
            clear_terminal()
            config["allow_flight"] = not config.get("allow_flight", False)
            print(f"Allow Flight is now {'Enabled' if config['allow_flight'] else 'Disabled'}.")
        elif choice == '18':
            clear_terminal()
            config["online_mode"] = not config.get("online_mode", True)
            print(f"Online Mode is now {'Enabled' if config['online_mode'] else 'Disabled'}.")
        elif choice == '19':
            clear_terminal()
            gc_options = input("Enter GC options (e.g., '-XX:+UseG1GC'): ").strip()
            config["gc_options"] = gc_options
        elif choice == '20':
            clear_terminal()
            vm_options = input("Enter VM options (e.g., '-Xmx4G -Xms2G'): ").strip()
            config["vm_options"] = vm_options
        elif choice == '21':
            clear_terminal()
            save_config(config)
            print(Fore.YELLOW + "Configuration saved. Returning to menu...")
            time.sleep(3)
            break
        else:
            print(Fore.RED + "Invalid option. Please try again.")

def on_exit():
    """Check and handle active processes before exiting."""
    global active_processes
    if any(proc.poll() is None for proc in active_processes):  # Check if any process is running
        print(Fore.RED + "Detected active processes. Exiting gracefully...")

def menu():
    global active_processes
    active_processes = []
    
    while True:
        clear_terminal()
        print(Fore.MAGENTA + text_art)
        print(Fore.RED + "========================================== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ==========================================")
        print("")
        print("")
        print("")
        print(Fore.CYAN + "Options:")
        print(Fore.YELLOW + "1. Start Minecraft Server")
        print(Fore.LIGHTGREEN_EX + "2. Check for Update Your Paper Build")
        print(Fore.LIGHTRED_EX + "3. Change Paper Version")
        print(Fore.CYAN + "4. Configure Server Settings")
        print(Fore.LIGHTCYAN_EX + "5. Reload Script (Sync from GitHub raw)")
        print(Fore.RED + "6. Quit (Please close window to exit if you use EXE version)")
        
        choice = input("Select an option: ").strip()

        if choice == '1':
            clear_terminal()
            while True:
                print(Fore.MAGENTA + text_art)
                print(Fore.RED + "========================================== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ==========================================")
                print("")
                print("")
                print("")
                print(Fore.CYAN + "Choose a start option:")
                print(Fore.YELLOW + "1. Start (Without Restart)")
                print(Fore.GREEN + "2. Start (Auto Restart)")
                print(f"3. Auto Update Paper: {Fore.GREEN + 'Enabled' if config.get('auto_update', False) else Fore.RED + 'Disabled'}")
                print(Fore.CYAN + "4. Go Back")
                
                sub_choice = input("Select an option: ").strip()

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
            on_exit()  # Call on_exit to handle active processes before quitting
            clear_terminal()
            print(Fore.MAGENTA + "Thank you for using this script. Goodbye!")
            sys.exit()
        else:
            print(Fore.RED + "Invalid option. Please try again.")


if __name__ == "__main__":
    menu()

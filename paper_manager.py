import os
import requests
import re
import subprocess
import time
import json
from colorama import init, Fore, Style

init(autoreset=True)

folder_path = "./"
projects_url = "https://api.papermc.io/v2/projects/paper"
builds_url_template = f"https://api.papermc.io/v2/projects/paper/versions/{{version}}/builds"
download_url_template = "https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build_number}/downloads/{file_name}"

config_file = "server_config.json"

default_config = {
    "ram": "4G",
    "nogui": True
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
        print(Fore.GREEN + f"Available versions: {versions}")
        return versions
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to fetch versions. Error: {e}")
        return []

def get_builds_for_version(version):
    try:
        print(Fore.CYAN + f"Fetching all builds for version {version}...")
        builds_url = builds_url_template.format(version=version)
        response = requests.get(builds_url)
        response.raise_for_status()
        builds_data = response.json()
        builds = builds_data['builds']
        if builds:
            print(Fore.GREEN + f"Available builds for version {version}: {[build['build'] for build in builds]}")
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
    print(Fore.GREEN + f"URL fetched successfully: {download_url}")
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
        print(Fore.CYAN + f"Downloading the latest version from: {url}")
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
    if current_version:
        print(Fore.GREEN + f"Starting server with version: {current_version}")
        server_process = run_server(current_version)
        server_process.wait()
        print(Fore.RED + "Server has stopped.")
    else:
        print(Fore.YELLOW + "No PaperMC file found. Please configure a PaperMC version.")

def start_server_loop():
    clear_terminal()
    while True:
        current_version = get_current_version()
        if current_version:
            print(Fore.GREEN + f"Starting server with version: {current_version}")
            server_process = run_server(current_version)
            server_process.wait()
            print(Fore.RED + "Server has stopped. Restarting in 5 seconds...")
            print(Fore.YELLOW + "If you don't want to restart the server, close the window or kill the terminal to stop the server without damaging data.")
            print(Fore.GREEN + "If you want to restart the server, please " + Fore.RED + "don't touch " + Fore.GREEN + "anything.")
            time.sleep(5)
        else:
            print(Fore.YELLOW + "No PaperMC file found. Please configure a PaperMC version.")
            time.sleep(5)

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
        print(Fore.GREEN + "You already have the latest version.")
        return
    
    print(Fore.CYAN + f"New version available: {latest_version_file}. Do you want to update? (yes/no)")
    user_input = input().strip().lower()
    
    if user_input in ['yes', 'y']:
        if current_version:
            print(Fore.YELLOW + f"Deleting old version: {current_version}")
            delete_old_version(current_version)
        
        print(Fore.BLUE + f"Downloading latest version: {latest_version_file}")
        download_latest_version(latest_version_url, latest_version_file)
        clear_terminal()
    else:
        print(Fore.YELLOW + "Update skipped. Returning to menu.")

def change_paper_version():
    clear_terminal()
    versions = get_versions()
    if not versions:
        return
    
    print(Fore.CYAN + "Available Minecraft versions:")
    for idx, version in enumerate(versions, 1):
        print(f"{idx}. {version}")

    try:
        choice = int(input("Select a Minecraft version (number): "))
        if choice < 1 or choice > len(versions):
            print(Fore.RED + "Invalid choice.")
            return
        
        selected_version = versions[choice - 1]
        builds = get_builds_for_version(selected_version)
        if not builds:
            return
        
        print(Fore.CYAN + f"Available builds for Minecraft version {selected_version}:")
        for idx, build in enumerate(builds, 1):
            print(f"{idx}. Build {build['build']}")
        
        choice = int(input("Select a build (number): "))
        if choice < 1 or choice > len(builds):
            print(Fore.RED + "Invalid choice.")
            return
        
        selected_build = builds[choice - 1]
        build_number = selected_build['build']
        file_name = f"paper-{selected_version}-{build_number}.jar"
        download_url = download_url_template.format(version=selected_version, build_number=build_number, file_name=file_name)
        
        print(Fore.CYAN + f"Do you want to download build {build_number} for Minecraft version {selected_version}? (yes/no)")
        user_input = input().strip().lower()
        
        if user_input in ['yes', 'y']:
            current_version = get_current_version()
            if current_version:
                print(Fore.YELLOW + f"Deleting old version: {current_version}")
                delete_old_version(current_version)
            
            print(Fore.BLUE + f"Downloading selected version: {file_name}")
            download_latest_version(download_url, file_name)
            clear_terminal()
        else:
            print(Fore.YELLOW + "Update skipped. Returning to menu.")
    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a number.")

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
        print(f"2. GUI Mode: {'Enabled' if not config['nogui'] else 'Disabled'}")
        
        print(Fore.CYAN + "Options:")
        print("1. Set RAM Limit")
        print("2. Toggle GUI Mode")
        print("3. Save and Return to Menu")

        choice = input("Select an option: ").strip()

        if choice == '1':
            ram_limit = input("Enter RAM limit (e.g., 4, 6): ").strip()
            config["ram"] = f"{ram_limit}G"
        elif choice == '2':
            config["nogui"] = not config["nogui"]
            print(f"GUI Mode is now {'Enabled' if not config['nogui'] else 'Disabled'}.")
        elif choice == '3':
            save_config(config)
            print(Fore.GREEN + "Configuration saved.")
            break
        else:
            print(Fore.RED + "Invalid option.")

def menu():
    while True:
        clear_terminal()
        print(Fore.MAGENTA + text_art)
        print(Fore.RED + "========================================== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ==========================================")
        print("")
        print("")
        print("")
        print(Fore.CYAN + "Options:")
        print(Fore.YELLOW + "1. Start Minecraft Server Without Restart")
        print(Fore.GREEN + "2. Start Minecraft Server With Auto Restart")
        print(Fore.LIGHTGREEN_EX + "3. Check for Update Your PaperMC Build")
        print(Fore.LIGHTRED_EX + "4. Change PaperMC Version")
        print(Fore.CYAN + "5. Configure Server Settings")
        print(Fore.RED + "6. Quit")
        choice = input("Select an option: ").strip()

        if choice == '1':
            clear_terminal()
            start_server_no_loop()
        elif choice == '2':
            clear_terminal()
            start_server_loop()
        elif choice == '3':
            clear_terminal()
            check_for_update()
        elif choice == '4':
            clear_terminal()
            change_paper_version()
        elif choice == '5':
            clear_terminal()
            configure_server()
        elif choice == '6':
            clear_terminal()
            print(Fore.MAGENTA + text_art)
            print(Fore.RED + "========================================== " + Fore.CYAN + "by " + Fore.GREEN + "sang765 " + Fore.YELLOW + "on " + Fore.WHITE + "GitHub" + Fore.RED + " ==========================================")
            print("")
            print("")
            print("")
            print(Fore.RED + "Thank for using this script, hope you enjoy and have a nice day. Bye!")
            time.sleep(5)
            exit()
        else:
            print(Fore.RED + "Invalid option. Please select a valid option.")

if __name__ == "__main__":
    menu()

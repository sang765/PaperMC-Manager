<div align="center">
  <img src="https://i.imgur.com/v27gUcx.png" alt="Paper Manager" width="100">
  <h1>PaperMC Manager</h1>
  <img src="https://ziadoua.github.io/m3-Markdown-Badges/badges/Python/python1.svg" alt="BetterDiscord" width="100">
  <img src="https://ziadoua.github.io/m3-Markdown-Badges/badges/Windows/windows1.svg" alt="BetterDiscord" width="120">
  <img src="https://ziadoua.github.io/m3-Markdown-Badges/badges/macOS/macos1.svg" alt="BetterDiscord" width="108">
  <img src="https://ziadoua.github.io/m3-Markdown-Badges/badges/Linux/linux2.svg" alt="BetterDiscord" width="93">
</div>

## Description

This script helps manage Minecraft servers using **[Paper](https://github.com/PaperMC/Paper)**. It provides features such as:
- Starting the Minecraft server without auto-restart
- Starting the Minecraft server with auto-restart
- Checking and updating to the latest PaperMC build
- Changing the PaperMC version
- Configuring server settings, including RAM limit and GUI mode

## Features

1. **Start Server Without Auto-Restart**
   - Start the Minecraft server without automatic restart when the server stops.

2. **Start Server With Auto-Restart**
   - Start the Minecraft server and automatically restart it after the server stops.

3. **Check for Updates**
   - Check and download the latest Paper build if available.

4. **Change PaperMC Version**
   - Select and download a specific Paper version from available builds.

5. **Configure Server**
   - Configure server settings, including RAM limit and GUI mode.

## Screenshot:
Main menu:
![image](https://i.imgur.com/HOPBWQz.png)
Start server:
![image](https://i.imgur.com/MMrtYbr.png)
Check for updates:
![image](https://i.imgur.com/lwGk71L.png)
Change version:
![image](https://i.imgur.com/b7ynEm3.png)
Configure server:
![image](https://i.imgur.com/xblw95w.png)
VSCode Preview:
![image](https://github.com/user-attachments/assets/5ce71df7-1c2b-432c-8bd4-bcc0f18c893e)

## Note Before Using
> [!NOTE]
>
> Please place **python** file or **exe** file to __root paper server folder__.
>
> **IMPORTANT**
> Please don't change the name for paper file (That 100% make the script broken.)


## Installation

### Python Installation

1. **Install Python and pip:**
   - Download Python from [python.org](https://www.python.org/downloads/) and install it.
   - Ensure Python is added to your PATH environment variable.

2. **Download source code and unzip to folder:**
   - Download the source code in release page `(or you can clone this repository with git)`.
   - Use any unzip tool like [7-Zip](https://www.7-zip.org/) or [WinRar](https://www.win-rar.com/) to unzip the source code to a folder. 

3. **Install Required Packages:**
   - Open a terminal window in address of the folder (or use "Open with Code" if you use VSCode).
   - Install the packages using:
   ```py
   pip install -r requirements.txt
   ```

4. **Run script**
   - Execute the script with:
   ```py
   python paper_manager.py
   ```

### Executable Installation
1. **Download the EXE Version:**

   - If you prefer not to use Python, you can download a pre-built EXE version from the project's release page or provided link.
2. **Run the EXE Version:**

   - Run the EXE file by double-clicking it or executing it from the command line.

## Note 
- This script is not affiliated with PaperMC team.
- If you see **PaperMC_Manager.exe** or **main.exe** of PaperMC Manager got malicious on [this](https://www.virustotal.com/gui/file/893fd96c0879418d6b7e75a2c88aafe48b70214e29e335388b619279101e6570)? Don't worry this executable **100% safe**. The reason this executable got malicious on VirusTotal because I use **pyinstall with UPX**.

![VT Test Image](assets/VT_Test.png)
import requests
import os

REPO_URL = "https://raw.githubusercontent.com/sang765/PaperMC-Manager/main/CHANGELOG.md"

LOCAL_PATH = "./CHANGELOG.md"

def sync_changelog():
    try:
        response = requests.get(REPO_URL)
        
        if response.status_code == 200:
            changelog_content = response.text
            
            with open(LOCAL_PATH, 'w', encoding='utf-8') as file:
                file.write(changelog_content)
            
            print(f"Sync completed CHANGELOG.md in {LOCAL_PATH}")
        else:
            print(f"Download error: HTTP {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Connect error: {e}")
    except IOError as e:
        print(f"Wirte fail: {e}")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(LOCAL_PATH), exist_ok=True)
    
    sync_changelog()
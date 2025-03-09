import os
import glob

CHANGELOG_DIR = "changelogs"
OUTPUT_FILE = os.path.join(CHANGELOG_DIR, "CHANGELOG.md")

def get_changelog_files():
    changelog_path = os.path.join(CHANGELOG_DIR, "changelog_v*.md")
    files = glob.glob(changelog_path)
    files.sort(reverse=True)
    return files

def update_changelogs():
    os.makedirs(CHANGELOG_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        outfile.write("# Changelog\n\n")
        outfile.write("All notable changes to this project will be documented in this file.\n\n")

        changelog_files = get_changelog_files()
        if not changelog_files:
            print(f"Không tìm thấy file changelog_v*.md nào trong {CHANGELOG_DIR}")
            outfile.write("No changelog entries yet.\n")
            return

        for file in changelog_files:
            with open(file, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n\n")
            print(f"Đã gộp {os.path.basename(file)} vào {OUTPUT_FILE}")

    print(f"Đã cập nhật thành công {OUTPUT_FILE}")

if __name__ == "__main__":
    update_changelogs()
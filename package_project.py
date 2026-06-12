"""
Package the 3D Graphics Final Project into a ZIP file on the Desktop.
"""
import os
import zipfile
import subprocess

PROJECT_DIR = r"C:\Users\Tunay\.gemini\antigravity\scratch\3d_graphics_final_project"
OUT_ZIP     = r"C:\Users\Tunay\Desktop\3D_Graphics_Final_Project_97294.zip"

# First: generate the presentation
print("[1/2] Generating presentation...")
result = subprocess.run(
    ["python", os.path.join(PROJECT_DIR, "create_final_presentation.py")],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("ERROR: ", result.stderr)

# Files to include in the ZIP
files_to_zip = [
    os.path.join(PROJECT_DIR, "main.py"),
    os.path.join(PROJECT_DIR, "README.md"),
    os.path.join(PROJECT_DIR, "3D_Graphics_Final_Presentation.pptx"),
    os.path.join(PROJECT_DIR, "presentation_speech.md"),
]

print(f"\n[2/2] Creating ZIP: {OUT_ZIP}")
with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for filepath in files_to_zip:
        if os.path.exists(filepath):
            arcname = os.path.basename(filepath)
            zf.write(filepath, arcname)
            print(f"   [+] Added: {arcname}")
        else:
            print(f"   [!] Missing: {filepath}")

print(f"\n[DONE] ZIP saved to Desktop: {OUT_ZIP}")
print("\nContents:")
with zipfile.ZipFile(OUT_ZIP, "r") as zf:
    for info in zf.infolist():
        size_kb = info.file_size / 1024
        print(f"   - {info.filename:45s}  {size_kb:8.1f} KB")

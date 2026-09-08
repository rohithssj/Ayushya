import os
import json

base_dir = r"d:\SIH"
manifest_path = os.path.join(base_dir, "data", "metadata", "resource_manifest.json")

with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

print(f"Total manifest records: {len(manifest)}")

missing_files = []
for entry in manifest:
    full_path = os.path.join(base_dir, entry["path"].replace("/", os.sep))
    if not os.path.exists(full_path):
        missing_files.append(entry["path"])
    else:
        file_size = os.path.getsize(full_path)
        print(f"VERIFIED: {entry['path']} ({file_size} bytes)")

if missing_files:
    print(f"FAILED: {len(missing_files)} files missing!")
else:
    print("ALL 28 FILES SUCCESSFULLY VERIFIED IN TARGET LOCATIONS!")

#!/usr/bin/env python3
"""Batch screenshot all style sample HTML files using CDP."""
import os, time, json, subprocess, base64, sys

SAMPLES_DIR = "/home/clawbot/.openclaw/workspace/skills/my-design/demos/style_samples"
OUT_DIR = "/home/clawbot/.openclaw/workspace/skills/my-design/demos/style_screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

# Kill any existing server
subprocess.run(["pkill", "-f", "python3.*8765"], capture_output=True)
time.sleep(0.5)

# Start HTTP server
proc = subprocess.Popen(
    ["python3", "-m", "http.server", "8765", "--directory", SAMPLES_DIR],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
time.sleep(1)

# Get HTML files sorted
html_files = sorted([f for f in os.listdir(SAMPLES_DIR) if f.endswith('.html')])
print(f"Found {len(html_files)} style samples")

import requests

# Use Playwright-like approach via the browser tool's CDP
CDP_PORT = 18800

def cdp_request(target_id, method, params=None):
    """Send CDP command via the browser tool's HTTP endpoint."""
    # We'll use a simpler approach: use the browser tool via openclaw
    pass

# Actually, let's use a simpler approach: open each in the browser and take screenshots
# We'll write a JSON manifest for the screenshot process
manifest = []
for f in html_files:
    style_id = f.split('_')[1]
    url = f"http://localhost:8765/{f}"
    manifest.append({"id": style_id, "file": f, "url": url})

manifest_path = os.path.join(OUT_DIR, "manifest.json")
with open(manifest_path, 'w') as mf:
    json.dump(manifest, mf, ensure_ascii=False, indent=2)

print(f"Manifest written to {manifest_path}")
print(f"HTTP server running on port 8765 (PID {proc.pid})")
print(f"Sample URLs:")
for m in manifest[:3]:
    print(f"  {m['url']}")
print(f"  ... and {len(manifest)-3} more")

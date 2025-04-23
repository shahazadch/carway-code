#!/usr/bin/env python3
"""
Script to organize static files for CarWay project.
This script identifies the static files referenced in the templates
and copies them to a new directory structure.
"""

import os
import re
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'
OUTPUT_DIR = BASE_DIR / 'static_used'

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Regular expression to find static references in templates
static_pattern = re.compile(r"{%\s*static\s+['\"](.+?)['\"]")

# Track files already processed
processed_files = set()

def find_static_references(template_dir):
    static_files = set()
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                template_path = os.path.join(root, file)
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Find all static references
                        for match in static_pattern.finditer(content):
                            static_path = match.group(1).strip()
                            static_files.add(static_path)
                except UnicodeDecodeError:
                    print(f"Warning: Could not read {template_path} as text")
    return static_files

def copy_static_files(static_files):
    for static_file in static_files:
        src_path = STATIC_DIR / static_file
        dest_path = OUTPUT_DIR / static_file
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # Copy file if it exists
        if os.path.exists(src_path):
            if static_file not in processed_files:
                shutil.copy2(src_path, dest_path)
                processed_files.add(static_file)
                print(f"Copied {static_file}")
        else:
            print(f"Warning: {static_file} not found in static directory")
            
def copy_css_references(static_files):
    """Copy CSS files and their referenced resources (fonts, images)"""
    css_files = [f for f in static_files if f.endswith('.css')]
    css_resource_pattern = re.compile(r'url\([\'"]?(.+?)[\'"]?\)')
    
    for css_file in css_files:
        css_path = STATIC_DIR / css_file
        if not os.path.exists(css_path):
            continue
            
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find all URL references
                for match in css_resource_pattern.finditer(content):
                    resource_path = match.group(1).strip()
                    # Skip data URLs and absolute URLs
                    if resource_path.startswith('data:') or resource_path.startswith('http'):
                        continue
                        
                    # Resolve path relative to CSS file
                    css_dir = os.path.dirname(css_file)
                    if resource_path.startswith('/'):
                        # Absolute path within static
                        full_resource_path = resource_path.lstrip('/')
                    else:
                        # Relative path
                        full_resource_path = os.path.normpath(os.path.join(css_dir, resource_path))
                        
                    # Copy the resource
                    src_path = STATIC_DIR / full_resource_path
                    dest_path = OUTPUT_DIR / full_resource_path
                    
                    if os.path.exists(src_path) and full_resource_path not in processed_files:
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(src_path, dest_path)
                        processed_files.add(full_resource_path)
                        print(f"Copied resource: {full_resource_path}")
        except UnicodeDecodeError:
            print(f"Warning: Could not read {css_path} as text")

def copy_service_worker_files():
    """Copy the service worker files"""
    sw_files = ['service-worker.js', 'js/sw-register.js', 'manifest.json']
    for sw_file in sw_files:
        src_path = STATIC_DIR / sw_file
        dest_path = OUTPUT_DIR / sw_file
        
        if os.path.exists(src_path):
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)
            processed_files.add(sw_file)
            print(f"Copied service worker file: {sw_file}")

def main():
    print("Finding static file references in templates...")
    static_files = find_static_references(TEMPLATES_DIR)
    
    print(f"Found {len(static_files)} static file references")
    for file in sorted(static_files):
        print(f" - {file}")
        
    print("\nCopying static files...")
    copy_static_files(static_files)
    
    print("\nCopying CSS referenced resources...")
    copy_css_references(static_files)
    
    print("\nCopying service worker files...")
    copy_service_worker_files()
    
    print(f"\nDone! Copied {len(processed_files)} files to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
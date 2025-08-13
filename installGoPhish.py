#!/usr/bin/env python3
import subprocess
import shutil
import os
import json

def run_command(command):
    """Run a shell command and print its output live."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {e}")

def is_installed(pkg_name):
    """Check if a command exists on the system."""
    return shutil.which(pkg_name) is not None

def update_gophish_config(config_path, cert_path, key_path):
    """Modify the GoPhish config.json file."""
    with open(config_path, "r") as f:
        config = json.load(f)

    # Modify admin server to allow remote access
    config["admin_server"]["listen_url"] = "0.0.0.0:3333"

    # Modify phishing server to use provided cert and key
    config["phish_server"]["listen_url"] = "0.0.0.0:443"
    config["phish_server"]["use_tls"] = True
    config["phish_server"]["cert_path"] = cert_path
    config["phish_server"]["key_path"] = key_path

    # Save changes
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    print(f"[INFO] Updated {config_path}")

def main():
    print("[INFO] Updating package lists...")
    run_command("sudo apt update")

    print("[INFO] Upgrading packages...")
    run_command("sudo apt upgrade -y")

    # Install unzip if not installed
    if is_installed("unzip"):
        print("[INFO] unzip is already installed. Skipping installation.")
    else:
        print("[INFO] Installing unzip...")
        run_command("sudo apt install unzip -y")

    # Install certbot if not installed
    if is_installed("certbot"):
        print("[INFO] certbot is already installed. Skipping installation.")
    else:
        print("[INFO] Installing certbot...")
        run_command("sudo apt install certbot -y")

    # Install GoPhish
    print("[INFO] Installing GoPhish...")
    os.makedirs("gophish", exist_ok=True)
    os.chdir("gophish")
    run_command("wget https://github.com/gophish/gophish/releases/download/v0.12.1/gophish-v0.12.1-linux-64bit.zip")
    run_command("unzip -o gophish-v0.12.1-linux-64bit.zip")
    run_command("chmod +x gophish")

    # Ask user for cert and key paths with defaults
    cert_path_input = input("Enter the full path for phish_server certificate [default: example.crt]: ").strip()
    if not cert_path_input:
        cert_path_input = "example.crt"

    key_path_input = input("Enter the full path for phish_server key [default: example.key]: ").strip()
    if not key_path_input:
        key_path_input = "example.key"

    # Update GoPhish config.json
    config_file = os.path.join(os.getcwd(), "config.json")
    if os.path.exists(config_file):
        update_gophish_config(config_file, cert_path_input, key_path_input)
    else:
        print("[WARNING] config.json not found. Skipping configuration update.")

    # Start GoPhish automatically
    print("[INFO] Starting GoPhish...")
    subprocess.Popen(["./gophish"], cwd=os.getcwd())
    print("[INFO] GoPhish started. Admin UI available at https://<your-server-ip>:3333")

    print("[INFO] All tasks completed.")

if __name__ == "__main__":
    main()

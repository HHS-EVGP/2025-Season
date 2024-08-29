import subprocess

def restart_now():
    # Command to restart the Raspberry Pi
    restart_command = ["sudo", "reboot"]

    # Execute the restart command
    subprocess.run(restart_command, check=True)

if __name__ == "__main__":
    restart_now()
import subprocess

def shutdown_now():
    # Command to restart the Raspberry Pi
    restart_command = ["sudo", "shutdown", "-h", "now"]

    # Execute the restart command
    subprocess.run(restart_command, check=True)

if __name__ == "__main__":
    shutdown_now()
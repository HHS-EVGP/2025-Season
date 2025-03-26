import subprocess

def start_service(service_name):
    try:
        # Starting the service
        subprocess.run(["sudo systemctl start", service_name], check=True)
        print(f"{service_name} successfully started.")
    except subprocess.CalledProcessError as e:
        # An error occurred while trying to start the service
        print(f"Failed to start {service_name}: {e}")

if __name__ == "__main__":
    start_service("transmit.service")

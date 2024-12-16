from django.utils import timezone
from monitoring.models import MonitoringCheck, MonitoringResult
import requests
from django.contrib.auth.models import User
import subprocess
import requests
import time

def monitor_websites_for_user(user_id):
    user = User.objects.get(id=user_id)
    checks = MonitoringCheck.objects.filter(user=user)
    now = timezone.now().replace(tzinfo=None)
    for check in checks:
        try:
            last_checked_naive = check.last_checked.replace(tzinfo=None) if check.last_checked else None
            time_difference = (now - last_checked_naive).total_seconds() / 60 if last_checked_naive else check.check_interval
            
            # Perform the check only if the interval has passed
            if time_difference >= check.check_interval:
                url_to_check = check.url
                locations = check.location_to_check.lower().split(',')  # Fetch and split multiple locations

                for location in locations:
                    location = location.strip()  # Clean any extra spaces
                    
                    # Check if the location has a corresponding VPN configuration
                    if location in VPN_CONFIGS:
                        ovpn_file_path = VPN_CONFIGS[location]
                        vpn_process = connect_vpn(ovpn_file_path)

                        try:
                            # Perform the URL check
                            response = requests.get(url_to_check, timeout=5)
                            status = response.status_code
                            response_time = response.elapsed.total_seconds() * 1000  # in milliseconds

                            # Save the monitoring result for each location
                            MonitoringResult.objects.create(
                                monitoring_check=check,
                                user=check.user,
                                url=check.url,
                                status=status,
                                response_time=response_time,
                                checked_at=timezone.now(),
                                location_checked=location
                            )
                        except Exception as e:
                            # Save result with error status
                            MonitoringResult.objects.create(
                                monitoring_check=check,
                                user=check.user,
                                url=check.url,
                                status='Error',
                                response_time=0,
                                checked_at=timezone.now(),
                                location_checked=location
                            )
                            print(f"Error checking URL {url_to_check} for location {location}: {e}")
                        finally:
                            # Disconnect from the VPN
                            disconnect_vpn(vpn_process)
                    else:
                        print(f"No VPN configuration found for location: {location}")

                # Update the last checked timestamp
                check.last_checked = timezone.now()
                check.save()
        except Exception as e:
            print(f"Error in monitoring for user {user_id}: {e}")


VPNBOOK_USERNAME = "vpnbook"  # Replace with VPNBook username
VPNBOOK_PASSWORD = "c28hes5"  # Replace with VPNBook password

# Define available VPN configuration files by location
VPN_CONFIGS = {
    "ca": "monitoring/vpnbook/vpnbook-ca149-udp25000.ovpn",
    "us": "monitoring/vpnbook/vpnbook-us16-udp25000.ovpn",
    "uk": "monitoring/vpnbook/vpnbook-uk16-udp25000.ovpn"
}

def connect_vpn(ovpn_file_path):
    """Connect to VPN using the specified configuration file."""
    print(f"Connecting to VPN with config: {ovpn_file_path}")
    process = subprocess.Popen(
        ['openvpn', '--config', ovpn_file_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.stdin.write(f"{VPNBOOK_USERNAME}\n{VPNBOOK_PASSWORD}\n".encode())
    process.stdin.flush()
    time.sleep(10)  # Adjust time for connection setup
    return process

def disconnect_vpn(vpn_process):
    """Disconnect from the VPN."""
    vpn_process.terminate()
    vpn_process.wait()
    print("VPN disconnected.")
import os
import socket
from urllib.parse import urlparse
from django.utils import timezone
from monitoring.models import MonitoringCheck, MonitoringResult, SSLDomainStatus
import requests
from django.contrib.auth.models import User
import subprocess
import requests
import time
import ssl
import socket
import whois
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email_notification(to_email, subject, content):
    try:
        message = Mail(
            from_email=os.environ.get("EMAIL"),
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"Email sent to {to_email}. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

def generate_email_body(url, http_status=None, ping_status=None, port_status=None):
    messages = []

    if http_status in [404, 'Error']:
        messages.append(f"<li>HTTP Status: {http_status} for URL: {url}</li>")
    if ping_status == 'Unreachable':
        messages.append(f"<li>Ping Status: {ping_status} for URL: {url}</li>")
    if port_status == 'Closed':
        messages.append(f"<li>Port Status: {port_status} for URL: {url}</li>")

    if messages:
        return f"""
        <p>Hello,</p>
        <p>We detected the following issues with your website <strong>{url}</strong>:</p>
        <ul>
            {''.join(messages)}
        </ul>
        <p>Please take immediate action to resolve these issues.</p>
        <p>Thank you,<br>Your Website Monitoring Team</p>
        """
    return None

def extract_host_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.hostname

def monitor_for_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        checks = MonitoringCheck.objects.filter(user=user)
        now = timezone.now().replace(tzinfo=None)

        for check in checks:
            try:
                last_checked_naive = check.last_checked.replace(tzinfo=None) if check.last_checked else None
                time_difference = (now - last_checked_naive).total_seconds() / 60 if last_checked_naive else check.check_interval
                
                if time_difference >= check.check_interval:
                    url_to_check = check.url
                    host = extract_host_from_url(url_to_check)
                    port = check.port

                    locations = check.location_to_check.lower().split(',')
                    for location in locations:
                        location = location.strip()
                        
                        if location in VPN_CONFIGS:
                            ovpn_file_path = VPN_CONFIGS[location]
                            vpn_process = connect_vpn(ovpn_file_path)

                            try:
                                # HTTP Monitoring
                                try:
                                    response = requests.get(url_to_check, timeout=5)
                                    http_status = response.status_code
                                    response_time = response.elapsed.total_seconds() * 1000  # ms
                                except Exception as e:
                                    http_status = 'Error'
                                    response_time = 0
                                    print(f"HTTP check failed for {url_to_check}: {e}")

                                # Ping Monitoring
                                try:
                                    ping_response = subprocess.run(
                                        ['ping', '-n', '1', host],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        timeout=5
                                    )
                                    ping_status = 'Reachable' if ping_response.returncode == 0 else 'Unreachable'
                                except Exception as e:
                                    ping_status = 'Error'
                                    print(f"Ping check failed for {host}: {e}")

                                # Port Monitoring
                                try:
                                    with socket.create_connection((host, port), timeout=5) as s:
                                        port_status = 'Open'
                                except Exception as e:
                                    port_status = 'Closed'
                                    print(f"Port check failed for {host}:{port}: {e}")

                                # Save or update the monitoring result
                                MonitoringResult.objects.create(
                                    monitoring_check=check,
                                    user=check.user,
                                    url=check.url,
                                    location_checked=location,
                                    status=http_status,
                                    response_time=response_time,
                                    ping_status=ping_status,
                                    port_status=port_status,
                                    checked_at=timezone.now(),
                                )

                                # Check failure conditions and send email
                                if http_status in [404, 'Error'] or ping_status == 'Unreachable' or port_status == 'Closed':
                                    subject = f"ALERT: Issues detected with {check.name_of_check}"
                                    content = generate_email_body(
                                        url=check.url,
                                        http_status=http_status,
                                        ping_status=ping_status,
                                        port_status=port_status
                                    )
                                    if content:
                                        send_email_notification(check.contact_detail, subject, content)
                            finally:
                                disconnect_vpn(vpn_process)
                        else:
                            print(f"No VPN configuration found for location: {location}")

                    # Update the last checked timestamp
                    check.last_checked = timezone.now()
                    check.save()
            except Exception as e:
                print(f"Error processing check for {check.url}: {e}")
    except Exception as e:
        print(f"Error in monitoring for user {user_id}: {e}")

VPNBOOK_USERNAME = "vpnbook"
VPNBOOK_PASSWORD = "c28hes5"

VPN_CONFIGS = {
    "ca": "monitoring/vpnbook/vpnbook-ca149-udp25000.ovpn",
    "us": "monitoring/vpnbook/vpnbook-us16-udp25000.ovpn",
    "uk": "monitoring/vpnbook/vpnbook-uk16-udp25000.ovpn"
}

def connect_vpn(ovpn_file_path):
    process = subprocess.Popen(
        ['openvpn', '--config', ovpn_file_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.stdin.write(f"{VPNBOOK_USERNAME}\n{VPNBOOK_PASSWORD}\n".encode())
    process.stdin.flush()
    time.sleep(10)
    return process

def disconnect_vpn(vpn_process):
    vpn_process.terminate()
    vpn_process.wait()


def get_ssl_expiry_date(hostname):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            expiry_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
            return expiry_date

def get_domain_expiry_date(domain):
    try:
        domain_info = whois.whois(domain)
        expiry_date = domain_info.expiration_date
        # Handle cases where expiry_date might be a list
        if isinstance(expiry_date, list):
            expiry_date = expiry_date[0]
        return expiry_date
    except Exception as e:
        print(f"Error fetching domain expiry for {domain}: {e}")
        return None

def check_and_store_ssl_domain_status(user_id):
    user = User.objects.get(id=user_id)
    checks = MonitoringCheck.objects.filter(user=user)
    for check in checks:
        try:
            hostname = check.url.split("//")[-1].split("/")[0]  # Extract hostname
            ssl_expiry = get_ssl_expiry_date(hostname)
            domain_expiry = get_domain_expiry_date(hostname)

            status_entry, created = SSLDomainStatus.objects.get_or_create(monitoring_check=check)

            status_entry.ssl_status = "Active" if ssl_expiry > datetime.now() else "Expired"
            status_entry.ssl_expiry_date = ssl_expiry
            status_entry.domain_expiry_date = domain_expiry
            status_entry.last_checked = datetime.now()

            status_entry.save()

            print(f"Updated SSL and domain status for {check.name_of_check}.")

        except Exception as e:
            print(f"Error checking SSL/Domain for {check.name_of_check}: {e}")

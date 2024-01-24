#!/bin/bash

# Check for root privileges
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Update and upgrade the system
apt update && apt full-upgrade -y

# Install necessary packages
apt install hostapd dnsmasq -y

# Disable services to prevent them from starting after a reboot
systemctl stop hostapd
systemctl stop dnsmasq

# Set up a static IP for wlan0
cat >> /etc/dhcpcd.conf <<EOL

interface wlan0
static ip_address=192.168.0.10/24
nohook wpa_supplicant
EOL

# Configure the DHCP server (dnsmasq)
cat > /etc/dnsmasq.conf <<EOL
interface=wlan0
dhcp-range=192.168.0.11,192.168.0.30,255.255.255.0,24h
EOL

# Configure the access point host software (hostapd)
cat > /etc/hostapd/hostapd.conf <<EOL
interface=wlan0
driver=nl80211
ssid=RaspberryPi
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=Admin123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOL

# Tell the system where to find the configuration file
sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

# Enable IP forwarding
sed -i 's|#net.ipv4.ip_forward=1|net.ipv4.ip_forward=1|' /etc/sysctl.conf

# Add a masquerade for outbound traffic on eth0
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Save the iptables rule
sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Install iptables-persistent to save rules on boot
apt-get install iptables-persistent -y

# Apply changes
systemctl unmask hostapd
systemctl enable hostapd
systemctl start hostapd
systemctl start dnsmasq

echo "Wi-Fi Router setup is complete. Please reboot the system."


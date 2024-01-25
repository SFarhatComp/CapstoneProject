#!/bin/bash

# Check for root privileges
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Stop and disable hostapd and dnsmasq services
systemctl stop hostapd
systemctl disable hostapd
systemctl stop dnsmasq
systemctl disable dnsmasq

# Remove static IP configuration for wlan0
sed -i '/interface wlan0/,/nohook wpa_supplicant/d' /etc/dhcpcd.conf

# Restore the original DHCP server configuration
mv /etc/dnsmasq.conf.orig /etc/dnsmasq.conf 2>/dev/null || echo "Original dnsmasq config not found. Skipping."

# Restore the original hostapd configuration
mv /etc/hostapd/hostapd.conf.orig /etc/hostapd/hostapd.conf 2>/dev/null || echo "Original hostapd config not found. Skipping."

# Remove NAT configuration for wlan0
iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Save the iptables rule removal
sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Restart networking services
service dhcpcd restart


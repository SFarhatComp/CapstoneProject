#!/bin/bash

LOGFILE="/var/log/setup_ap.log"
exec > >(tee -a $LOGFILE) 2>&1

echo "[$(date)] --- Script Start ---"

echo "[$(date)] Backing up existing configuration files..."
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
sudo cp /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.backup
sudo cp /etc/sysctl.d/routed-ap.conf /etc/sysctl.d/routed-ap.conf.backup
sudo iptables-save > /etc/iptables/rules.v4.backup

echo "[$(date)] Updating and upgrading the system..."
sudo apt update && sudo apt upgrade -y

echo "[$(date)] Installing hostapd..."
sudo apt install hostapd -y
sudo systemctl unmask hostapd
sudo systemctl enable hostapd

echo "[$(date)] Installing dnsmasq..."
sudo apt install dnsmasq -y

echo "[$(date)] Installing netfilter-persistent and iptables-persistent..."
sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent

echo "[$(date)] Configuring static IP for wlan0 and restarting dhcpcd..."
echo "interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant" | sudo tee /etc/dhcpcd.conf
sudo systemctl restart dhcpcd

echo "[$(date)] Enabling IP forwarding..."
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/routed-ap.conf

echo "[$(date)] Setting up NAT..."
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo netfilter-persistent save

echo "[$(date)] Configuring dnsmasq and restarting it..."
echo "interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan" | sudo tee /etc/dnsmasq.conf
sudo systemctl restart dnsmasq

echo "[$(date)] Unblocking wlan and configuring hostapd..."
sudo rfkill unblock wlan
echo "country_code=CA
interface=wlan0
ssid=RaspberryPI
hw_mode=g
channel=7
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=Admin123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP" | sudo tee /etc/hostapd/hostapd.conf
sudo systemctl restart hostapd

echo "[$(date)] Setup complete. Rebooting in 5 seconds..."
sleep 5

sudo reboot
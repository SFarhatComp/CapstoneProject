#!/bin/bash

LOGFILE="/var/log/revert_ap.log"
exec > >(tee -a $LOGFILE) 2>&1

echo "[$(date)] --- Script Start ---"

echo "[$(date)] Stopping services..."
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

echo "[$(date)] Restoring backups..."
sudo mv /etc/dhcpcd.conf.backup /etc/dhcpcd.conf
sudo mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf
sudo mv /etc/hostapd/hostapd.conf.backup /etc/hostapd/hostapd.conf
sudo mv /etc/sysctl.d/routed-ap.conf.backup /etc/sysctl.d/routed-ap.conf
sudo iptables-restore < /etc/iptables/rules.v4.backup

echo "[$(date)] Disabling hostapd..."
sudo systemctl disable hostapd

echo "[$(date)] Restarting networking services..."
sudo service networking restart

echo "[$(date)] Reversion complete. A reboot is recommended."

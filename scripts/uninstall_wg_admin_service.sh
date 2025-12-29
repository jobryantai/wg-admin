#!/bin/bash

sudo systemctl stop wg-admin
sudo systemctl disable wg-admin
sudo rm /etc/systemd/system/wg-admin.service
sudo systemctl daemon-reload
sudo systemctl reset-failed


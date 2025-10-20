#!/bin/bash

# Inicia ngrok
xterm -e bash -c "ngrok http 5000; exec bash" &

# Inicia OpenVPN dentro da pasta certa
#xterm -e bash -c "cd /home/gustavo/cyberghost-openvpn && sudo openvpn --config openvpn.ovpn; exec bash" &

# Inicia OpenVPN Surfshark
xterm -e bash -c "cd ~/surfshark_ovpn && sudo openvpn --config selected.ovpn --auth-user-pass login.txt; exec bash" &


export FLASK_APP=/${HOME}/Desktop/automacao-python/automacao_app

# Inicia Flask
xterm -e bash -c "flask run; exec bash" &

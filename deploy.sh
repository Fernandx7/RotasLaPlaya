#!/bin/bash
set -e

echo "Atualizando código..."
git pull origin main

echo "Ativando venv..."
source venv/bin/activate

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Reiniciando serviço..."
sudo systemctl restart flaskcoletas.service

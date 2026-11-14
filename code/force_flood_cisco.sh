#!/bin/bash

TARGET_IP="192.168.2.10"

# LIMPEZA: Remove qualquer resqucio de floods anteriores
sudo pkill -f "ping -f" 2>/dev/null

echo "[0s] Experimento IP SLA iniciado. Trfego normal..."
echo "Aguardando 15 segundos..."
sleep 15

echo "[15s] INJETANDO CONGESTIONAMENTO (Ping Flood do Host-3 para $TARGET_IP)..."
# O "&" joga o ping para background, permitindo que o script continue contando o tempo
sudo ping -f -s 65000 $TARGET_IP > /dev/null 2>&1 &
FLOOD_PID=$!

echo "Rede degradada (Flood Ativo). Aguardando 30 segundos..."
sleep 30

echo "[45s] REMOVENDO CONGESTIONAMENTO (Parando o Ping Flood)..."
sudo kill -9 $FLOOD_PID 2>/dev/null
sudo pkill -f "ping -f" 2>/dev/null

echo "Teste concludo! Trfego normalizado."

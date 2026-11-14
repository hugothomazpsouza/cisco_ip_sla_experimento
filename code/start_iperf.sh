#!/bin/bash
echo "Iniciando 10 servidores iperf3 em background..."
for i in {0..9}; do
	    iperf3 -s -p $((5001 + i)) -D
    done
    echo "Servidores iniciados com sucesso nas portas 5001-5010."
    ss -tunlp | grep iperf3

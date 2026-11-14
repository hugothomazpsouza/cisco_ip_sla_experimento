#!/bin/bash

TARGET_IP="192.168.2.10"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CSV_FILE="experimento_cisco_ipsla_${TIMESTAMP}.csv"

echo "Iniciando coleta de mtricas REAIS para $TARGET_IP..."
echo "Gerando o arquivo: $CSV_FILE"

# CABEALHO CRU: Apenas o que o ambiente legado consegue fornecer
echo "timestamp,latencia_ms" > "$CSV_FILE"

timeout 60 ping -O -D -i 0.05 "$TARGET_IP" | awk -v csv="$CSV_FILE" '
BEGIN {
    OFS = ",";
}
{
    ts = $1;
    gsub(/\[|\]/, "", ts);

    if ($0 ~ /time=/) {
        match($0, /time=[0-9.]+/);
        lat_str = substr($0, RSTART+5, RLENGTH-5);
        lat_ms = lat_str + 0.0;

        # Salva apenas timestamp e latncia nua e crua
        print ts, lat_ms >> csv;
    }
    else if ($0 ~ /no answer yet/) {
        # Pacote perdido: Timestamp exato, latncia nula (NaN)
        print ts, "NaN" >> csv;
        print "[" ts "] Pacote Perdido!" > "/dev/stderr"
    }
}'

echo "Teste concludo! CSV gerado refletindo as limitaes do Cisco IP SLA." 

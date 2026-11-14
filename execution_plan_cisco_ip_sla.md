## 2. Sequência de Execução de Cada Rodada (60 Segundos)

Abra os **3 terminais lado a lado** e execute exatamente nesta ordem:

### Passo 1 — Host-2 (`192.168.2.10`): Abrir receptores `iperf3`

```bash
sudo ./start_iperf.sh
```

### Passo 2 — Host-1 (`192.168.1.10`): Iniciar tráfego uRLLC + coleta ICMP

```bash
python3 urllc_traffic.py & ./coleta_ping_cisco.sh
```

_(Imediatamente após dar `Enter`, mude para o terminal do Host-3)._

### Passo 3 — Host-3 (Atacante): Disparar o script de falha

```bash
sudo ./force_flood_cisco.sh
```

---

## 3. Encerramento e Conferência Pós-Teste

Quando o `coleta_ping_cisco.sh` finalizar (após 60s):

**1. Parar processos em background:**

- **No Host-1:**
  ```bash
  killall python3
  ```
- **No Host-2:**
  ```bash
  killall iperf3
  ```

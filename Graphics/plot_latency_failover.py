import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregar Dados Reais do CSV
df = pd.read_csv('experimento_cisco_ipsla_20261114_004930.csv')
df['timestamp'] = df['timestamp'].astype(float)

# 2. Converter o Tempo Relativo para MILISSEGUNDOS (* 1000)
start_time = df['timestamp'].min()
df['time_rel_ms'] = (df['timestamp'] - start_time) * 1000

# 3. Extrair os valores EXATOS do CSV
nans = df[df['latencia_ms'].isna()]
last_ok_before_ms = df[df['timestamp'] < nans['timestamp'].min()]['time_rel_ms'].max()
first_ok_after_ms = df[df['timestamp'] > nans['timestamp'].max()]['time_rel_ms'].min()
downtime_ms = first_ok_after_ms - last_ok_before_ms

# 4. Criação do Gráfico
fig, ax = plt.subplots(figsize=(12, 6))

# Filtros para Pacotes Normais (<= 1000ms) e Degradados (> 1000ms)
normal_mask = df['latencia_ms'] <= 1000
degraded_mask = df['latencia_ms'] > 1000

# Linha de fundo muito leve conectando os pontos
ax.plot(df['time_rel_ms'], df['latencia_ms'], color='#2980b9', linewidth=0.8, alpha=0.4, zorder=1)

# Plotando pacotes normais e degradados separadamente (conforme legenda)
ax.scatter(df.loc[normal_mask, 'time_rel_ms'], df.loc[normal_mask, 'latencia_ms'], 
           color='#4c4cff', s=20, label='Normal Packets (<= 1000ms)', zorder=2, alpha=0.9)
ax.scatter(df.loc[degraded_mask, 'time_rel_ms'], df.loc[degraded_mask, 'latencia_ms'], 
           color='#ffa500', s=25, label='Degraded Packets (> 1000ms)', zorder=3, alpha=1.0)

# Linha Horizontal de Threshold (1 segundo / 1000 ms)
ax.axhline(y=1000, color='red', linestyle='--', linewidth=2.5, label='Threshold (1000 ms)', zorder=4)

# Destaque Visual (Downtime) preenchido
ax.axvspan(last_ok_before_ms, first_ok_after_ms, color='#e74c3c', alpha=0.15)

# Linhas Verticais de Demarcação 
ax.axvline(x=last_ok_before_ms, color='grey', linestyle=':', linewidth=2.5, label='Congestion Start (Approx)')
ax.axvline(x=last_ok_before_ms, color='orange', linestyle='--', linewidth=2, label='Threshold Detection')
ax.axvline(x=first_ok_after_ms, color='green', linestyle='-', linewidth=2.5, label=f'Failover / Convergence (+{int(downtime_ms)}ms)')

# Colocando APENAS os tempos exatos nas linhas
ax.text(last_ok_before_ms - 500, ax.get_ylim()[1] * 0.9, f'{int(last_ok_before_ms)} ms', color='orange', ha='right', fontweight='bold', fontsize=12)
ax.text(first_ok_after_ms + 500, ax.get_ylim()[1] * 0.9, f'{int(first_ok_after_ms)} ms', color='green', ha='left', fontweight='bold', fontsize=12)

# Formatação Exata dos Eixos
ax.set_title('Graph 01: Latency Behavior in Cisco IP SLA Environment', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Relative Time (milliseconds)', fontsize=14, fontweight='bold')
ax.set_ylabel('Latency (ms)', fontsize=14, fontweight='bold')
ax.grid(True, linestyle=':', alpha=0.7)

# Legenda - No canto superior direito
ax.legend(loc='upper right', fontsize=11)

# Limites de visualização
ax.set_ylim(-50, df['latencia_ms'].max() * 1.3) 
ax.set_xlim(-1000, df['time_rel_ms'].max() + 1000)

plt.tight_layout()
plt.savefig('./experiment01/graphic_plot_latency_failover.png', dpi=300)
plt.show() 

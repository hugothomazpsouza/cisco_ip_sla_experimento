import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Estilo global limpo para artigo IEEE (coluna dupla)
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 9.5,
})

# 1. Carregar Dados Reais do CSV
df = pd.read_csv('./experiment01/experimento_cisco_ipsla_20261114_004930.csv')
df['timestamp'] = df['timestamp'].astype(float)

# 2. Converter o Tempo Relativo para MILISSEGUNDOS (* 1000)
start_time = df['timestamp'].min()
df['time_rel_ms'] = (df['timestamp'] - start_time) * 1000

# 3. Extrair os valores EXATOS do CSV
nans = df[df['latencia_ms'].isna()]
last_ok_before_ms = df[df['timestamp'] < nans['timestamp'].min()]['time_rel_ms'].max()
first_ok_after_ms = df[df['timestamp'] > nans['timestamp'].max()]['time_rel_ms'].min()
downtime_ms = first_ok_after_ms - last_ok_before_ms

# 4. Criação do Gráfico (proporção ideal para 1 coluna IEEE)
fig, ax = plt.subplots(figsize=(6.0, 3.6))

normal_mask = df['latencia_ms'] <= 1000
degraded_mask = df['latencia_ms'] > 1000

# Linha de fundo suave
ax.plot(df['time_rel_ms'], df['latencia_ms'], color='#5dade2', linewidth=0.9, alpha=0.45, zorder=1)

# Pacotes normais e degradados
ax.scatter(
    df.loc[normal_mask, 'time_rel_ms'], df.loc[normal_mask, 'latencia_ms'],
    color='#3b5bdb', s=18, label=r'Normal ($\leq 1000$ ms)', zorder=2, alpha=0.85
)
ax.scatter(
    df.loc[degraded_mask, 'time_rel_ms'], df.loc[degraded_mask, 'latencia_ms'],
    color='#f08c00', s=26, label=r'Degraded ($> 1000$ ms)', zorder=3
)

# Linha horizontal de threshold
ax.axhline(y=1000, color='#e03131', linestyle='--', linewidth=1.6, label='Threshold (1000 ms)', zorder=4)

# Faixa de indisponibilidade (downtime) + linhas de início e convergência
ax.axvspan(
    last_ok_before_ms, first_ok_after_ms,
    color='#e03131', alpha=0.14,
    label=f'Outage / Failover ({int(downtime_ms)} ms)', zorder=0
)
ax.axvline(x=last_ok_before_ms, color='#e67700', linestyle='--', linewidth=1.4, zorder=4)
ax.axvline(x=first_ok_after_ms, color='#2b8a3e', linestyle='-', linewidth=1.6, zorder=4)

# Limites dos eixos (definidos ANTES das anotações de texto)
y_max = df['latencia_ms'].max() * 1.25
ax.set_ylim(-60, y_max)
ax.set_xlim(-1000, df['time_rel_ms'].max() + 1000)

# Limita a quantidade de ticks no eixo X para não encavalar os valores em ms
ax.xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))

# Anotações limpas dos instantes exatos em ms
ax.text(
    last_ok_before_ms - 450, y_max * 0.86, f'{int(last_ok_before_ms)} ms',
    color='#d9480f', ha='right', va='center', fontweight='bold', fontsize=8.5
)
ax.text(
    first_ok_after_ms + 450, y_max * 0.86, f'{int(first_ok_after_ms)} ms',
    color='#2b8a3e', ha='left', va='center', fontweight='bold', fontsize=8.5
)

# Rótulos dos eixos em ms (sem título interno)
ax.set_xlabel('Relative Time (ms)', fontweight='bold')
ax.set_ylabel('Latency (ms)', fontweight='bold')

# Estética clean: sem bordas superior/direita e grade discreta
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linestyle='--', linewidth=0.6, alpha=0.35)

# Legenda limpa no canto superior direito
ax.legend(loc='upper right', frameon=True, framealpha=0.92, edgecolor='#dee2e6')

plt.tight_layout()
plt.savefig('graphic_plot_latency_failover.png', dpi=300, bbox_inches='tight')
plt.savefig('graphic_plot_latency_failover.pdf', bbox_inches='tight')
plt.show()
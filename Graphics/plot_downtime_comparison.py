import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Estilo global idêntico aos gráficos Cisco IP SLA e P4/ONT (coluna dupla IEEE)
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 9.5,
})

# Proporção consistente com os demais gráficos (mesma largura = mesma escala de fonte)
fig, ax = plt.subplots(figsize=(6.0, 3.2))

# Pequeno deslocamento no eixo Y para evitar sobreposição total das linhas
y_cisco_up = 1.04
y_cisco_down = 0.02
y_p4_up = 0.96
y_p4_down = 0.0

# Coordenadas Cisco IP SLA (4223.6 ms)
cisco_x = [-500, 0, 0, 4223.6, 4223.6, 5000]
cisco_y = [y_cisco_up, y_cisco_up, y_cisco_down, y_cisco_down, y_cisco_up, y_cisco_up]

# Coordenadas P4/ONT (290.6 ms)
p4_x = [-500, 0, 0, 290.6, 290.6, 5000]
p4_y = [y_p4_up, y_p4_up, y_p4_down, y_p4_down, y_p4_up, y_p4_up]

# Sombreamento sutil nas janelas de indisponibilidade
ax.axvspan(0, 4223.6, ymin=0.08, ymax=0.78, color='#868e96', alpha=0.10, zorder=0)
ax.axvspan(0, 290.6, ymin=0.08, ymax=0.72, color='#3b5bdb', alpha=0.18, zorder=1)

# Linhas de estado
ax.plot(cisco_x, cisco_y, color='#6c757d', linewidth=2.0, linestyle='--', label='Cisco IP SLA', zorder=2)
ax.plot(p4_x, p4_y, color='#3b5bdb', linewidth=2.2, linestyle='-', label='P4/ONT (uRLLC)', zorder=3)

# Anotações limpas dentro das janelas de downtime
ax.text(
    290.6 + 120, 0.26, 'P4/ONT\n290.6 ms',
    color='#3b5bdb', ha='left', va='center', fontweight='bold', fontsize=9.5
)
ax.text(
    4223.6 / 2, 0.56, 'Cisco IP SLA\n4223.6 ms',
    color='#495057', ha='center', va='center', fontweight='bold', fontsize=9.5
)

# Limites dos eixos (espaço superior reservado para a legenda sem sobrepor as linhas)
ax.set_xlim(-500, 5000)
ax.set_ylim(-0.12, 1.38)

# Ticks limpos
ax.set_yticks([0, 1])
ax.set_yticklabels(['0 (Down)', '1 (Up)'])
ax.xaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))

# Rótulos dos eixos (sem título interno; usar \caption no LaTeX)
ax.set_xlabel('Time (ms)', fontweight='bold')
ax.set_ylabel('SLA State', fontweight='bold')

# Estética clean
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, axis='x', linestyle='--', linewidth=0.6, alpha=0.35)

# Legenda posicionada antes do savefig (no original estava depois e não saía na imagem)
ax.legend(
    loc='upper right',
    ncol=2,
    frameon=True,
    framealpha=0.92,
    edgecolor='#dee2e6',
    columnspacing=1.0,
    handletextpad=0.5
)

plt.tight_layout()
plt.savefig('graphic_plot_downtime_comparison.png', dpi=300, bbox_inches='tight')
plt.savefig('graphic_plot_downtime_comparison.pdf', bbox_inches='tight')
plt.show()
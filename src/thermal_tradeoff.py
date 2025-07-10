import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import toml
import subprocess
import simulation
import matplotlib.cm as cm
from pydantic import BaseModel
import tomllib  # Use 'import tomli' for Python < 3.11

class ThermalConfig(BaseModel):
    n_samples    : int
    cutoff_low   : float 
    cutoff_high  : float 
    p_0          : float 
    q_0          : float
    d_sail       : float
    t_f          : float 

# Load TOML
with open("input/_thermal_tradeoff.toml", "rb") as f:
    data = tomllib.load(f)

cf = ThermalConfig(**data)
print(cf)

cmap = cm.get_cmap('Set1')

compute = True
figsize = (4.2, 1.8)

cutoff_frequencies = np.linspace(cf.cutoff_low, cf.cutoff_high, cf.n_samples)  # Normalized to Nd:YAG

output = "results/"
l = simulation.Launch()
l.multilayer = simulation.Reflector.M1

l.alpha2 = 1.0
l.mode = "delay"
l.p_0 = cf.p_0
l.t_f = cf.t_f
# 3e6 for short, 3e9 for long. Medium: 1e9
l.q_0 = 3e6
l.d_sail = 100
l.compile()

P_list = []
q_list = []
Q_list = []
T_list = []

for cutoff_frequency in cutoff_frequencies:
    l.cutoff_frequency = cutoff_frequency
    l.file = f'cutoff_{cutoff_frequency:.2f}.csv'
    if compute:
        l.write_config('input/_config.toml')
        l.run()
        l.plot_dynamics(na = f'_{cutoff_frequency:.2f}')
    # l.plot_spectrum(threshold=0.001, na = f'_{cutoff_frequency:.2f}')
    dd = pd.read_csv('results/' + l.file)
    P_list.append(dd['P'])
    q_list.append(dd['q'])
    Q_list.append(dd['Q'])
    T_list.append(dd['T'])
    print(f"cut: {cutoff_frequency:>10} | max Q: {np.max(dd['Q']):>10}, max T: {np.max(dd['T']):>10}")

Q_max = [np.max(Q) for Q in Q_list]
T_max = [np.max(T) for T in T_list]

fig, ax1 = plt.subplots(figsize=figsize)
color1 = 'tab:blue'
ax1.plot(cutoff_frequencies, Q_max, marker='o', linestyle='-', markersize = 4, color=color1, label='Max Q')
ax1.set_ylabel(r'$\Delta v/c$', color=color1)
ax1.set_ylim(0, 1.1 * np.max(Q_list))
ax1.tick_params(axis='y', labelcolor=color1)

# Shared x-axis
ax1.set_xlabel(r'$\omega_c/\omega_0$')
# ax1.ticklabel_format(style='sci', axis='x', scilimits=(3, 0))

# Second axis: T_max
ax2 = ax1.twinx()
color2 = 'tab:red'
ax2.plot(cutoff_frequencies, T_max, marker='d', linestyle='--', markersize = 4, color=color2, label='T_max')
ax2.set_ylim(0, 2000)
ax2.set_ylabel(r'$T$ [K]', color=color2)
ax2.tick_params(axis='y', labelcolor=color2)

# Optional: add grid or a combined legend
# ax1.grid(True)
# Combine legends from both axes if needed
# lines, labels = ax1.get_legend_handles_labels()
# lines2, labels2 = ax2.get_legend_handles_labels()
# ax1.legend(lines + lines2, labels + labels2, loc='best')

plt.tight_layout()
name = 'media/tradeoff_Q_T.pdf'
plt.savefig(name)
print(f"Saved plot to {name}")
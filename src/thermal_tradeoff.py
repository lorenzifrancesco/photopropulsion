import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import toml
import subprocess
import simulation
import matplotlib.cm as cm
cmap = cm.get_cmap('Set1')

compute = 1
figsize = (2.5, 2.3)
n_samples = 200
cutoff_frequencies = np.linspace(0.1, 0.9, n_samples)  # Normalized to Nd:YAG

output = "results/"
l = simulation.Launch()
l.multilayer = simulation.Reflector.M1 # Enable temperature computation 
l.alpha2 = 1.0
l.mode = "delay"
l.p_0 = 50e9
l.t_f = 500
l.d_sail = 100
# 3e6 for short, 3e9 for long. Medium: 1e9
l.q_0 = 1e6  # Change to 3e9 for long, 1e9 for medium
l.compile()

P_list = []
q_list = []
Q_list = []
T_list = []

for cutoff_frequency in cutoff_frequencies:
    l.cutoff_frequency = cutoff_frequency
    l.file = f'cutoff_{cutoff_frequency:.2f}.csv'
    if compute:
        l.write_config('input/config.toml')
        l.run()
    dd = pd.read_csv('results/' + l.file)
    P_list.append(dd['P'])
    q_list.append(dd['q'])
    Q_list.append(dd['Q'])
    T_list.append(dd['T'])


Q_max = [np.max(Q) for Q in Q_list]
T_max = [np.max(T) for T in T_list]

print(T_max)
plt.figure(figsize=figsize)
plt.plot(cutoff_frequencies, Q_max, 
    marker='o', linestyle='-', color='blue', label='Max Q')
plt.ylim(0, 1.1 * np.max(Q_list))
plt.xlabel(r'$f_C/f_0$')
# plt.yscale('log')
plt.ylabel(r'$\dot{q}(t_f)/c$')
plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))

# plt.legend(labelspacing=0.1, handletextpad = 0.2)  # Adjust these values to control spacing
plt.tight_layout()
name = 'media/tradeoff_Q.pdf'
plt.savefig(name)
print(f"Saved plot to {name}")

plt.figure(figsize=figsize)
plt.plot(cutoff_frequencies, T_max, 
    marker='o', linestyle='-', color='blue')
plt.xlabel(r'$f_C/f_0$')
# plt.yscale('log')
plt.ylabel(r'$T $ [K]')
plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))

# plt.legend(labelspacing=0.1, handletextpad = 0.2)  # Adjust these values to control spacing
plt.tight_layout()
name = 'media/tradeoff_T.pdf'
plt.savefig(name)
print(f"Saved plot to {name}")
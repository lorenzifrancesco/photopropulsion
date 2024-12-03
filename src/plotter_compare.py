import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import toml
import subprocess
import simulation
compute = 1

output = "results/"
l = simulation.Launch()
l.multilayer = simulation.Reflector.FLAT
l.alpha2 = 1.0
l.mode = "delay"
l.p_0 = 50e9
l.t_f = 500
# 3e6 for short, 3e9 for long
l.q_0 = 3e6
l.d_sail = 100
l.show()
l.compile()

configurations = [0.3, 0.6, 0.9, 1e-12]
df_list = []
P_list =  []
Q_list =  []
q_list =  []

for mode in ["delay", "lubin"]:
  l.mode = mode
  for i, alpha1 in enumerate(configurations):
    if compute:
      l.file = 'power.csv'
      l.alpha1 = alpha1
      l.write_config('input/config.toml')
      l.run()
    dd = pd.read_csv('results/'+l.file)
    df_list.append(dd)
    P_list.append(dd['P'])
    q_list.append(dd['q'])
    Q_list.append(dd['Q'])
print(len(P_list))
time = np.linspace(0, l.t_f, len(P_list[0]))/l.get_t_rel()
# time = np.linspace(0, l.t_f, len(P_list[0]))
file_type = '.pdf'
grid = False
lw0 = 1.4
ls_list = ["-", "--", ":", "-", "-", "-"]
color_list = ["c", "r", "g", "b", "y", "b"]

color_list = ['b', 'g', 'r', 'orange']
ls_list = [ '--', ':', '-.', '-']
labels = [ r"$\alpha=0.3$", r"$\alpha=0.6$", r"$\alpha=0.9$", r"$\alpha=0$"]
# color_list = color_list[::-1]
# ls_list = ls_list[::-1]
# labels = labels[::-1]

plt.figure(figsize=(3, 2.6))
max = 4
for i in range(max):
  # Plotting P
  if i == 3:
    lw = 1
  else:
    lw = lw0
  plt.semilogy(time, P_list[i], linestyle=ls_list[i], color=color_list[i], label=labels[i], linewidth=lw)
  plt.semilogy(time, 1/(1-(configurations[i]*l.alpha2)) * np.ones_like(P_list[i]), linestyle="-", color=color_list[:][i], linewidth=lw-0.5)
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel(r'$P/P_0$')
plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))
plt.grid(grid)
plt.legend(labelspacing=0.1)
plt.tight_layout()
plt.savefig('media/P_ratio_compare'+file_type)  # Save plot as PDF for LaTeX

plt.figure(figsize=(3, 2.6))
for i in range(max):
  # Plotting P
  if i == 3:
    lw = 1
  else:
    lw = lw0
  plt.plot(time, Q_list[i], linestyle=ls_list[i], color=color_list[i], label=labels[i], linewidth=lw)
  plt.plot(time, Q_list[i+4], linestyle="-", color=color_list[i], linewidth=lw-0.8)
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel(r'$\dot{q}/c$')
plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))
plt.grid(grid)
plt.legend(labelspacing=0.1, handletextpad = 0.2)  # Adjust these values to control spacing
plt.tight_layout()
plt.savefig('media/qdot_compare'+file_type)  # Save plot as PDF for LaTeX

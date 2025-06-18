import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import toml
import subprocess
import simulation
import matplotlib.cm as cm
cmap = cm.get_cmap('Set1')

compute = 0
plotting = ["p_compare", "qdot_compare"]
figsize = (2.5, 2.3)

output = "results/"
l = simulation.Launch()
l.multilayer = simulation.Reflector.FLAT
l.alpha2 = 1.0
l.mode = "delay"
l.p_0 = 50e9
l.t_f = 500
# 3e6 for short, 3e9 for long

for q_0_type in ["short", "long"]:
  if q_0_type == "short":
      l.q_0 = 3e6
  else:
      l.q_0 = 3e9

  l.d_sail = 100
  l.show()
  l.compile()

  configurations = [0.5, 0.7, 0.9, 1e-12]
  df_list = []
  P_list =  []
  Q_list =  []
  q_list =  []

  l.alpha1 = 1
  for mode in ["delay", "lubin"]:
    l.mode = mode
    for i, alpha2 in enumerate(configurations):
      l.file = q_0_type+'_'+f'{alpha2:.2f}'+'_'+str(mode)+'.csv'
      if compute:
        print(f">> Running with alpha1 = {alpha2} and mode = {mode}")
        l.alpha2 = alpha2
        l.write_config('input/config.toml')
        l.run()
      dd = pd.read_csv('results/'+l.file)
      df_list.append(dd)
      P_list.append(dd['P'])
      q_list.append(dd['q'])
      Q_list.append(dd['Q'])

  # Lubin (S) analytical result
  betas = np.linspace(0, 0.9, 200)
  time_samples = (((1 + betas) * (2 - betas) * (1 - betas**2)**(-1/2))/(1 - betas) - 2)/6

  # (S) numerical result
  l.mode = "lubin"
  l.alpha2 = 0.0
  l.file = 'power0.00_lubin.csv'
  l.write_config('input/config.toml')
  if True:
    print(f"Lubin S and mode={l.mode}")
    l.run()

  print(len(P_list))
  time = np.linspace(0, l.t_f, len(P_list[0]))/l.get_t_rel()
  file_type = '.pdf'
  grid = False
  lw0 = 1.4
  ls_list = ["-", "--", ":", "-", "-", "-"]
  color_list = ["c", "r", "g", "b", "y", "b"]

  color_list = [cmap(i) for i in (np.array([0.0, 0.33, 0.66, 1.0])-0.5)*0.5 + 0.5]
  color_list = ['b', 'g', 'r', 'orange']

  ls_list = [ '--', ':', '-.', '-']
  labels = [ r"$r=0.5$", r"$r=0.7$", r"$r=0.9$", r"$r=0$"]

  if "p_compare" in plotting:
    plt.figure(figsize=figsize)
    max = 4
    for i in range(max):
      if i == 3:
        lw = 1
      else:
        lw = lw0
      plt.semilogy(time, P_list[i]/(1/(1-(configurations[i]*l.alpha1)) * np.ones_like(P_list[i])), linestyle=ls_list[i], color=color_list[i], label=labels[i], linewidth=lw)
      # plt.semilogy(time, 1/(1-(configurations[i]*l.alpha2)) * np.ones_like(P_list[i]), linestyle="-", color=color_list[:][i], linewidth=lw-0.5)
    plt.xlabel(r'$t/t_{\mathrm{rel}}$')
    plt.ylabel(r'$P/P_{\mathrm{inst}}$')
    plt.xlim([0, np.max(time)])
    plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))
    plt.grid(grid)
    plt.legend(labelspacing=0.1)
    plt.tight_layout()
    name = 'media/P_compare'+'_'+q_0_type+file_type
    plt.savefig(name)
    print(f"Saved plot to {name}")

  if "qdot_compare" in plotting:
    plt.figure(figsize=figsize)
    for i in range(max):
      if i == 3:
        lw = 1
      else:
        lw = lw0
      plt.plot(time, Q_list[i], 
              linestyle=ls_list[i], color=color_list[i], label=labels[i], linewidth=lw)
      plt.plot(time, Q_list[i+4], 
              linestyle="-", color=color_list[i], linewidth=lw-0.8)
      amplification = (1-configurations[i])
      plt.scatter((time_samples * amplification)[::int(round(1/amplification))], 
                  betas[::int(round(1/amplification))], 
                  marker="4", s=35, linewidths=0.5, color=color_list[i])  
    
    plt.xlim(0, np.max(time))
    plt.ylim(0, 1.1 * np.max(Q_list))
    plt.xlabel(r'$t/t_{\mathrm{rel}}$')
    # plt.yscale('log')
    plt.ylabel(r'$\dot{q}/c$')
    plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))
    plt.grid(grid)
    # plt.legend(labelspacing=0.1, handletextpad = 0.2)  # Adjust these values to control spacing
    plt.tight_layout()
    name = 'media/qdot_compare'+'_'+q_0_type+file_type
    plt.savefig(name)
    print(f"Saved plot to {name}")
import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a pandas DataFrame
dfnothing = pd.read_csv('results/nothing.csv')
dflubin = pd.read_csv('results/lubin.csv')
dfdelay = pd.read_csv('results/delay.csv')
dfdelay9 = pd.read_csv('results/delay09.csv')
dfdelay6 = pd.read_csv('results/delay06.csv')
dfdelay3 = pd.read_csv('results/delay03.csv')


# Extract data from the DataFrame
time = dfnothing['Time']
P = [dfnothing['P'], dflubin['P'], dfdelay['P']]
q = [dfnothing['q'], dflubin['q'], dfdelay['q']]
Q = [dfnothing['Q'], dflubin['Q'], dfdelay['Q']]
P1 = [dfdelay3['P'], dfdelay6['P'], dfdelay9['P'], dfnothing['P'], dflubin['P']]

file_type = '.pdf'
grid = False
lw = 1.0
ls_list = ["--", ":", "-"]
color_list = ["r", "g", "b"]
# names_list = [r"", r"", r""]
ls_list = ["--", ":", "-", "-", "-"]
color_list = ["r", "g", "b", "y", "b"]

plt.figure(figsize=(3, 2.6))
for i in range(3):
  # Plotting q
  plt.plot(time, q[i], linestyle=ls_list[i], color=color_list[i], label=r'$q \ / c t_{\mathrm{rel}}$', linewidth=lw)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$q \ / c  t_{\mathrm{rel}}$')
  plt.grid(grid)
  # plt.legend()
  plt.tight_layout()
plt.savefig('media/q_compare'+file_type)  # Save plot as PDF for LaTeX

plt.figure(figsize=(3, 2.6))
for i in range(3):
  # Plotting Q
  plt.plot(time, Q[i], linestyle=ls_list[i], color=color_list[i], label=r'$Q$', linewidth=lw)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$\dot{q}/c$')
  plt.grid(grid)
  # plt.legend()
  plt.tight_layout()
plt.savefig('media/qdot_compare'+file_type)  # Save plot as PDF for LaTeX


color_list = ['r', 'b', 'g', 'm', 'orange']
ls_list = ['-', '--', ':', '-.', '-.']
labels = [r"$\alpha=0.3$", r"$\alpha=0.6$", r"$\alpha=0.9$", r"no delay", r"$\alpha=0$"]
plt.figure(figsize=(3, 2.6))
for i in range(5):
  # Plotting P
  plt.plot(time, P1[i], linestyle=ls_list[i], color=color_list[i], label=labels[i], linewidth=lw)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$P/P_0$')
  plt.grid(grid)
  plt.legend()
  plt.tight_layout()
plt.savefig('media/P_compare'+file_type)  # Save plot as PDF for LaTeX
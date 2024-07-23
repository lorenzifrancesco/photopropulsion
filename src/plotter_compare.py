import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a pandas DataFrame
dfnothing = pd.read_csv('results/nothing.csv')
dflubin = pd.read_csv('results/lubin.csv')
dfdelay = pd.read_csv('results/delay.csv')


# Extract data from the DataFrame
time = dfnothing['Time']
P = [dfnothing['P'], dflubin['P'], dfdelay['P']]
q = [dfnothing['q'], dflubin['q'], dfdelay['q']]
Q = [dfnothing['Q'], dflubin['Q'], dfdelay['Q']]
file_type = '.pdf'
grid = False
lw = 1.0
ls_list = ["--", ":", "-"]
color_list = ["r", "g", "b"]
# names_list = [r"", r"", r""]

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

plt.figure(figsize=(3, 2.6))
for i in range(3):
  # Plotting P
  plt.plot(time, P[i], linestyle=ls_list[i], color=color_list[i], label=r'$P$', linewidth=lw)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$P/P_0$')
  plt.grid(grid)
  # plt.legend()
  plt.tight_layout()
plt.savefig('media/P_compare'+file_type)  # Save plot as PDF for LaTeX
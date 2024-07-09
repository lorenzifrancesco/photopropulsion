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
grid = True
lw = 0.5

plt.figure(figsize=(4, 3))
for i in range(3):
  # Plotting q
  plt.plot(time, q[i], linestyle='-', color='g', label=r'$q$', linewidth=lw)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$q$')
  plt.grid(grid)
  # plt.legend()
  plt.tight_layout()
plt.savefig('media/q_compare'+file_type)  # Save plot as PDF for LaTeX

plt.figure(figsize=(4, 3))
for i in range(3):
  # Plotting Q
  plt.plot(time, Q[i], linestyle='-', color='b', label=r'$Q$', linewidth=lw)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$\dot{q}/c$')
  plt.grid(grid)
  # plt.legend()
  plt.tight_layout()
plt.savefig('media/qdot_compare'+file_type)  # Save plot as PDF for LaTeX

plt.figure(figsize=(4, 3))
for i in range(3):
  # Plotting P
  plt.plot(time, P[i], linestyle='-', color='r', label=r'$P$', linewidth=lw)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$P/P_0$')
  plt.grid(grid)
  # plt.legend()
  plt.tight_layout()
plt.savefig('media/P_compare'+file_type)  # Save plot as PDF for LaTeX
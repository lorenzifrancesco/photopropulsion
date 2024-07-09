import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('results/results.csv')

# Extract data from the DataFrame
time = df['Time']
q = df['q']
Q = df['Q']
P = df['P']
file_type = '.pdf'
grid = True
lw = 0.5

# Plotting q
plt.figure(figsize=(4, 3))
plt.plot(time, q, linestyle='-', color='g', label=r'$q$', linewidth=lw)
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel(r'$q$')
plt.grid(grid)
# plt.legend()
plt.tight_layout()
plt.savefig('media/q'+file_type)  # Save plot as PDF for LaTeX

# Plotting Q
plt.figure(figsize=(4, 3))
plt.plot(time, Q, linestyle='-', color='b', label=r'$Q$', linewidth=lw)
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel(r'$\dot{q}/c$')
plt.grid(grid)
# plt.legend()
plt.tight_layout()
plt.savefig('media/qdot'+file_type)  # Save plot as PDF for LaTeX

# Plotting P
plt.figure(figsize=(4, 3))
plt.plot(time, P, linestyle='-', color='r', label=r'$P$', linewidth=lw)
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel(r'$P/P_0$')
plt.grid(grid)
# plt.legend()
plt.tight_layout()
plt.savefig('media/P'+file_type)  # Save plot as PDF for LaTeX
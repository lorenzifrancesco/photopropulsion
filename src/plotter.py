import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('results/results.csv')

# Extract data from the DataFrame
time = df['Time']
q = df['q']
Q = df['Q']

# Plotting q
plt.figure(figsize=(4, 3))
plt.plot(time, q, linestyle='-', color='b', label='q')
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel('q')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('media/plot_q.png')  # Save plot as PDF for LaTeX

# Plotting Q
plt.figure(figsize=(4, 3))
plt.plot(time, Q, linestyle='-', color='r', label='Q')
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel('Q')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('media/plot_Q.png')  # Save plot as PDF for LaTeX

# plt.show()

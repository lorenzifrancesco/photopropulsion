import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file into a pandas DataFrame
results_file = 'results/delay.csv'
output = "results/"

alpha2 = 0.9
alpha1 = []
file_list = ["delay03.csv", "delay"]

configurations[i][j] = {
    "q": float(p1),
    "q_prime": 0.0,
    "p": 1.0,
    "delta": 0.0,
    "t": 0.0,
    # very high value to allow the termination due to stationary state detection.
    "tf": float(tf_range[i]),
    "alpha1": float(p2),
    "alpha2": float(alpha2),
    "l_diffraction": float(l_diffraction_range[i]),
    "file": file,
    "mode": str(mode_range[j]),
    "output": output
}
            
print("Plotting from: ", results_file)
df = pd.read_csv(results_file)

# Extract data from the DataFrame
time = df['Time']
q = df['q']
Q = df['Q']
P = df['P']
file_type = '.pdf'
grid = False
lw = 0.5

# Plotting q
plt.figure(figsize=(3, 2.5))
plt.plot(time, q, linestyle='-', color='g', label=r'$q$', linewidth=lw)
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel(r'$q$')
plt.grid(grid)
# plt.legend()
plt.tight_layout()
plt.savefig('media/q'+file_type)  # Save plot as PDF for LaTeX

# Plotting Q
plt.figure(figsize=(3, 2.5))
plt.plot(time, Q, linestyle='-', color='b', label=r'$Q$', linewidth=lw)
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel(r'$\dot{q}/c$')
plt.grid(grid)
# plt.legend()
plt.tight_layout()
plt.savefig('media/qdot'+file_type)  # Save plot as PDF for LaTeX

# Plotting P
# P = np.where(P == 1.0, np.nan,  P)
plt.figure(figsize=(3, 2.5))
plt.plot(time, P, linestyle='-', color='r', label=r'$P$', linewidth=lw)
plt.xlabel(r'$t/t_{\mathrm{rel}}$')
plt.ylabel(r'$\tilde{P}/P_0$')
plt.grid(grid)
# plt.legend()
plt.tight_layout()
plt.savefig('media/P'+file_type)  # Save plot as PDF for LaTeX
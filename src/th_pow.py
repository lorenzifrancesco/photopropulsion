import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

file_path = "results/res.txt"

temps = []
th_pows = []

with open(file_path, 'r') as f:
    for line in f:
        try:
            line = line.strip()
            entries = line.split('|')
            entry_dict = {key: float(value) for key, value in (e.split('=') for e in entries)}

            temps.append(entry_dict['temp'])
            th_pows.append(entry_dict['th.pow'])
        except: 
            print(f"Failed parsing line: {line}")

# Convert to NumPy arrays
temps = np.array(temps)
powers = np.array(th_pows) * 50e9  # Scale as per your original code

# Stefan–Boltzmann-style fit: T = alpha * P^(1/4)
def stefan_boltzmann_fit(P, alpha):
    return alpha * P**0.25

# Filter out zero or negative powers (since P^0.25 is undefined there)
mask = (powers > 0)
powers_fit = powers[mask]
temps_fit = temps[mask]

# Fit the curve
popt, pcov = curve_fit(stefan_boltzmann_fit, powers_fit, temps_fit)
alpha_fit = popt[0]
print(f"Fitted alpha = {alpha_fit:.3e}")

# Generate fit curve
P_fit_vals = np.linspace(powers_fit.min(), powers_fit.max(), 200)
T_fit_vals = stefan_boltzmann_fit(P_fit_vals, alpha_fit)

# Plotting
plt.figure(figsize=(3, 3))
plt.scatter(powers_fit, temps_fit, marker='o', s=3, linewidth=0.5, color='b', label='Data')
plt.plot(P_fit_vals, T_fit_vals, 'r--', label=rf'Stefan-Boltzmann law')
plt.xlabel(r'$P_{\mathrm{abs}}$ [W]')
plt.ylabel(r'$T$ [K]')
# apply 'sci' style to x-axis
plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))
# plt.title('Thermal Power vs Temperature')
# plt.grid(True)
plt.legend()
plt.tight_layout()
name = 'media/tests/th_pow_vs_temp.pdf'
plt.savefig(name)
print(f"Saved plot to {name}")
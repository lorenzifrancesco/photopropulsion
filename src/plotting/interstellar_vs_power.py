import subprocess
import toml
import os
import shutil

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import pandas as pd

# convert in "list 1"


# SI section
sail_mass = 10e-3  # kg
payload_mass = 0
power = np.logspace(8, 10, 100, dtype=np.float64)
print(power)
tf = 3600  # s
trel_range = (payload_mass + sail_mass) * (3e8)**2 / power
xrel_range = trel_range * 3e8
q0 = 800e3  # LEO
# q0 = 3500e3  # GEO
sigma = 1e-3  # kg/m^2
S = sail_mass / sigma
d_sail = np.sqrt(S/np.pi) * 2
d_laser = 10e3
wavelength = 1064e-9
l_diffraction = d_laser * d_sail / (2 * 1.22 * wavelength)
# print(np.mean(trel_range))

alpha1 = 0.97
alpha2 = 1.0

# thermals
epsilon = 1e5 * alpha1
sigma_sb = 5.67e-8
max_temp = ((1-alpha1) * power / (2 * epsilon * S * sigma_sb))**(1/4)
# print('> d_sail = {:.3f} | S = {:.3f} | Tmax = {:.3f}'.format(
    # d_sail, S, max_temp))
# continue

# Adimensional section
p1_range = q0 / xrel_range
p2_range = [alpha1, 0.0, 0.0]
mode_range = ["delay", "delay", "no"]
tf_range = tf / trel_range
l_diffraction_range = l_diffraction / xrel_range
# print(p1_range)
print(np.mean(tf_range))
print(np.mean(p1_range))
print(np.mean(l_diffraction_range))
mode = "delay"
file = "auto.csv"
output = "results/"
override = 1

if not os.path.exists("results/delta_v.npy") or override:
    print("Computing...")
    configurations = [[{} for _ in p2_range] for _ in p1_range]
    results_matrix = np.zeros((len(p1_range), len(p2_range)), dtype=np.float64)
    for (i, p1) in enumerate(p1_range):
        for (j, p2) in enumerate(p2_range):
            # print(i)
            # print(j
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

    rust_program = "./target/release/photopropulsion"
    print("Running the Rust program in ", rust_program)

    for (i, p1) in enumerate(p1_range):
        for (j, p2) in enumerate(p2_range):
            with open("input/config.toml", "w") as config_file:
                toml.dump(configurations[i][j], config_file)

            result = subprocess.run(
                [rust_program], capture_output=True, text=True)
            output = result.stdout.strip()
            lines = output.splitlines()
            last_line = lines[-1].strip()
            try:
                result_float = np.double(last_line)
                results_matrix[i, j] = result_float
                print(i, result_float)

            except ValueError as e:
                print(f"Failed to convert the last line to float: {e}")

    print(np.shape(results_matrix))
    np.save("results/delta_v.npy", results_matrix)

results_matrix = np.load("results/delta_v.npy")
print("Plotting...")
color_list = ['r', 'g', 'b', 'm', 'orange']
ls_list = ['-', ':', '--', '-.', '-.']
# single line
plt.figure(figsize=(3, 2.5))
label_list = [r'$\Delta v ^{\mathrm{M}}/c$',
              r'$\Delta v ^{\mathrm{Bragg}}/c$', r'$\Delta v^{\mathrm{S}}/c$']
np.set_printoptions(precision=10)
for (j, alpha) in enumerate(p2_range):
    plt.plot(power, results_matrix[:, j],
            color=color_list[j], ls=ls_list[j], lw=1.5, label=label_list[j])

td_fom = 2 * power * alpha1/(3e8 * (sail_mass + payload_mass)) * tf / 3e8 * np.ones(len(power))
td_fom[td_fom > 0.3] = np.nan
print(td_fom)
plt.plot(power, td_fom,
        color="m", ls="-.", lw=1.5, label=r'$\Delta v ^{\mathrm{TD}}/c$')


plt.xlabel(r'$P$ [GW]')
plt.ylabel(r'$\Delta v / c$')
num_xticks = 5  # Number of xticks you want
xtick_positions = np.linspace(power.min(), power.max(), num_xticks)
xtick_labels = [fr"${pos/1e9:3.0f}$" for pos in xtick_positions]
plt.xticks(xtick_positions, xtick_labels)
# plt.legend(labelspacing=0.1)
plt.tight_layout()
plt.savefig("media/delta_v_pow.pdf")

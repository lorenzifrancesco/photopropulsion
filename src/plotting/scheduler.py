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

p1_range = np.linspace(0.001, 0.1, 3)
p1_range = np.array([0.001, 0.05, 0.1])
p2_range = np.linspace(0.0, 0.9, 50)
mode = "delay"
file = "auto.csv"
output = "results/"
override = 0

if not os.path.exists("results/terminal_vel.npy") or override:
    print("Computing...")
    configurations = [[{} for _ in p2_range] for _ in p1_range]
    results_matrix = np.zeros((len(p1_range), len(p2_range)))
    for (i, p1) in enumerate(p1_range):
        for (j, p2) in enumerate(p2_range):
            # print(i)
            # print(j)
            configurations[i][j] = {
                "q": float(p1),
                "q_prime": 0.0,
                "p": 1.0,
                "delta": 0.0,
                "t": 0.0,
                # very high value to allow the termination due to stationary state detection.
                "tf": 100.0,
                "alphart": float(p2),
                "l_diffraction": 1000,
                "file": file,
                "mode": mode,
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
            print(lines[-2])
            last_line = lines[-1].strip()
            try:
                result_float = float(last_line)
                print(i, j, result_float)
                results_matrix[i, j] = result_float

            except ValueError as e:
                print(f"Failed to convert the last line to float: {e}")

    print(np.shape(results_matrix))
    np.save("results/terminal_vel.npy", results_matrix)

results_matrix = np.load("results/terminal_vel.npy")
print("Plotting...")
# print(np.shape(results_matrix))

# df = pd.DataFrame(results_matrix, index=p1_range, columns=p2_range)
# plt.figure(figsize=(3, 2.5))
# ax = sns.heatmap(df, annot=False, cmap='viridis',
#                  fmt=".2f", cbar=True, square=True)
# plt.xlabel(r'$q_0$')
# plt.ylabel(r'$\alpha$')
# num_xticks = 5  # Number of xticks you want
# xtick_positions = np.linspace(p1_range.min(), p1_range.max(), num_xticks)
# xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
# plt.xticks(xtick_positions, xtick_labels)
# num_yticks = 5  # Number of yticks you want
# ytick_positions = np.linspace(p2_range.min(), p2_range.max(), num_yticks)
# ytick_labels = [fr"${pos:.2f}$" for pos in ytick_positions]
# plt.yticks(ytick_positions, ytick_labels)
# plt.tight_layout()
# plt.savefig("media/heatmap.pdf")


# P1, P2 = np.meshgrid(p2_range, p1_range)
# print(np.shape(P1))
# plt.figure(figsize=(3, 2.5))
# contour = plt.contourf(P2, P1, results_matrix, cmap='viridis', levels=20)
# cbar = plt.colorbar(contour, label=r'$\dot{q}_\infty$')
# plt.xlabel(r'$q_0$')
# plt.ylabel(r'$\alpha$')
# num_xticks = 5  # Number of xticks you want
# xtick_positions = np.linspace(p1_range.min(), p1_range.max(), num_xticks)
# xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
# plt.xticks(xtick_positions, xtick_labels)
# num_yticks = 5  # Number of yticks you want
# ytick_positions = np.linspace(p2_range.min(), p2_range.max(), num_yticks)
# ytick_labels = [fr"${pos:.2f}$" for pos in ytick_positions]
# plt.yticks(ytick_positions, ytick_labels)
# num_cbar_ticks = 5  # Number of colorbar ticks you want
# cbar_ticks = np.linspace(results_matrix.min(),
#                          results_matrix.max(), num_cbar_ticks)
# cbar_tick_labels = [rf"${tick:.2f}$" for tick in cbar_ticks]
# cbar.set_ticks(cbar_ticks)
# cbar.set_ticklabels(cbar_tick_labels)

# plt.tight_layout()
# plt.savefig("media/contour.pdf")

color_list = ['r', 'b', 'g', 'm', 'orange']
ls_list = ['-', '--', ':', '-.', '-.']
# plt.figure(figsize=(3, 2.5))
# for i in range(len(p1_range)):
#     plt.plot(p2_range, results_matrix[i, :],
#              color=color_list[i], ls=ls_list[i], lw=1.5, label=rf"$q_0={p1_range[i]:.3f}$")

# plt.xlabel(r'$\alpha$')
# plt.ylabel(r'$\dot{q}_\infty$')
# plt.legend()
# num_xticks = 5  # Number of xticks you want
# xtick_positions = np.linspace(p2_range.min(), p2_range.max(), num_xticks)
# xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
# plt.xticks(xtick_positions, xtick_labels)

# plt.tight_layout()
# plt.savefig("media/terminal_lines.pdf")

# single line
plt.figure(figsize=(3, 2.5))
plt.plot(p2_range, results_matrix[0, :]*(1-p2_range),
          color=color_list[0], ls=ls_list[0], lw=1.5)

plt.xlabel(r'$\alpha$')
plt.ylabel(r'$P_\infty / \bar{P}$')
num_xticks = 5  # Number of xticks you want
xtick_positions = np.linspace(p2_range.min(), p2_range.max(), num_xticks)
xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
plt.xticks(xtick_positions, xtick_labels)

plt.tight_layout()
plt.savefig("media/P_ratio_compare.pdf")

plt.figure(figsize=(3, 2.5))
for i in range(len(p1_range)):
    plt.plot(p2_range, results_matrix[i, :]*(1-p2_range),
             color=color_list[i], ls=ls_list[i], lw=1.5, label=rf"$q_0={p1_range[i]:.3f}$")

plt.xlabel(r'$\alpha$')
plt.ylabel(r'$P_\infty / \bar{P}$')
plt.legend()
num_xticks = 5  # Number of xticks you want
xtick_positions = np.linspace(p2_range.min(), p2_range.max(), num_xticks)
xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
plt.xticks(xtick_positions, xtick_labels)

plt.tight_layout()
plt.savefig("media/P_lines.pdf")
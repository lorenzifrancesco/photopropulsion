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

p1_range = np.linspace(0.001, 1.0, 15) # percent of the lower frequency laser 
p2_range = np.linspace(0.0, 1.0, 15) # reflectivity

configurations = [[{} for _ in p2_range] for _ in p1_range]
results_matrix = np.zeros((len(p1_range), len(p2_range)))

mode = "delay.csv"
output = "results/"

for (i, p1) in enumerate(p1_range):
  for (j, p2) in enumerate(p2_range):
    # print(i)
    # print(j)
    configurations[i][j] = {
      "q": float(p1), 
      "q_prime": 0.0, 
      "p":1.0, 
      "delta":0.0, 
      "t":0.0, 
      "tf":2.5, 
      "alphart":float(p2),
      "mode":mode,
      "output":output
      }

rust_program = "./target/release/photopropulsion"

for (i, p1) in enumerate(p1_range):
  for (j, p2) in enumerate(p2_range):
    with open("input/config.toml", "w") as config_file:
        toml.dump(configurations[i][j], config_file)

    result = subprocess.run([rust_program], capture_output=True, text=True)
    output = result.stdout.strip()
    lines = output.splitlines()
    last_line = lines[-1].strip()
    try:
      result_float = float(last_line)
      print(result_float)
      results_matrix[i, j] = result_float
      
    except ValueError as e:
      print(f"Failed to convert the last line to float: {e}")
      
df = pd.DataFrame(results_matrix, index=p1_range, columns=p2_range)
plt.figure(figsize=(3, 2.5))
ax = sns.heatmap(df, annot=False, cmap='viridis', fmt=".2f", cbar=True, square=True)
plt.xlabel(r'$\alpha$')
plt.ylabel(r'$q_0$')
num_xticks = 5  # Number of xticks you want
xtick_positions = np.linspace(p1_range.min(), p1_range.max(), num_xticks)
xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
plt.xticks(xtick_positions, xtick_labels)
num_yticks = 5  # Number of yticks you want
ytick_positions = np.linspace(p2_range.min(), p2_range.max(), num_yticks)
ytick_labels = [fr"${pos:.2f}$" for pos in ytick_positions]
plt.yticks(ytick_positions, ytick_labels)
plt.tight_layout()
plt.savefig("media/heatmap.pdf")


P1, P2 = np.meshgrid(p1_range, p2_range)

plt.figure(figsize=(3, 2.5))
contour = plt.contourf(P1, P2, results_matrix, cmap='viridis', levels=20)
cbar = plt.colorbar(contour, label=r'$\dot{q}_\infty$')

# # Add contour lines on top of filled contours (optional)
# ax = plt.contour(P1, P2, results_matrix, colors='k', levels=10, linestyles='--')

plt.xlabel(r'$\alpha$')
plt.ylabel(r'$q_0$')
# plt.xticks(np.round(p1_range, 2))  # X-axis ticks formatted to 2 decimal places
# plt.yticks(np.round(p2_range, 2))# ax.set_xticklabels([f"{x:.2f}" for x in df.columns], 

num_xticks = 5  # Number of xticks you want
xtick_positions = np.linspace(p1_range.min(), p1_range.max(), num_xticks)
xtick_labels = [fr"${pos:.2f}$" for pos in xtick_positions]
plt.xticks(xtick_positions, xtick_labels)
num_yticks = 5  # Number of yticks you want
ytick_positions = np.linspace(p2_range.min(), p2_range.max(), num_yticks)
ytick_labels = [fr"${pos:.2f}$" for pos in ytick_positions]
plt.yticks(ytick_positions, ytick_labels)
num_cbar_ticks = 5  # Number of colorbar ticks you want
cbar_ticks = np.linspace(results_matrix.min(), results_matrix.max(), num_cbar_ticks)
cbar_tick_labels = [rf"${tick:.2f}$" for tick in cbar_ticks]
cbar.set_ticks(cbar_ticks)
cbar.set_ticklabels(cbar_tick_labels)

plt.tight_layout()
plt.savefig("media/contour.pdf")
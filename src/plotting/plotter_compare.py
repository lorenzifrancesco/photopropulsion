import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import toml
import subprocess

p1_list = [1e-12, 0.3, 0.6, 0.9]

mode = "delay"
output = "results/"
file = ["power0.csv", "power3.csv", "power6.csv", "power9.csv"]
configurations = []
tf = 3e-2
for i, p1 in enumerate(p1_list):
  configurations.append({
      "q": 3e-7,
      "q_prime": 0.0,
      "p": 1.0,
      "delta": 0.0,
      "t": 0.0,
      # very high value to allow the termination due to stationary state detection.
      "tf": tf,
      "alpha1": float(p1),
      "alpha2": 1,
      "l_diffraction": 10000.00,
      "file": str(file[i]),
      "mode": mode,
      "output": output
  })

rust_program = "./target/release/photopropulsion"
print("Running the Rust program in ", rust_program)
for conf in configurations:
  with open("input/config.toml", "w") as running_config_file:
      print(f"Running the script for ", conf["file"])
      toml.dump(conf, running_config_file)
  if True: # skip computation
    result = subprocess.run([rust_program], capture_output=True, text=True)
    print("done")
# Load the CSV file into a pandas DataFrame
df_list = []
P_list = []
Q_list = []
q_list = []
for ff in file:
  dd = pd.read_csv('results/'+ff)
  df_list.append(dd)
  P_list.append(dd['P'])
  q_list.append(dd['q'])
  Q_list.append(dd['Q'])

time = np.linspace(0, tf, len(P_list[0]))
file_type = '.pdf'
grid = False
lw = 1.0
ls_list = ["--", ":", "-"]
# color_list = ["r", "g", "b"]
# names_list = [r"", r"", r""]
ls_list = ["--", ":", "-", "-", "-"]
color_list = ["r", "g", "b", "y", "b"]

color_list = ['orange', 'b', 'g', 'r']
ls_list = ['-', '--', ':', '-.']
labels = [r"$\alpha=0$", r"$\alpha=0.3$", r"$\alpha=0.6$", r"$\alpha=0.9$"]
color_list = color_list[::-1]
P_list = P_list[::-1]
ls_list = ls_list[::-1]
labels = labels[::-1]

plt.figure(figsize=(3, 2.6))
max = 4
for i in range(max):
  # Plotting P
  plt.plot(time, P_list[i], linestyle=ls_list[i], color=color_list[i], label=labels[i], linewidth=lw)
  if i != 0:
    plt.plot(time, 1/(1-(0.3*i)) * np.ones_like(P_list[i]), linestyle="-", color=color_list[::-1][i], linewidth=0.5)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$\tilde{P}/P_0$')
  plt.grid(grid)
plt.legend(labelspacing=0.1)
plt.tight_layout()
plt.savefig('media/P_ratio_compare'+file_type)  # Save plot as PDF for LaTeX


Q_list = Q_list[::-1]
plt.figure(figsize=(3, 2.6))
max = 4
for i in range(max):
  # Plotting P
  plt.plot(time, Q_list[i], linestyle=ls_list[i], color=color_list[i], label=labels[i], linewidth=lw)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$\dot{q}/c$')
  plt.grid(grid)
plt.legend(labelspacing=0.1, handletextpad=0.2)  # Adjust these values to control spacing
plt.tight_layout()
plt.savefig('media/qdot_compare'+file_type)  # Save plot as PDF for LaTeX

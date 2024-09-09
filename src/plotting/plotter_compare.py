import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import toml
import subprocess

p1_list = [0.0, 0.3, 0.6, 0.9]

mode = "delay"
output = "results/"
file = ["power0.csv", "power3.csv", "power6.csv", "power9.csv"]
configurations = []
tf = 0.7
for i, p1 in enumerate(p1_list):
  configurations.append({
      "q": 0.1,
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
  result = subprocess.run([rust_program], capture_output=True, text=True)

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

# plt.figure(figsize=(3, 2.6))
# for i in range(3):
#   # Plotting q
#   plt.plot(time, q[i], linestyle=ls_list[i], color=color_list[i], label=r'$q \ / c t_{\mathrm{rel}}$', linewidth=lw)
#   plt.xlabel(r'$t/t_{\mathrm{rel}}$')
#   plt.ylabel(r'$q \ / c  t_{\mathrm{rel}}$')
#   plt.grid(grid)
#   # plt.legend()
#   plt.tight_layout()
# plt.savefig('media/q_compare'+file_type)  # Save plot as PDF for LaTeX

# plt.figure(figsize=(3, 2.6))
# for i in range(3):
#   # Plotting Q
#   plt.plot(time, Q[i], linestyle=ls_list[i], color=color_list[i], label=r'$Q$', linewidth=lw)
#   plt.xlabel(r'$t/t_{\mathrm{rel}}$')
#   plt.ylabel(r'$\dot{q}/c$')
#   plt.grid(grid)
#   # plt.legend()
#   plt.tight_layout()
# plt.savefig('media/qdot_compare'+file_type)  # Save plot as PDF for LaTeX


color_list = ['r', 'b', 'g', 'm', 'orange']
ls_list = ['-', '--', ':', '-.', '-.']
labels = [r"$\alpha=0.3$", r"$\alpha=0.6$", r"$\alpha=0.9$", r"no delay", r"$\alpha=0$"]
plt.figure(figsize=(3, 2.6))
for i in range(5):
  # Plotting P
  plt.plot(time, P_list[i]/(1/(1-0.3*(i+1))), linestyle=ls_list[i], color=color_list[i], label=labels[i], linewidth=lw)
  plt.xlabel(r'$t/t_{\mathrm{rel}}$')
  plt.ylabel(r'$P/P_0$')
  plt.grid(grid)
  plt.legend()
  plt.tight_layout()
plt.savefig('media/P_ratio_compare'+file_type)  # Save plot as PDF for LaTeX


# labels = [r"$\alpha=0.3$", r"$\alpha=0.6$", r"$\alpha=0.9$", r"no delay", r"$\alpha=0$"]
# plt.figure(figsize=(3, 2.6))
# for i in range(5):
#   # Plotting P
#   plt.plot(time, P1[i], linestyle=ls_list[i], color=color_list[i], label=labels[i], linewidth=lw)
#   plt.xlabel(r'$t/t_{\mathrm{rel}}$')
#   plt.ylabel(r'$\tilde{P}/P_0$')
#   plt.grid(grid)
#   plt.legend()
#   plt.tight_layout()
# plt.savefig('media/P_ratio_compare'+file_type)  # Save plot as PDF for LaTeX
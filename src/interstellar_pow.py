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
from scipy.constants import c
import simulation
from simulation import Reflector

override = 1

eta_list = np.array([0.0])

with open('input/params.toml', 'r') as file:
    config = toml.load(file)
print("================== physical parameters ")
for key, value in config.items():
    globals()[key] = value
    print(key, globals()[key])
print("======================= end parameters ")

for eidx, eta in enumerate(eta_list):
    l = simulation.Launch()
    l.eta = eta
    power_range = np.linspace(0, 200, 100, dtype=np.float64) * 1e9

    # Adimensional section
    alpha1 = 0.99
    mode_range = [("delay", Reflector.FLAT),
                  ("delay", Reflector.M1),
                  ("delay", Reflector.M2),
                  ("lubin", Reflector.FLAT),
                  ]

    mode = "delay"
    file = "auto.csv"
    output = "results/"
    # exit()
    if not os.path.exists("results/delta_v.npy") or override:
        print("Computing...")
        results_matrix = np.zeros(
            (len(power_range), len(mode_range)), dtype=np.float64)

        for (i, power) in enumerate(power_range):
            for (j, mode) in enumerate(mode_range):
                with open("input/config.toml", "w") as config_file:
                    l.p_0 = power
                    l.mode = mode[0]
                    l.multilayer = mode[1]
                    l.write_config('input/config.toml')
                    results_matrix[i, j] = l.run()

        print(np.shape(results_matrix))
        np.save("results/delta_v.npy", results_matrix)

    results_matrix = np.load("results/delta_v.npy")
    print("Plotting...")
    color_list = ['r', 'g', 'b', 'm', 'c']
    ls_list = ['-', ':', '--', '-.', '--']

    # single line
    plt.figure(figsize=(3, 2.5))
    label_list = [r'${\mathrm{F}}$',
                  r'${\mathrm{M1}}$',
                  r'${\mathrm{M2}}$',
                  r'${\mathrm{S}}$']
    np.set_printoptions(precision=10)
    for (j, alpha) in enumerate(mode_range):
        plt.plot(power_range, results_matrix[:, j],
                 color=color_list[j], ls=ls_list[j], lw=1.5, label=label_list[j])

    td_fom = 2 * power_range * alpha1 / \
        (c**2 * (l.sail_mass * (1 + l.eta))) * l.t_f
    td_fom[td_fom > 1] = np.nan
    plt.plot(power_range, td_fom,
             color=color_list[4], ls=ls_list[4], lw=1.5, label=r'${\mathrm{NR}}$')

    plt.xlabel(r'$P_0$')
    plt.ylabel(r'$\Delta v / c$')
    num_xticks = 5
    xtick_positions = np.linspace(
        power_range.min(), power_range.max(), num_xticks)
    plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))
    plt.legend(labelspacing=0.1)
    plt.tight_layout()
    plt.savefig("media/delta_v_p_"+str(eidx)+".pdf")
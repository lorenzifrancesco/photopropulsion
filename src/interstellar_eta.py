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

override = 0

power_list = np.array([100.0]) * 1e9

# with open('input/params.toml', 'r') as file:
#     config = toml.load(file)
# print("================== physical parameters ")
# for key, value in config.items():
#     globals()[key] = value
#     print(key, globals()[key])
# print("======================= end parameters ")

for pidx, power in enumerate(power_list):
    l = simulation.Launch()
    l.p_0 = power
    eta_range = np.linspace(0, 2, 50, dtype=np.float64)

    # Adimensional section
    alpha1 = 0.999
    mode_range = [("delay", Reflector.FLAT),
                  ("delay", Reflector.M1),
                  ("delay", Reflector.M2),
                  ("delay", Reflector.M3),
                  ("lubin", Reflector.FLAT),
                  ]

    mode = "delay"
    file = "auto.csv"
    output = "results/"
    # exit()
    if not os.path.exists("results/delta_v.npy") or override:
        print("Computing...")
        results_matrix = np.zeros(
            (len(eta_range), len(mode_range)), dtype=np.float64)

        for (i, eta) in enumerate(eta_range):
            for (j, mode) in enumerate(mode_range):
                with open("input/config.toml", "w") as config_file:
                    l.eta = eta
                    l.mode = mode[0]
                    l.multilayer = mode[1]
                    l.write_config('input/config.toml')
                    results_matrix[i, j] = l.run()
                    
        print(np.shape(results_matrix))
        np.save("results/delta_v.npy", results_matrix)

    results_matrix = np.load("results/delta_v.npy")
    print("Plotting...")
    color_list = ['r', 'g', 'b', 'm', 'c', 'orange']
    ls_list = ['-', ':', '--', '-.', '--', '--']

    # single line
    plt.figure(figsize=(3, 2.5))
    label_list = [r'${\mathrm{F}}$',
                  r'${\mathrm{M1}}$',
                  r'${\mathrm{M2}}$',
                  r'${\mathrm{M3}}$',
                  r'${\mathrm{S}}$']
    np.set_printoptions(precision=10)
    for (j, alpha) in enumerate(mode_range):
        plt.plot(eta_range, results_matrix[:, j],
                 color=color_list[j], ls=ls_list[j], lw=1.5, label=label_list[j])

    td_fom = 2 * power * alpha1/(3e8 * (l.sail_mass *(1+eta_range))) * l.t_f / c
    td_fom[td_fom > 1] = np.nan
    plt.plot(eta_range, td_fom,
             color=color_list[4], ls=ls_list[4], lw=1.5, label=r'${\mathrm{NR}}$')

    plt.xlabel(r'$\eta$')
    plt.ylabel(r'$\Delta v / c$')
    num_xticks = 5  # Number of xticks you want
    # xtick_positions = np.linspace(eta_range.min(), eta_range.max(), num_xticks)
    # xtick_labels = [fr"${pos:.0f}$" for pos in xtick_positions]
    # plt.xticks(xtick_positions, xtick_labels)
    plt.legend(labelspacing=0.1)
    plt.tight_layout()
    plt.savefig("media/delta_v_"+str(pidx)+".pdf")

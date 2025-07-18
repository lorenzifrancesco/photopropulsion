import subprocess
import toml
import os, sys
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
from tqdm import tqdm
from scipy.interpolate import interp1d

figsize = (2.8, 2.2)
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "text.usetex": True,
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 12,
})

def plot_interstellar(todo = ["eta", "pow"],
                      override = False,
                      ratio = True,
                      special = ""
                      ):
  if ratio: 
    assert not override 
     
  if ratio:
    ylabel = r'$\Delta v / \Delta v_S$'
  else:
    ylabel = r'$\Delta v/ c$'
  mode_range = [("delay", Reflector.FLAT),
                ("delay", Reflector.M1),
                ("delay", Reflector.M2),
                ("delay", Reflector.M3),
                ("lubin", Reflector.FLAT),
                ]
  color_list = ['r', 
                'g', 
                'b', 
                'm', 
                'c', 
                'orange']
  ls_list = ['-', 
              ':', 
              '--', 
              '-.', 
              '--',
              '--', 
              '-']
  label_list = [r'$\mathrm{F}$',
                r'$\mathrm{M}_{S1}$',
                r'$\mathrm{M}_{S2}$',
                r'$\mathrm{M}_{S3}$',
                r'$\mathrm{S}$',]
  panels_pow = [r'(a)', r'(c)']
  panels_eta = [r'(b)', r'(d)']
  panel_pow = panels_pow[0]
  panel_eta = panels_eta[0]
  if ratio:
    label_list = label_list[:-1]
    mode_range = mode_range[:-1]
    color_list = ['r', 
                'g', 
                'b', 
                'm', 
                'orange']
    panel_pow = panels_pow[1]
    panel_eta = panels_eta[1]
    ylims = [0.0, 9.3]
  else:
    ylims = [0, 0.35]
  n_simulations = len(label_list)
  # file = "auto.csv"
  # output = "results/"

  ## ETA section ========================
  if "eta" in todo:
    n_samples_eta = 5
    eta_range = np.linspace(0, 2, n_samples_eta, dtype=np.float64)
    eta_range_us = np.linspace(0, 2, n_samples_eta*50, dtype=np.float64)
    l = simulation.Launch()
    l.p_0 = 50.0e9
    l.alpha1 = 0.0
    ## Compute section
    if not os.path.exists("results/v_eta.npy") or override:
        print("Computing...")
        results_matrix = np.zeros(
            (len(eta_range), len(mode_range)), dtype=np.float64)

        for (i, eta) in enumerate(eta_range):
            for (j, mode) in enumerate(mode_range):
                with open("input/_config.toml", "w") as config_file:
                    l.eta = eta
                    l.mode = mode[0]
                    l.multilayer = mode[1]
                    assert(l.cutoff_frequency == 0.0)
                    print(f"eta={l.eta:.1e}, mode={str(mode[1]):15}", end="")
                    print(f" | tf={l.get_tf():.3e}, ht = 1e-06")
                    sys.stdout = open(os.devnull, 'w')
                    l.write_config('input/_config.toml')
                    results_matrix[i, j] = l.run()
                    sys.stdout = sys.__stdout__
        print(np.shape(results_matrix))
        np.save("results/v_eta.npy", results_matrix)

    results_matrix = np.load("results/v_eta.npy")
    print("Plotting...")
    print(np.shape(results_matrix))
    n_last_result = np.shape(results_matrix)[1]
    # single line
    plt.figure(figsize=figsize)
    np.set_printoptions(precision=10)
    if ratio:
      for i in range(np.shape(results_matrix)[1]-1):
        results_matrix[:, i] = results_matrix[:, i] / results_matrix[:, n_last_result-1]
    # resampling
    f = interp1d(eta_range, results_matrix, axis=0, kind='cubic', fill_value="extrapolate")
    results_matrix_us = f(eta_range_us)
    for (j, alpha) in enumerate(mode_range):
        plt.plot(eta_range_us, results_matrix_us[:, j],
                  color=color_list[j], ls=ls_list[j], lw=1.5, label=label_list[j])
    alpha1 = 1.0
    td_fom = 2 * l.p_0 * alpha1/(3e8 * (l.sail_mass *(1+eta_range_us))) * l.t_f / c
    td_fom[td_fom > 1] = np.nan
    if ratio:
        td_fom = td_fom / results_matrix_us[:, n_last_result-1]
    plt.plot(eta_range_us, td_fom,
              color=color_list[n_simulations], ls=ls_list[n_simulations], lw=1.5, label=r'${\mathrm{NR}}$')

    plt.xlabel(r'$\eta$')
    plt.ylabel(ylabel)
    num_xticks = 5
    # plt.legend(labelspacing=0.1)
    plt.tight_layout()
    plt.ylim(ylims)
    # sci notation
    plt.gca().ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.text(0.5, 0.95, panel_eta, 
         horizontalalignment='center', 
         verticalalignment='center', 
         transform=plt.gca().transAxes, 
         fontsize=12)
    name = "media/v_eta"+special+".pdf"
    plt.savefig(name)
    print("Saved to", name)

  ## POWER section =====================
  if "pow" in todo:
    n_samples_pow = 5
    power_range = np.linspace(10, 100, n_samples_pow, dtype=np.float64) * 1e9
    power_range_us = np.linspace(10, 100, n_samples_pow*50, dtype=np.float64) * 1e9
    l = simulation.Launch()
    l.eta = 0.0
    if not os.path.exists("results/v_pow.npy") or override:
        print("Computing...")
        results_matrix = np.zeros(
            (len(power_range), len(mode_range)), dtype=np.float64)

        for (i, power) in enumerate(power_range):
            for (j, mode) in enumerate(mode_range):
                with open("input/_config.toml", "w") as config_file:
                    l.p_0 = power
                    l.mode = mode[0]
                    l.multilayer = mode[1]
                    l.alpha1 = 0.0 # enforce loading of actual reflectances
                    # print(f"\n tf={l.get_tf():.3e}, ht = 1e-06")
                    assert(l.cutoff_frequency == 0.0)
                    print(f"pow={l.p_0:.1e}, mode={str(mode[1]):15}", end="")
                    print(f" | tf={l.get_tf():.3e}, ht = 1e-06")
                    sys.stdout = open(os.devnull, 'w')
                    l.write_config('input/_config.toml')
                    results_matrix[i, j] = l.run()
                    sys.stdout = sys.__stdout__
        np.save("results/v_pow.npy", results_matrix)

    results_matrix = np.load("results/v_pow.npy")
    print("Plotting...")
    if ratio:
      for i in range(np.shape(results_matrix)[1]-1):
        results_matrix[:, i] = results_matrix[:, i] / results_matrix[:, 4]
    # single line
    plt.figure(figsize=figsize)
    np.set_printoptions(precision=10)
    # resampling 
    f = interp1d(power_range, results_matrix, axis=0, kind='cubic', fill_value="extrapolate")
    results_matrix_us = f(power_range_us)
    for (j, alpha) in enumerate(mode_range):
        plt.plot(power_range_us, results_matrix_us[:, j],
                  color=color_list[j], ls=ls_list[j], lw=1.5, label=label_list[j])

    alpha1 = 1.0
    td_fom = 2 * power_range_us * alpha1 / \
        (c**2 * (l.sail_mass * (1 + l.eta))) * l.t_f
    td_fom[td_fom > 1] = np.nan
    if ratio:
      td_fom = td_fom / results_matrix_us[:, 4]
    plt.plot(power_range_us, td_fom,
              color=color_list[n_simulations], ls=ls_list[n_simulations], lw=1.5, label=r'${\mathrm{NR}}$')

    plt.xlabel(r'$P_0$')
    plt.ylabel(ylabel)
    plt.ylim(ylims)
    # sci notation
    plt.gca().ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    num_xticks = 5
    xtick_positions = np.linspace(
        power_range_us.min(), power_range_us.max(), num_xticks)
    plt.gca().ticklabel_format(style='sci', axis='x', scilimits=(3, 0))
    plt.legend(labelspacing=0.1)
    plt.tight_layout()
    plt.text(0.5, 0.95, panel_pow, 
         horizontalalignment='center', 
         verticalalignment='center', 
         transform=plt.gca().transAxes, 
         fontsize=12)
    plt.savefig("media/v_pow"+special+".pdf")
    print("Saved to media/v_pow"+special+".pdf")
    
if __name__ == "__main__":
  # for i in range(2):
  #   if i == 0:
  #     special = "_rr"
  #     ratio = True
  #   else:
  #     special = ""
  #     ratio = False
  #   #
  #   plot_interstellar(todo = ["eta", "pow"],
  #               override = not ratio,
  #               ratio = ratio, 
  #               special = special)
    
  # make this out of the for loop for overriding the values in the files
  plot_interstellar(todo = ["pow", "eta"],
                    override = False,
                    ratio = False, 
                    special = "_+5cents")
  # plot_interstellar(todo = ["pow", "eta"],
  #                   override = False,
  #                   ratio = True, 
  #                   special = "_ref")
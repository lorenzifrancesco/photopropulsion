import numpy as np
from dataclasses import dataclass
import toml
from scipy.constants import Boltzmann, c, h
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum
import csv
import matplotlib.colors as mcolors
from matplotlib.cm import get_cmap


class Reflector(Enum):
    M1 = 1
    M2 = 2
    FLAT = 3


class Launch:
    sail_mass: float
    eta: float
    tf: float
    q0: float
    sigma: float
    d_sail: float
    d_laser: float
    alpha1: float
    alpha2: float
    rust: str

    def __init__(self, filename='input/params.toml'):
        with open(filename, 'r') as f:
            ff = toml.load(f)
            self.sail_mass = ff['sail_mass']
            self.eta = ff['eta']  # m_payload/m_sail
            self.t_f = ff['t_f']
            self.q_0 = ff['q_0']
            self.sigma = ff['sigma']
            self.p_0 = ff['p_0']
            # self.d_sail = ff['d_sail']
            self.d_laser = ff['d_laser']
            self.alpha1 = ff['alpha1']
            self.alpha2 = ff['alpha2']
            self.rust = ff['rust']
            self.lambda_0 = ff['lambda_0']
            self.mode = ff['mode']
            self.multilayer = Reflector(ff['multilayer'])
        self.d_sail = np.sqrt(self.sail_mass/self.sigma/np.pi)
        self.alpha = 1.22
        self.file = 'delay.csv'
        self.output_folder = 'results/'

    def get_m(self):
        return (1 + self.eta) * self.sail_mass

    def get_t_rel(self):
        return self.sail_mass * c**2 / self.p_0

    def get_l_rel(self):
        return self.get_t_rel() * c

    def get_l_diffraction(self):
        return self.d_sail*self.d_laser/(2*self.alpha * self.lambda_0)

    def get_l_d(self):
        return self.get_l_diffraction() / self.get_l_rel()

    def get_tf(self):
        return self.t_f/self.get_t_rel()

    def update(self):
        self.compile()
        self.run()

    def compile(self):
        rust_compile = 'cargo build --release'
        # print("Compiling...")
        result = subprocess.run(rust_compile, shell=True,
                                capture_output=True, text=True)
        # print("Done.")

    def write_config(self, file):
        # print("Wrinting config...")

        config = {
            "q":             self.q_0/self.get_l_rel(),
            "q_prime":       0.0,
            "p":             1.0,
            "delta":         0.0,
            "t":             0.0,
            "tf":            self.t_f/self.get_t_rel(),
            "multilayer":    self.multilayer.name,
            "alpha1":        self.alpha1,
            "alpha2":        self.alpha2,
            "l_diffraction": float(self.get_l_d()),
            "file":          self.file,
            "mode":          self.mode,
            "output":        self.output_folder
        }
        # print(config)
        with open(file, "w") as config_file:
            toml.dump(config, config_file)
        # print("Done.")

    def run(self, realtime=False):
        print("Running...")
        print("_" * 30)
        if realtime:
            result = subprocess.run(
                [self.rust], text=True, stdout=subprocess.PIPE, capture_output=True)
        else:
            result = subprocess.run(
                [self.rust], capture_output=True, text=True)
        print(result.stdout)
        colored_text = result.stderr
        if "panicked" in colored_text:
            colored_text = colored_text.replace(
                "panicked", "\033[91mpanicked\033[0m")
        print(colored_text)
        print("_" * 30)
        print("Done.")

    def show(self):
        # Table headers and layout
        header_width = 35
        value_width = 20
        print("=" * (header_width + value_width))
        print(f"{'Sail Properties':<{header_width-15}}{'Value':>{value_width}}")
        print("=" * (header_width + value_width))
        print(f"{'Sail Mass':<{header_width}}{self.sail_mass:.2e}")
        print(f"{'Alpha1':<{header_width}}{self.alpha1:.2e}")
        print(f"{'Alpha2':<{header_width}}{self.alpha2:.2e}")
        print(f"{'Mulilayer':<{header_width}}{self.multilayer}")
        print(f"{'Payload-to-Sail Mass Ratio (eta)':<{header_width}}{self.eta:.2e}")
        print(f"{'Surface Mass Density (sigma)':<{header_width}}{self.sigma:.2e}")

        print("\n" + "=" * (header_width + value_width))
        print(f"{'Laser Properties':<{header_width-15}}{'Value':>{value_width}}")
        print("=" * (header_width + value_width))
        print(f"{'Sail Diameter':<{header_width}}{self.d_sail:.2e}")
        print(f"{'Laser Diameter':<{header_width}}{self.d_laser:.2e}")
        print(f"{'Laser Wavelength (lambda_0)':<{header_width}}{self.lambda_0:.2e}")
        print(f"{'Diffraction Lenght':<{header_width}}{self.get_l_diffraction():.2e}")

        print("\n" + "=" * (header_width + value_width))
        print(f"{'Simulation Settings':<{header_width-15}}{'Value':>{value_width}}")
        print("=" * (header_width + value_width))
        print(f"{'Final Time (t_f)':<{header_width}}{self.t_f:.2e}")
        print(f"{'Initial Position (q_0)':<{header_width}}{self.q_0:.2e}")
        # print(f"{'Rust Version':<{header_width}}{self.rust}")
        print(f"{'Mode':<{header_width}}{self.mode}")
        print(f"{'Output File':<{header_width}}{self.file}")
        print(f"{'Output Folder':<{header_width}}{self.output_folder}")
        print("\n" + "=" * (header_width + value_width))
        print(f"{'Normalized values':<{header_width-15}}{'Value':>{value_width}}")
        print("=" * (header_width + value_width))
        print(f"{'t_rel':<{header_width}}{self.get_t_rel():.2e}")
        print(f"{'l_rel':<{header_width}}{self.get_l_rel():2e}")
        print("_" * (header_width + value_width))
        print(f"{'l_d':<{header_width}}{self.get_l_d():2e}")
        print(f"{'t_f':<{header_width}}{self.t_f/self.get_t_rel():.2e}")
        print("=" * (header_width + value_width))

    def plot_dynamics(self):
        print("Plotting from: ", self.output_folder + self.file)
        df = pd.read_csv(self.output_folder + self.file)

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
        if self.get_l_d() < np.max(q):
            plt.axhline(self.get_l_d(), ls="--", color="r", lw=1)
        # plt.legend()
        plt.tight_layout()
        plt.savefig('media/q'+file_type)  # Save plot as PDF for LaTeX

        # Plotting Q
        plt.figure(figsize=(3, 2.5))
        plt.plot(time, Q, linestyle='-', color='b', label=r'$Q$', linewidth=lw)
        plt.xlabel(r'$t/t_{\mathrm{rel}}$')
        plt.ylabel(r'$\dot{q}/c$')
        plt.grid(grid)
        plt.axhline(0.2, ls="--", color="r", lw=1)
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
        print("Done.")

    def read_speed_from_csv(self, file_path):
        df = pd.read_csv(file_path)
        times = np.array(df['Time'])
        speeds = np.array(df['Q'])
        total_powers = np.array(df['P'])
        return times, speeds, total_powers

    def read_spectral_components_from_csv(self, file_path):
        frequencies = []
        powers = []

        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            row_count = 0
            for row in reader:
                if row_count % 2 == 0:  # Frequencies (even index)
                    frequencies.append(list(map(float, row)))
                else:  # Powers (odd index)
                    powers.append(list(map(float, row)))
                row_count += 1
        return np.array(frequencies), np.array(powers)

    def plot_spectrum(self):
        frequencies, powers = self.read_spectral_components_from_csv(
            'results/spectrum.csv')
        times, speeds, total_powers = self.read_speed_from_csv(
            'results/delay.csv')
        speeds = speeds[2:]
        times = times[2:]
        total_powers = total_powers[2:]
        sqrt_d = np.sqrt((1-speeds)/(1+speeds))
        print(frequencies.shape, sqrt_d.shape)
        powers = np.where(powers == 0, np.nan, powers)
        frequencies = np.where(frequencies == 0, np.nan, frequencies)
        time_steps = np.arange(powers.shape[0])

        config_path = 'input/config.toml'
        config = toml.load(config_path)
        tf = config['tf']

        lw = 1.5
        norm = mcolors.Normalize(vmin=np.min(
            frequencies), vmax=np.max(frequencies))
        tot_frequencies = frequencies.shape[1]
        plt.figure(figsize=(3, 2.5))
        viridis = get_cmap('viridis', tot_frequencies)
        max_power = np.max(powers)
        for j in range(tot_frequencies):
            plt.plot(time_steps/len(time_steps)*tf,
                     frequencies[:, j] * sqrt_d, lw=lw)

        # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        # sm.set_array([])
        # plt.colorbar(sm, label='Frequency')
        plt.gca().ticklabel_format(style='sci', axis='both', scilimits=(3, 0))
        plt.xlabel(r'$t/t_\mathrm{rel}$')
        plt.ylabel(r'$\omega_i^\prime/\omega_0$')
        # plt.legend(loc='best')
        # plt.grid(True)
        plt.tight_layout()
        plt.savefig("media/spectrum_lines.pdf")

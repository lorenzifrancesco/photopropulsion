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
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize, ListedColormap


def adjust_luminosity_contrast(cmap, lum_factor, contrast_factor):
    colors = cmap(np.arange(cmap.N))
    colors = np.clip(colors * lum_factor, 0, 1)
    midpoint = 0.5
    colors = (colors - midpoint) * contrast_factor + midpoint
    colors = np.clip(colors, 0, 1)
    return ListedColormap(colors)


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
        return self.sail_mass * (1+self.eta) * c**2 / self.p_0

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
        print("Compiling...")
        result = subprocess.run(rust_compile, shell=True,
                                capture_output=True, text=True)
        print("Done.")

    def write_config(self, file):
        print("Wrinting config...")

        config = {
            "q":             float(self.q_0/self.get_l_rel()),
            "q_prime":       0.0,
            "p":             1.0,
            "delta":         0.0,
            "t":             0.0,
            "tf":            float(self.t_f/self.get_t_rel()),
            "multilayer":    self.multilayer.name,
            "alpha1":        float(self.alpha1),
            "alpha2":        float(self.alpha2),
            "l_diffraction": float(self.get_l_d()),
            "file":          self.file,
            "mode":          self.mode,
            "output":        self.output_folder
        }
        with open(file, "w") as config_file:
            toml.dump(config, config_file)
        print("Done.")

    def run(self, realtime=False):
        print("Running...")
        print("_" * 30)
        if realtime:
            result = subprocess.run(
                [self.rust], text=True, stdout=subprocess.PIPE, capture_output=True)
            result_float = -1
        else:
            result = subprocess.run(
                [self.rust], capture_output=True, text=True)
            output = result.stdout.strip()
            lines = output.splitlines()
            last_line = lines[-1].strip()
            try:
                result_float = np.double(last_line)
            except:
              print("\033[91Failed to read final velocity\033[0m")
              pass
        print(result.stdout)
        colored_text = result.stderr
        if "panicked" in colored_text:
            colored_text = colored_text.replace(
                "panicked", "\033[91mpanicked\033[0m")
        print(colored_text)
        print("_" * 30)
        print("Done.")
        return result_float


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
        print(f"{'t_rel [s]':<{header_width}}{self.get_t_rel():.2e}")
        print(f"{'l_rel [m]':<{header_width}}{self.get_l_rel():2e}")
        print(
            f"{'l_rel [AU]':<{header_width}}{self.get_l_rel()/1.495979e+11:2e}")
        print("_" * (header_width + value_width))
        print(f"{'l_d':<{header_width}}{self.get_l_d():2e}")
        print(f"{'q_0':<{header_width}}{self.q_0/self.get_l_rel():2e}")
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

    def plot_spectrum(self, threshold=0.0):
        print("Plotting spectrum...")
        frequencies, powers = self.read_spectral_components_from_csv(
            'results/spectrum.csv')
        times, speeds, total_powers = self.read_speed_from_csv(
            'results/delay.csv')
        skip = 20
        speeds = speeds[2::skip]
        times = times[2::skip]
        frequencies = frequencies[::skip, :]
        powers = powers[::skip, :]
        total_powers = total_powers[2::skip]
        sqrt_d = np.sqrt((1-speeds)/(1+speeds))
        tot_frequencies = frequencies.shape[1]
        for j in range(tot_frequencies):
            frequencies[:, j] = frequencies[:, j]*sqrt_d
            powers[:, j] = powers[:, j]*sqrt_d
            frequencies[:, j] = np.where(
                powers[:, j] < threshold, np.nan, frequencies[:, j])
        frequencies = np.where(frequencies == 0, np.nan, frequencies)
        frequencies = np.where(powers <= threshold, np.nan, frequencies)
        time_steps = np.arange(powers.shape[0])

        config_path = 'input/config.toml'
        config = toml.load(config_path)
        tf = config['tf']

        time_axis = time_steps/len(time_steps)*tf

        fig, ax = plt.subplots(figsize=(3.2, 2.6))
        norm = Normalize(0.0, 1.0)
        cmap = get_cmap('coolwarm')
        adj_cmap = adjust_luminosity_contrast(cmap, 0.6, 2.5)
        print(frequencies.shape)
        for j in range(tot_frequencies):
            points = np.array([time_axis, frequencies[:, j]]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
            lc = LineCollection(segments, cmap=adj_cmap, norm=norm)
            lc.set_array(powers[:, j])
            lc.set_linewidth(1.5)
            ax.add_collection(lc)
        # ax.autoscale()
        ax.set_xlim(time_axis.min(), time_axis.max())
        cb = plt.colorbar(lc, ax=ax)
        cb.set_label(r"$\tilde{P}_i'/P_0$")
        green_threshold = 0.5
        freq_with_power_above_half = np.nanmin(
            frequencies[powers >= green_threshold])
        # freq_with_power_above_half = np.min(frequencies[-1, powers[-1, :] >= threshold])
        print(freq_with_power_above_half)
        plt.axhspan(freq_with_power_above_half, 1.0, xmin=0,
                    xmax=1, color='green', alpha=0.2)
        # plt.axhline(np.nanmin(frequencies))
        # for j in range(tot_frequencies):
        #     print(np.nanmin(frequencies[:, j]))
        plt.gca().ticklabel_format(style='sci', axis='both', scilimits=(3, 0))
        plt.xlabel(r'$t/t_\mathrm{rel}$')
        plt.ylim((0.0, 1.0))
        plt.ylabel(r'$\omega_i^\prime/\omega_0$')
        # plt.legend(loc='best')
        # plt.grid(True)
        plt.tight_layout()
        plt.savefig("media/spectrum_lines.pdf")
        print("Done.")

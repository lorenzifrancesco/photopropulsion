import numpy as np
from dataclasses import dataclass
import toml
from scipy.constants import Boltzmann, c, h
import subprocess


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

    def __init__(self, filename = 'input/params.toml'):
        with open(filename, 'r') as f:
            ff = toml.load(f)
            self.sail_mass = ff['sail_mass']
            self.eta = ff['eta']  # m_payload/m_sail
            self.t_f = ff['t_f']
            self.q_0 = ff['q_0']
            self.sigma = ff['sigma']
            self.p_0 = ff['p_0']
            self.d_sail = ff['d_sail']
            self.d_laser = ff['d_laser']
            self.alpha1 = ff['alpha1']
            self.alpha2 = ff['alpha2']
            self.rust = ff['rust']
            self.lambda_0 = ff['lambda_0']
            self.mode = ff['mode']
        self.alpha = 1.22
        self.file = 'delay.toml'
        self.output_folder = 'results/'

    def get_m(self):
        return (1 + self.eta) * self.sail_mass

    def get_t_rel(self):
        return self.sail_mass * c**2 / self.p_0

    def get_l_rel(self):
        return self.get_t_rel(self) * c

    def get_l_diffraction(self):
        return self.d_sail*self.d_laser/(2*self.alpha / self.lambda_0)

    def get_l_d(self):
        return self.get_l_diffraction(self) / self.get_l_rel(self)

    def get_tf(self):
        return self.t_f/self.get_t_rel(self)
      
    def update(self):
        self.compile(self)
        self.run(self)

    def compile(self):
        rust_compile = 'cargo build --release'
        subprocess.run(rust_compile, shell=True,
                       capture_output=True, text=True)

    def write_config(self, file):
        config = {
            "q":             self.q_0,
            "q_prime":       0.0,
            "p":             1.0,
            "delta":         0.0,
            "t":             0.0,
            "tf":            self.get_t_rel(self),
            "alpha1":        self.alpha1,
            "alpha2":        self.alpha2,
            "l_diffraction": self.get_l_d(self),
            "file":          self.file,
            "mode":          self.mode,
            "output":        self.output_folder
        }
        toml.dump(config, file)

    def run(self):
        result = subprocess.run([self.rust], capture_output=True, text=True)
    
    def show(self):
        # Table headers and layout
        header_width = 35
        value_width = 20
        print("=" * (header_width + value_width))
        print(f"{'Sail Properties':<{header_width}}{'Value':>{value_width}}")
        print("=" * (header_width + value_width))
        print(f"{'Sail Diameter':<{header_width}}{self.d_sail:.2e}")
        print(f"{'Sail Mass':<{header_width}}{self.sail_mass:.2e}")
        print(f"{'Alpha1':<{header_width}}{self.alpha1:.2e}")
        print(f"{'Alpha2':<{header_width}}{self.alpha2:.2e}")
        print(f"{'Payload-to-Sail Mass Ratio (eta)':<{header_width}}{self.eta:.2e}")
        print(f"{'Surface Mass Density (sigma)':<{header_width}}{self.sigma:.2e}")
        
        print("\n" + "=" * (header_width + value_width))
        print(f"{'Laser Properties':<{header_width}}{'Value':>{value_width}}")
        print("=" * (header_width + value_width))
        print(f"{'Laser Diameter':<{header_width}}{self.d_laser:.2e}")
        print(f"{'Laser Wavelength (lambda_0)':<{header_width}}{self.lambda_0:.2e}")
        
        print("\n" + "=" * (header_width + value_width))
        print(f"{'Simulation Settings':<{header_width}}{'Value':>{value_width}}")
        print("=" * (header_width + value_width))
        print(f"{'Final Time (t_f)':<{header_width}}{self.t_f:.2e}")
        print(f"{'Initial Momentum (q_0)':<{header_width}}{self.q_0:.2e}")
        print(f"{'Rust Version':<{header_width}}{self.rust}")
        print(f"{'Mode':<{header_width}}{self.mode}")
        print(f"{'Output File':<{header_width}}{self.file}")
        print(f"{'Output Folder':<{header_width}}{self.output_folder}")
        print("=" * (header_width + value_width))
        
l = Launch()
l.show()
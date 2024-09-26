import numpy as np
from dataclasses import dataclass

@dataclass
class PhysicalParameters:
    ga: float
    sail_mass: float
    eta: float
    tf: float
    q0: float
    sigma: float
    d_sail: float
    d_laser: float
    alpha1: float
    alpha2: float
    def __init__(self, ga: float):
        self.ga = ga

class Launch:
    def __init__(self, ga: float):
        self.parameters = PhysicalParameters(ga)
        self.rust_src = "rust"
    
    def run(self):
        print(f"Running with ga = {self.parameters.ga}")

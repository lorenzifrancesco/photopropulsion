import numpy as np
from scipy.optimize import fsolve, brentq
from scipy.interpolate import interp1d
import numba
from numba import njit
import pandas as pd
import matplotlib.pyplot as plt

# Physical constants
h = 6.62607015e-34  # Planck constant (J⋅s)
c = 299792458       # Speed of light (m/s)
kB = 1.380649e-23   # Boltzmann constant (J/K)

@njit
def planck_spectrum(freq, T):
    """
    Compute Planck spectrum I(ω) = (ℏω³)/(2π²c² * (exp(ℏω/kBT) - 1))
    
    Args:
        freq: frequency in Hz
        T: temperature in K
    
    Returns:
        Planck spectrum intensity
    """
    if T <= 0:
        return 0.0
    
    hf_over_kT = h * freq / (kB * T)
    
    # Avoid overflow for large hf_over_kT
    if hf_over_kT > 700:
        return 0.0
    
    try:
        exp_term = np.exp(hf_over_kT) - 1.0
        if exp_term <= 0:
            return 0.0
        
        return (h * freq**3) / (2 * np.pi**2 * c**2 * exp_term)
    except:
        return 0.0

@njit
def integrand(freq, T, emissivity):
    """
    Compute the integrand: emissivity(freq) * I(freq, T)
    """
    return emissivity * planck_spectrum(freq, T)

@njit
def compute_rhs_integral(T, frequencies, emissivities):
    """
    Compute the RHS integral using trapezoidal rule
    ∫ ε(ω) * I(ω, T) dω
    
    Args:
        T: temperature
        frequencies: array of frequencies
        emissivities: array of emissivity values
    
    Returns:
        Integral value
    """
    n = len(frequencies)
    if n < 2:
        return 0.0
    
    integral = 0.0
    for i in range(n - 1):
        freq1, freq2 = frequencies[i], frequencies[i + 1]
        eps1, eps2 = emissivities[i], emissivities[i + 1]
        
        # Trapezoidal rule
        df = freq2 - freq1
        y1 = integrand(freq1, T, eps1)
        y2 = integrand(freq2, T, eps2)
        integral += 0.5 * df * (y1 + y2)
    
    return integral

class EquilibriumSolver:
    """
    Fast solver for equilibrium temperature condition:
    P_absorbed = 2π * d² * ∫ ε(ω) * I(ω, T) dω
    """
    def __init__(self, frequencies, emissivities, diameter):
        self.frequencies = np.asarray(frequencies, dtype=np.float64)
        self.emissivities = np.asarray(emissivities, dtype=np.float64)
        self.diameter = diameter
        self.coeff = 2 * np.pi * diameter**2
        if not np.all(np.diff(self.frequencies) >= 0):
            sort_idx = np.argsort(self.frequencies)
            self.frequencies = self.frequencies[sort_idx]
            self.emissivities = self.emissivities[sort_idx]
    
    def residual_function(self, T, P_absorbed):
        """
        Compute residual: P_absorbed - 2πd² * ∫ ε(ω) * I(ω, T) dω
        """
        if T <= 0:
            return P_absorbed  # Large positive residual for invalid T
        
        rhs = self.coeff * compute_rhs_integral(T, self.frequencies, self.emissivities)
        return P_absorbed - rhs
    
    def solve_temperature(self, P_absorbed, T_guess=300.0, T_bounds=(1.0, 10000.0)):
        if P_absorbed <= 0:
            return 0.0
        try:
            # Try Brent's method (robust root finding)
            T_solution = brentq(
                lambda T: self.residual_function(T, P_absorbed),
                T_bounds[0], T_bounds[1],
                xtol=1e-6, rtol=1e-6, maxiter=100
            )
            return T_solution

        except ValueError:
            # Fallback to fsolve if brentq fails
            try:
                sol = fsolve(
                    lambda T: self.residual_function(T[0], P_absorbed),
                    [T_guess],
                    xtol=1e-6
                )
                return max(sol[0], 0.0)
            except:
                return T_guess
    
def load_emissivity_data(filename):
    try:
        data = pd.read_csv(filename)
        frequencies = data["x"] * 282e12
        print(f"Loaded {len(frequencies)} frequency-emissivity pairs from {filename}")
        emissivities = data["y"]
    except:
        # Fallback: generate sample data
        frequencies = np.logspace(12, 15, 1000)  # 1 THz to 1000 THz
        emissivities = 0.5 + 0.3 * np.sin(np.log10(frequencies))
        print("Using sample frequency-emissivity data")
    return frequencies, emissivities


if __name__ == "__main__":
    frequencies, emissivities  = load_emissivity_data('input/reflectivity/abs1_f.csv')
    frequencies2, reflectivity = load_emissivity_data('input/reflectivity/M1_f.csv')
    
    diameter = 10
    solver = EquilibriumSolver(frequencies, emissivities, diameter)
    
    freq = 282e12
    ee = interp1d(frequencies, emissivities, bounds_error=False,  fill_value=1e-6)
    rr = interp1d(frequencies2, reflectivity, bounds_error=False, fill_value=1e-6)
    aa = lambda w: (1 - rr(w)) * ee(w)
    temperature = np.logspace(1, 3, 1000)
    P_absorbed = 100e9 * aa(freq)

    plt.semilogx(temperature, list(map(lambda t: solver.residual_function(t, P_absorbed=P_absorbed), temperature)))
    plt.axhline(0, color='black', linestyle='--', linewidth=0.5)
    plt.xlabel('Temperature (K)')
    plt.ylabel('Pout-Pin')
    plt.tight_layout()
    plt.savefig('media/tests/absorption_test.pdf')

    T_equilibrium = solver.solve_temperature(P_absorbed)
    print(f"Equilibrium temperature: {T_equilibrium:.2f} K")
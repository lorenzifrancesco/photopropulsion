import numpy as np
import matplotlib.pyplot as plt

# Constants
h = 6.62607015e-34  # Planck's constant (Joule second)
c = 3e8  # Speed of light in vacuum (m/s)
k_B = 1.380649e-23  # Boltzmann constant (Joule/Kelvin)

# Calculate the Nd:YAG laser emission frequency (for 1064 nm)
lambda_nd_yag = 1064e-9  # Wavelength of Nd:YAG laser (in meters)
freq_nd_yag = c / lambda_nd_yag  # Frequency corresponding to 1064 nm

def planck_spectrum_freq(frequency, temperature):
    """Calculate the spectral radiance of black-body radiation in terms of frequency."""
    intensity = (2 * h * frequency**3) / (c**2) * 1 / (np.exp(h * frequency / (k_B * temperature)) - 1)
    return intensity

# Frequency range (in Hz)
frequencies = np.linspace(1e12, 5e14, 1000)  # e.g., from 1 THz to 1000 THz

# Normalize the frequencies with respect to the Nd:YAG frequency
normalized_frequencies = frequencies / freq_nd_yag
temps = [500, 1000, 1500]  # e.g., temperature of the Sun's surface
plt.figure(figsize=(5, 4))
for temperature in temps:
  intensity = planck_spectrum_freq(frequencies, temperature)
  # Plot the spectrum
  plt.plot(normalized_frequencies, intensity, label=f'T = {temperature} K')

# Add vertical lines at 0.8 and 1.2 times the Nd:YAG frequency
plt.axvline(x=0.8, color='red', linestyle='--', label='0.8 * f$_{Nd:YAG}$')
plt.axvline(x=1.2, color='blue', linestyle='--', label='1.2 * f$_{Nd:YAG}$')

# Add labels and title
plt.title('Planck Spectrum (Normalized by Nd:YAG Frequency)')
plt.xlabel('Normalized Frequency (f / f$_{\mathrm{Nd:YAG}}$)')
plt.ylabel('Spectral Radiance')
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.show()

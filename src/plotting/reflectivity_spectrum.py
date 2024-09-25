import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import UnivariateSpline

def plot_reflectivity_splines_accurate():
    # Wavelength range (zoomed in)
    wavelength = np.linspace(1.04, 1.08, 500)
    
    # Example data points for SiN and BN, approximating the plot shape
    wavelength_points = np.array([1.04, 1.05, 1.06, 1.07, 1.08])
    reflectivity_SiN_points = np.array([0.2, 0.8, 1.0, 0.6, 0.2])
    reflectivity_BN_points = np.array([0.4, 0.85, 0.95, 0.7, 0.3])   
    # Create smooth cubic splines for SiN and BN using UnivariateSpline
    spline_SiN = UnivariateSpline(wavelength_points, reflectivity_SiN_points, s=0.001)
    spline_BN = UnivariateSpline(wavelength_points, reflectivity_BN_points, s=0.001)
    
    # Evaluate the splines on the full wavelength range
    reflectivity_SiN = spline_SiN(wavelength)
    reflectivity_BN = spline_BN(wavelength)
    
    # Plotting the curves
    plt.figure(figsize=(2, 1.5))
    plt.plot(wavelength, reflectivity_SiN, color='red', label=r'\mathrm{Si}_3\mathrm{N}_4')
    # plt.plot(wavelength, reflectivity_BN, color='blue', label='BN')
    
    # Labeling the axes
    plt.xlabel('Wavelength (µm)')
    plt.ylabel('Reflectivity')
    
    # Setting limits for the axes
    plt.xlim(1.04, 1.08)
    plt.ylim(0, 1)
    
    # Adding a legend
    plt.legend()
    
    # Display the plot
    plt.show()

# Call the function to plot
plot_reflectivity_splines_accurate()

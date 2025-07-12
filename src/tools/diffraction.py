import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

# Enable LaTeX rendering
rc('text', usetex=True)
rc('font', family='serif')
def fuu(wsail, wde, lam, lmax):
    pi = np.pi
    phi = 2

    def wbkw(l):
        return wsail * np.sqrt(1 + ((lam * l) / (pi * wsail**2))**2)

    def wbestf(l):
        return lam * l / (pi * wde)

    def wbestb(l):
        return lam * l / (pi * wsail)

    def fbkw(l):
        return 1 - np.exp(-2 * (phi * wde)**2 / wbkw(l)**2)

    def fbestb(l):
        return 1 - np.exp(-2 * (phi * wde)**2 / wbestb(l)**2)

    def nonsense(l):
        # val = ((4*2*np.pi) / (2**(1/2)*2) * (wde * wsail) / (lam * l))**2
        val = 2 * (phi * wsail)**2 / wbestf(l)**2
        val = ((wde * wsail) / (lam * l) * 2**(1/2) * np.pi * phi)**2
        return np.minimum(val, 1)
    
    def nonsense_vero(l):
        # val = ((4*2*np.pi) / (2**(1/2)*2) * (wde * wsail) / (lam * l))**2
        val = 2 * (phi * wsail)**2 / wbestf(l)**2
        val = ((wde * wsail) / (lam * l * 2 * 1.22))**2 # FIXME this was fixed
               
        return np.minimum(val, 1)

    l_vals = np.logspace(9, np.log10(lmax), 500)
    lref = wde * wsail / lam * (2**(3/2) * np.pi)
    y1 = fbestb(l_vals)
    y2 = fbkw(l_vals)

    plt.figure(figsize=(4, 2))
    plt.loglog(l_vals/lref, y1, label='fbestb(l)')
    plt.loglog(l_vals/lref, y2, label='')
    plt.loglog(l_vals/lref, nonsense(l_vals), label='nonsense(l)', linestyle='--')
    plt.loglog(l_vals/lref, nonsense_vero(l_vals), label='nonsense(l)', linestyle='--')
    plt.xlabel(r"$q/q_D$")
    plt.ylabel(r"$F$")
    plt.ylim(1e-4, 1.5)
    plt.tight_layout()
    name = "media/tests/diffraction.pdf"
    plt.savefig(name)
    print(f"Plot saved to {name}")  

fuu(10**4 / 4, 10**3 / 4, 1064e-9, 9e14)

import simulation 
import os
import time

l = simulation.Launch()
l.show()
l.multilayer = simulation.Reflector.M1
l.write_config('input/config.toml')
l.update()
l.plot_dynamics()
l.plot_spectrum(0.01)
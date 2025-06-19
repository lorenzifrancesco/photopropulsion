import simulation
import os
import time

def continuously_update_screen():
    try:
        last_mtime = 0
        while True:
            current_mtime = os.path.getmtime('input/params.toml')
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                os.system('clear')
                l = simulation.Launch()
                l.show()
                l.write_config('input/config.toml')
                # running
                l.update()
                l.plot_dynamics()
                # l.plot_spectrum(threshold=0.001)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopped by user")

if __name__ == "__main__":
    continuously_update_screen()

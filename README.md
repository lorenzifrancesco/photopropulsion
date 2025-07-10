# photopropulsion
A package to solve the relativistic Newton equation of a sail subjected to radiation pressure.
Core numerics (RK4) is made in Rust, and simulation management is done in Python.

```_params.toml``` is utilized to set the SI parameters of the simulation, and ```_config.toml``` is utilized to pass the normalized parameters to the Rust code.

use toml;
use serde::Deserialize;
use std::fs;

#[derive(Debug, Deserialize)]
pub struct Config {
    pub q: f64,
    pub q_prime: f64,
    pub p: f64,
    pub delta: f64,
    pub t: f64,
    pub mode: String,
    pub file: String,
    pub output: String,
    pub tf: f64,
    pub alpha1: f64, // set to 0.0 to enable the reading of the spectrum
    pub alpha2: f64,
    pub cutoff_frequency: f64,
    pub multilayer: String,
    pub diffraction_constant: f64,
    pub sail_diameter: f64,
}

#[derive(Debug, Deserialize)]
pub struct Params {
    pub sail_mass: f64,
    pub eta: f64,
    pub sigma: f64,
    pub d_laser: f64,
    pub alpha1: f64,
    pub alpha2: f64,
    pub cutoff_frequency: f64,
    pub multilayer: i32,
    pub p_0: f64,
    pub t_f: i32,
    pub q_0: f64,
    pub lambda_0: f64,
    pub mode: String,
    pub rust: String,
}

pub fn load_config() -> Config {
let config_content = fs::read_to_string("input/_config.toml").expect("Failed to read config file");
  toml::from_str(&config_content).expect("Failed to parse config file")
}

pub fn load_params() -> Params {
let params_content = fs::read_to_string("input/_params.toml").expect("Failed to read params file");
  toml::from_str(&params_content).expect("Failed to parse params file")  
}
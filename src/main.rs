use std::path::{Path, PathBuf};

use log::Level;
use simple_logger;
use log::{warn, debug};
use toml;
use serde::Deserialize;
use std::fs;

pub mod io;
use crate::io::*;

pub mod solver;
use crate::solver::*; 

const HT: f64 = 0.00001; // Time step


#[derive(Debug, Deserialize)]
struct Config {
    q: f64,
    q_prime: f64,
    p: f64,
    delta: f64,
    t: f64,
    mode: String,
    file: String,
    output: String,
    tf: f64,
    alphart: f64,
    l_diffraction: f64
}

fn load_config() -> Config {
let config_content = fs::read_to_string("input/config.toml").expect("Failed to read config file");
  toml::from_str(&config_content).expect("Failed to parse config file")
}

fn main() {
    simple_logger::init_with_level(Level::Debug).unwrap();
    
    let config = load_config();

    let mut q = config.q;
    let mut q_prime = config.q_prime;
    let mut p= config.p;
    let mut delta = config.delta;
    let mut t = config.t;
    let tf = config.tf;
    let alphart = config.alphart;
    let l_diffraction = config.l_diffraction;
    let threshold = 2e-7; // empirically determined
    let mut status: f64 = -1.0;
    let mut history: Vec<(f64, f64, f64, f64)> = Vec::new();
    let mut results: Vec<(f64, f64, f64, f64)> = Vec::new();
    let mut frequency_range: Vec<f64> = Vec::new();
    let mut power_spectrum: Vec<f64> = Vec::new();
    frequency_range.push(1.0);

    let mode = &config.mode;
    let file = &config.file;
    let mut output: PathBuf = PathBuf::from(&config.output);

    if mode == "lubin" {
      p /= 1.0 - alphart;
    }

    results.push((t, q, q_prime, p));
    while (t < tf) && (q_prime - status > threshold){
        if mode == "delay" {
          if !(t==0.0) {
            let p_past = get_p_past(&history, t);
            delta = get_delta(&history, t);
            if !p_past.is_nan() {
              // multiply here by the D factor and by the diffraction renormalization factor.
              let doppler = (1.0 - q_prime)/(1.0 + q_prime);

              frequency_range.iter_mut().for_each(|freq| *freq *= doppler);
              frequency_range.push(1.0);
              power_spectrum.push(alphart * p_past * doppler);
              // println!("{:?}", frequency_range);
              // println!("{:?}", power_spectrum);

              p = 1.0 + alphart * p_past * doppler;

            } else {
              println!("p_past is NaN");
              p = 1.0;
            }
          }
        }
        if q > l_diffraction {
          p *= (l_diffraction/q).powi(2);
        }
        
        status = q_prime;
        // Compute the next values in a RK4 step
        (q, q_prime) = rk4((q, q_prime), |y| h_dydt(y, p, HT));
        // q = 0.3;
        // q_prime = 0.0;
        t += HT;
        
        // Save to history
        history.push((t, q, q_prime, p));
        #[cfg(debug_assertions)] 
        {
          println!("t={:3.2e}|tau={:3.2e}|q={:3.2e}|p={:3.2e}|Q={:3.2e}|stationary={:3.2e}", t, t-delta, q, p, q_prime, q_prime-status);
        }

        results.push((t, q, q_prime, p));
    }
    if t < tf {
      println!("Terminated as stationary state.")
    } else {
      println!("Terminated by t > tf.")
    }
    // plot_results(&results).expect("Failed to plot results");
    output.push(&file);
    save_results_to_csv(output.as_path(), &results);
    output.set_file_name("spectrum.csv");
    let results_spectrum = vec![frequency_range, power_spectrum];
    save_spectrum_to_csv(output.as_path(), &results_spectrum);
    println!("{}", q_prime);
}
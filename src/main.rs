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
    alpha1: f64, // set to 0.0 to enable the reading of the spectrum
    alpha2: f64,
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
    let mut cnt = 0;
    let tf = config.tf;
    let alpha1 = config.alpha1;
    let alpha2 = config.alpha2;
    let l_diffraction = config.l_diffraction;
    let threshold = 2e-7; // empirically determined
    let mut status: f64 = -1.0;
    let mut history: Vec<(f64, f64, f64, f64)> = Vec::new();
    let mut results: Vec<(f64, f64, f64, f64)> = Vec::new();
    // let n_frequencies = 200;
    // let frequency_range: Vec<f64> = (0..n_frequencies).map(|x| x as f64 /(n_frequencies as f64)).collect();
    let mut power_spectrum: Vec<Vec<(f64, f64)>> = vec![vec![(1.0, 1.0)]];
    // let mut laser_power: Vec<f64> = vec![0.0; n_frequencies];
    // // laser_power[n_frequencies-1] = 1.0;
    // for i in 0..n_frequencies {
    //   laser_power[n_frequencies-1-i] = 1.0 * (-(i as f64).powi(2)/1.0).exp()
    // }
    let alpha1_fun;
    if alpha1 == 0.0 {
      alpha1_fun = linear_interpolator("input/reflectivity/braggSiN.csv").expect("c");
    } else {
      alpha1_fun = constant_interpolator(alpha1).expect("c");
    }
    let alphart = alpha1*alpha2;

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
              power_spectrum.append(&mut vec![get_spectral_components(&power_spectrum, &history, t, &alpha1_fun, alpha2)]);
              p = 0.0;
              for line in power_spectrum[cnt].clone() {
                p += line.1;
              }
              cnt += 1;
            } else {
              println!("p_past is NaN");
              p = 1.0;
            }
          }
        } else {
          p = 1.0;
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
          // println!("t={:3.2e}|tau={:3.2e}|q={:3.2e}|p={:3.2e}|Q={:3.2e}|stationary={:3.2e}", t, t-delta, q, p, q_prime, q_prime-status);
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
    
    if mode=="delay" 
    {
      output.set_file_name("spectrum.csv");
      // println!("Final power spectrum: {:?}", power_spectrum[cnt-1]);
      save_spectral_components_to_csv(output.as_path(), &mut power_spectrum);
    }
    // let results_spectrum = (frequency_range, power_spectrum.clone());
    println!("{}", q_prime);
}
use std::path::{PathBuf};

use log::Level;
use simple_logger;
// use log::{warn, debug};
use toml;
use serde::Deserialize;
use std::fs;

pub mod io;
use crate::io::*;

pub mod solver;
use crate::solver::*;
pub mod thermal;
use crate::thermal::*;

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
    cutoff_frequency: f64,
    multilayer: String,
    diffraction_constant: f64,
    sail_diameter: f64,
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
    let mut th = 1e-20;
    let mut past_temperature = 0.0;
    let mut temperature = 0.0;
    let temperature_stepping_decimation = 10000;
    let mut delta = config.delta;
    let mut t = config.t;
    let mut cnt = 0;
    let tf = config.tf;
    let multilayer = config.multilayer;
    let alpha1 = config.alpha1;
    let alpha2 = config.alpha2;
    let diameter = config.sail_diameter; // FIXME
    let diffraction_constant = config.diffraction_constant;
    let threshold = 0.0; // empirically determined
    let cutoff_frequency = config.cutoff_frequency;
    let mut status: f64 = -1.0;
    let mut history: Vec<(f64, f64, f64, f64)> = Vec::new();
    let mut results: Vec<(f64, f64, f64, f64, f64)> = Vec::new();
    let mut power_spectrum: Vec<Vec<(f64, f64)>> = vec![vec![(1.0, 1.0)]];
    
    let alpha1_fun;
    let alpha2_fun;
    let absor1_fun;
    // in the Cout assumption, absorp1 is only the absorptivity of the emitter structure.
    if cutoff_frequency > 0.0 {
      absor1_fun = step_interpolator(&("input/reflectivity/freq/abs2_step_f.csv"), 0.2, 0.2).expect("c");
      alpha1_fun = step_interpolator(&("input/reflectivity/freq/S_step_f.csv"), 0.5, 0.15).expect("c");
      alpha2_fun = step_interpolator(&("input/reflectivity/freq/DE_step_f.csv"), cutoff_frequency, 0.1).expect("c");
    }
    else {
      absor1_fun = linear_interpolator(&("input/reflectivity/freq/abs2_extended_f.csv")).expect("c");
      if alpha1 == 0.0 {
        alpha1_fun = linear_interpolator(&("input/reflectivity/freq/".to_string() + & multilayer + "_f.csv")).expect("c");
        if multilayer == "FLAT" {
          alpha2_fun = linear_interpolator(&("input/reflectivity/freq/FLAT_f.csv")).expect("c");
        } else {
          alpha2_fun = linear_interpolator(&("input/reflectivity/freq/DE_f.csv")).expect("c");
        }
        print!("{}", & multilayer);
      } else {
        alpha1_fun = constant_interpolator(alpha1).expect("c");
        alpha2_fun = constant_interpolator(alpha2).expect("c");
      }
    }


    let mode = &config.mode;
    println!("Mode: {}", mode);
    let file = &config.file;
    let mut output: PathBuf = PathBuf::from(&config.output);
    let mut diff_factor: f64;

    let alphart = alpha1*alpha2;
    if mode == "lubin" {
      p /= 1.0 - alphart;
    }

    results.push((t, q, q_prime, th, temperature));
    while (t < tf) && (q_prime - status > threshold){
        if mode == "delay" {
          if !(t==0.0) {
            let p_past = get_p_past(&history, t);
            delta = get_delta(&history, t);
            if !p_past.is_nan() {
              // multiply here by the D factor and by the diffraction renormalization factor.
              power_spectrum.append(&mut vec![get_spectral_components(&power_spectrum, 
                &history, 
                t, 
                diffraction_constant,
                &alpha1_fun, 
                &alpha2_fun)]);
              // p = 0.0;
              for line in power_spectrum[cnt].clone() {
                let l_d = diffraction_constant * line.0; 
                if q > l_d {
                  diff_factor = (l_d/q).powi(2);
                } else {
                  diff_factor = 1.0;
                }
              }
              let tmp = get_thrust_and_thermal_power(&power_spectrum.last().expect("power_spectrum has no last!"), 
                &history, 
                t, 
                &alpha1_fun, 
                &absor1_fun);
              p = tmp.0;
              th = tmp.1;
              
              if multilayer != "FLAT" {
                // temperature = solve_temperature(th * 10e9,
                //   diameter,
                //   &absor1_fun, 
                //   1e9,
                //   3e14,
                //   Some(100),
                //   Some(1.0),
                //   Some((0.0, 50000.0))).unwrap_or(-1.0);
                for _i in 0..temperature_stepping_decimation {
                    temperature = step_temperature_euler(th * 50e9,
                      &absor1_fun, 
                      diameter,
                      1e9,
                      3e14,
                      100,
                      past_temperature,
                      HT/temperature_stepping_decimation as f64,
                      1.0).unwrap_or(-1.0);
                    past_temperature = temperature;
                  }
              }
              else {
                temperature = 0.0;
              }
              cnt += 1;
            } else {
              // println!("\np_past is NaN");
              p = 1.0;
            }
          }
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
          println!("t={:3.2e}|tau={:3.2e}|q={:3.2e}|p={:3.2e}|Q={:3.2e}|stat.ty={:3.2e}|temp={:3.2e}|th.pow={:3.2e}", 
          t, 
          t-delta, 
          q, 
          p, 
          q_prime, 
          q_prime-status,
          temperature, 
          th);
        }
        results.push((t, th, q_prime, p, temperature));
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
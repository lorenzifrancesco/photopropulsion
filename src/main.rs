use std::path::Path;

use log::Level;
use simple_logger;
use log::{warn, debug};

pub mod io;
use crate::io::*;

pub mod solver;
use crate::solver::*; 

const HT: f64 = 0.0001; // Time step
const ALPHART: f64 = 0.5; // Example value, adjust as necessary

fn main() {
    simple_logger::init_with_level(Level::Debug).unwrap();
    let mut q = 0.3;
    let mut q_prime = 0.0;
    let mut p = 1.0;
    let mut delta = 0.0;
    let mut t = 0.0;
    let mut history: Vec<(f64, f64, f64, f64)> = Vec::new();
    let mut results: Vec<(f64, f64, f64, f64)> = Vec::new();
    let mode = "delay";
    if mode == "lubin" {
      p /= 1.0 - ALPHART;
    }

    results.push((t, q, q_prime, p));
    while t < 2.5 {
        if mode == "delay" {
          if !(t==0.0) {
            let p_past = get_p_past(&history, t);
            delta = get_delta(&history, t);
            if !p_past.is_nan() {
              p = 1.0 + ALPHART * p_past;
            } else {
              println!("p_past is NaN");
              p = 1.0;
            }
          }
        }

        // Compute the next values in a RK4 step
        (q, q_prime) = rk4((q, q_prime), |y| h_dydt(y, p, HT));
        // q = 0.3;
        // q_prime = 0.0;
        t += HT;
        
        // Save to history
        history.push((t, q, q_prime, p));
        println!("t={:3.2e}|del={:3.2e}|q={:3.2e}|p={:3.2e}|Q={:3.2e}", t, delta, q, p, q_prime);
        results.push((t, q, q_prime, p));
    }
    plot_results(&results).expect("Failed to plot results");
    let output = Path::new("results/results.csv");
    save_results_to_csv(output, &results)
}
use std::{path::Path, process::Output};

use plotters::prelude::*;
use log::{Level, info, warn, error, debug};
use simple_logger;
use csv::Writer;

const HT: f64 = 0.01; // Time step
const ALPHART: f64 = 0.5; // Example value, adjust as necessary

fn h_dydt(y: (f64, f64), p: f64, ht: f64) -> (f64, f64) {
  (ht *y.1, 
  ht *2.0 * p * (1.0 - y.1.powi(2)).powf(3.0/2.0) * (1.0 - y.1) / (1.0 + y.1))
}

// fn dq_dt(q_prime_t: f64) -> f64 {
//     q_prime_t
// }

// fn dq_prime_dt(p: f64, q_prime_t: f64) -> f64 {
//     2.0 * p * (1.0 - q_prime_t.powi(2)).powf(3.0/2.0) * (1.0 - q_prime_t) / (1.0 + q_prime_t)
// }

fn rk4<F>(y: (f64, f64), dydt: F, h: f64) -> (f64, f64)
where
    F: Fn((f64, f64)) -> (f64, f64),
{
    let k1 = dydt(y);
    let k2 = dydt((y.0 + 0.5 * k1.0, 
                              y.1 + 0.5 * k1.1));
    let k3 = dydt((y.0 + 0.5 * k2.0,
                              y.1 + 0.5 * k2.1));
    let k4 = dydt((y.0 + k3.0, y.1 + k3.1));
    (y.0 + (k1.0 + 2.0 * k2.0 + 2.0 * k3.0 + k4.0) / 6.0, y.1 + (k1.1 + 2.0 * k2.1 + 2.0 * k3.1 + k4.1) / 6.0)
}

fn t_segment(history: &Vec<(f64, f64, f64)>, t: f64) -> (usize, usize) {
  let mut cnt: usize = 0;
  let l: usize = history.len();
  while cnt < l-1 {
    if t >= history[cnt].0 && t<history[cnt+1].0 {
      return (cnt, cnt+1);
    }
    cnt += 1;
  }
  (0, 0)
}

// p_q = 1 : select q
// p_q = 2 : select p

fn interpolate(history: &Vec<(f64, f64, f64)>, t: f64, p_q: usize) -> f64 {
  let seg: (usize, usize) = t_segment(history, t);
  let t_prev = history[seg.0].0;
  let t_next = history[seg.1].0;

  let prev = match p_q {
      1 => history[seg.0].1,
      2 => history[seg.0].2,
      _ => panic!("invalid p_q")
  };
  let next = match p_q {
      1 => history[seg.1].1,
      2 => history[seg.1].2,
      _ => panic!("invalid p_q")
  };
  prev + (next - prev) * (t - t_prev) / (t_next - t_prev)
}

fn get_delta(history: &Vec<(f64, f64, f64)>, t: f64) -> f64 {
  let q = history.last().unwrap().1;
  warn!("wrong value of speed");
  let q_past = interpolate(history, t - q, 1);
  println!("delta_eval_point {:3.2e}", t-q);
  debug!("{:3.2e}", 3.0*q - q_past);
  4.0 * q.powi(2) / (3.0*q - q_past)
}

fn get_p_past(history: &Vec<(f64, f64, f64)>, t: f64) -> f64 {
  let delta = get_delta(history, t);
  println!("t = {:3.2e}, delta = {:3.2e}", t, delta);
  interpolate(history, t-delta, 2)
}

fn plot_results(results: &[(f64, f64, f64)]) -> Result<(), Box<dyn std::error::Error>> {
    let root = BitMapBackend::new("media/q_prime.png", (600, 400)).into_drawing_area();
    root.fill(&WHITE)?;

    let mut chart = ChartBuilder::on(&root)
        .caption("", ("sans-serif", 1))
        .margin(10)
        .x_label_area_size(50)
        .y_label_area_size(50)
        .build_cartesian_2d(
            0.0..results.last().unwrap().0,
            results.iter().map(|&(_, q, _)| q).fold(0./0., f64::min)..results.iter().map(|&(_, q, _)| q).fold(0./0., f64::max)
        )?;

    chart.configure_mesh().draw()?;

    chart
        .draw_series(LineSeries::new(
            results.iter().map(|&(t, q, _)| (t, q)),
            &RED,
        ))?
        .label("q(t)")
        .legend(|(x, y)| PathElement::new([(x, y), (x + 20, y)], &RED));

    chart
        .draw_series(LineSeries::new(
            results.iter().map(|&(t, _, q_prime)| (t, q_prime)),
            &BLUE,
        ))?
        .label("Q(t)")
        .legend(|(x, y)| PathElement::new([(x, y), (x + 20, y)], &BLUE));

    chart.configure_series_labels().draw()?;
    Ok(())
}


fn main() {
    simple_logger::init_with_level(Level::Debug).unwrap();
    let mut q = 0.0;
    let mut q_prime = 0.0;
    let mut p = 1.0; 
    let mut t = 0.0; 
    let mut history: Vec<(f64, f64, f64)> = Vec::new();
    let mut results: Vec<(f64, f64, f64)> = Vec::new();

    while t < 2.5 {
        if t != 0.0 {
          let p_past = get_p_past(&history, t);
          if !p_past.is_nan() {
            p = 1.0 + ALPHART * p_past;
          } else {
            println!("p_past is NaN");
            p = 1.0;
          }
        }

        // Compute the next values in a RK4 step
        (q, q_prime) = rk4((q, q_prime), |y| h_dydt(y, p, HT), HT);

        // Save to history
        history.push((t, q, p));
        println!("t = {:3.2e}| q = {:3.2e}| p = {:3.2e}|  Q = {:3.2e}", t, q, p, q_prime);
        results.push((t, q, q_prime));

        t += HT;
    }
    plot_results(&results).expect("Failed to plot results");
    let output = Path::new("results/results.csv");
    save_results_to_csv(output, &results)
}

fn save_results_to_csv(output: &Path, y: &Vec<(f64, f64, f64)>) {
  // Create a CSV writer
  let mut writer = Writer::from_path(output).expect("Failed to create a CSV Writer");

  // Write the header
  let header = vec!["Time".to_string(), "q".to_string(), "Q".to_string()];
  writer.write_record(&header).expect("Failed writing header");
  let steps = y.len();
  // Write the rows
  let mut row = vec![3.to_string(); 3]; 
  for i in 0..steps {
      row[0] = y[i].0.to_string();
      row[1] = y[i].1.to_string();
      row[2] = y[i].2.to_string();
      writer.write_record(&row).expect("Failed to write row");
  }

  // Flush the writer
  writer.flush().expect("Failed to write the buffer");
}
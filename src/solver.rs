use log::{info, warn, error, debug};

pub fn h_dydt(y: (f64, f64), p: f64, ht: f64) -> (f64, f64) {
  (ht *y.1, 
  ht *2.0 * p * (1.0 - y.1.powi(2)).powf(3.0/2.0) * (1.0 - y.1) / (1.0 + y.1))
}

// fn dq_dt(q_prime_t: f64) -> f64 {
//     q_prime_t
// }

// fn dq_prime_dt(p: f64, q_prime_t: f64) -> f64 {
//     2.0 * p * (1.0 - q_prime_t.powi(2)).powf(3.0/2.0) * (1.0 - q_prime_t) / (1.0 + q_prime_t)
// }

pub fn rk4<F>(y: (f64, f64), hdydt: F) -> (f64, f64)
where
    F: Fn((f64, f64)) -> (f64, f64),
{
    let k1 = hdydt(y);
    let k2 = hdydt((y.0 + 0.5 * k1.0, 
                              y.1 + 0.5 * k1.1));
    let k3 = hdydt((y.0 + 0.5 * k2.0,
                              y.1 + 0.5 * k2.1));
    let k4 = hdydt((y.0 + k3.0, y.1 + k3.1));
    (y.0 + (k1.0 + 2.0 * k2.0 + 2.0 * k3.0 + k4.0) / 6.0, y.1 + (k1.1 + 2.0 * k2.1 + 2.0 * k3.1 + k4.1) / 6.0)
}

pub fn get_p_past(history: &Vec<(f64, f64, f64)>, t: f64) -> f64 {
  let delta = get_delta(history, t);
  println!("t = {:3.2e}, delta = {:3.2e}", t, delta);
  interpolate(history, t-delta, 2)
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


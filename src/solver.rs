use log::{debug, warn};

pub const HT: f64 = 0.000001; // Time step

pub fn h_dydt(y: (f64, f64), p: f64, ht: f64) -> (f64, f64) {
    (
        ht * y.1,
        ht * 2.0 * p * (1.0 - y.1.powi(2)).powf(3.0 / 2.0) * (1.0 - y.1) / (1.0 + y.1),
    )
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
    let k2 = hdydt((y.0 + 0.5 * k1.0, y.1 + 0.5 * k1.1));
    let k3 = hdydt((y.0 + 0.5 * k2.0, y.1 + 0.5 * k2.1));
    let k4 = hdydt((y.0 + k3.0, y.1 + k3.1));
    (
        y.0 + (k1.0 + 2.0 * k2.0 + 2.0 * k3.0 + k4.0) / 6.0,
        y.1 + (k1.1 + 2.0 * k2.1 + 2.0 * k3.1 + k4.1) / 6.0,
    )
}

pub fn get_p_past(history: &Vec<(f64, f64, f64, f64)>, t: f64) -> f64 {
    let delta = get_delta(history, t);
    // println!("t = {:3.2e}, delta = {:3.2e}", t, delta);
    if t - delta < 0.0 {
        0.0
    } else {
        interpolate(history, t - delta, 2)
    }
}

pub fn get_spectral_components(
    power_spectrum: &Vec<Vec<(f64, f64)>>,
    history: &Vec<(f64, f64, f64, f64)>,
    t: f64,
    diffraction_constant:f64, 
    alpha1: &Box<dyn Fn(f64) -> f64>,
    alpha2: &Box<dyn Fn(f64) -> f64>,
) -> Vec<(f64, f64)> {
    let mut new_power_spectrum: Vec<(f64, f64)> = vec![];
    let delta = get_delta(history, t);
    if t - delta < 0.0 {
        vec![(1.0, 1.0)]
    } else {
        let q_prime_old = interpolate(history, t - delta, 3);
        let q_old = interpolate(history, t - delta, 1);
        let doppler = (1.0 - q_prime_old) / (1.0 + q_prime_old);
        let sqrt_doppler = doppler.sqrt();
        // println!("{}", doppler);
        let idx = ((t - delta) / HT).floor() as usize;
        let reflected_spectrum: Vec<(f64, f64)>;
        if !(idx >= power_spectrum.len()) {
            reflected_spectrum = power_spectrum[idx].clone();
        } else {
            reflected_spectrum = power_spectrum
                .last()
                .expect("power_spectrum has no last!")
                .clone();
        }
        let mut diff_factor;
        for line in reflected_spectrum {
            let l_d = diffraction_constant * line.0; 
            if q_old > l_d {
              diff_factor = (l_d/q_old).powi(2);
            } else {
              diff_factor = 1.0;
            }
            new_power_spectrum.append(&mut vec![(
                (line.0 * doppler),
                (diff_factor * line.1 * doppler * (alpha1(line.0 * sqrt_doppler) * alpha2(line.0))),
            )]);
            // new_power_spectrum.append((1.1, 1.2));
        }
        new_power_spectrum.append(&mut vec![(1.0, 1.0)]);
        new_power_spectrum
    }
}

pub fn get_spectrum_past<'a>(
    power_spectrum: &'a Vec<Vec<f64>>,
    history: &Vec<(f64, f64, f64, f64)>,
    t: f64,
) -> Vec<f64> {
    let n = power_spectrum[0].len();
    let delta = get_delta(history, t);
    if t - delta < 0.0 {
        vec![0.0; n]
    } else {
        power_spectrum[((t - delta) / HT).floor() as usize].clone()
    }
}

pub fn get_delta(history: &Vec<(f64, f64, f64, f64)>, _t: f64) -> f64 {
    let q = history.last().unwrap().1;
    let q_prime = history.last().unwrap().2;
    // old approach using the first iteration of the numerical approximation of (deltina)
    // warn!("wrong value of speed");
    // let q_past = interpolate(history, t - 2.0*q, 1);
    // println!("delta_eval_point {:3.2e}", t-2.0*q);
    // debug!("{:3.2e}", 3.0*q - q_past);
    // 4.0 * q.powi(2) / (3.0*q - q_past)
    2.0 * q / (1.0 + q_prime)
}

fn t_segment(history: &Vec<(f64, f64, f64, f64)>, t: f64) -> (usize, usize) {
    let mut cnt: usize = 0;
    let l: usize = history.len();
    while cnt < l - 1 {
        if t >= history[cnt].0 && t < history[cnt + 1].0 {
            return (cnt, cnt + 1);
        }
        cnt += 1;
    }
    (0, 0)
}

// p_q = 1 : select q
// p_q = 2 : select p
// p_q = 3 : select q_prime
fn interpolate(history: &Vec<(f64, f64, f64, f64)>, t: f64, p_q: usize) -> f64 {
    let seg: (usize, usize) = t_segment(history, t);
    let t_prev = history[seg.0].0;
    let t_next = history[seg.1].0;

    let prev = match p_q {
        1 => history[seg.0].1,
        2 => history[seg.0].3,
        3 => history[seg.0].2,
        _ => panic!("invalid p_q"),
    };
    let next = match p_q {
        1 => history[seg.1].1,
        2 => history[seg.1].3,
        3 => history[seg.1].2,
        _ => panic!("invalid p_q"),
    };
    prev + (next - prev) * (t - t_prev) / (t_next - t_prev)
}

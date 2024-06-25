use plotters::prelude::*;

const HT: f64 = 0.01; // Time step
// const ALPHA1: f64 = 0.5; // Example value, adjust as necessary
// const ALPHA2: f64 = 0.5; // Example value, adjust as necessary
// const TAU: f64 = 0.1; // Delay

fn dq_dt(q_prime_t: f64) -> f64 {
    q_prime_t
}

fn dq_prime_dt(p: f64, q_prime_t: f64) -> f64 {
    2.0 * p * (1.0 - q_prime_t.powi(2)).powi(3/2) * (1.0 - q_prime_t) / (1.0 + q_prime_t)
}

// fn interpolate(delayed_q: f64, q_prev: f64, q_next: f64, t_prev: f64, t_next: f64, t: f64) -> f64 {
//     q_prev + (q_next - q_prev) * (t - t_prev) / (t_next - t_prev)
// }

fn rk4<F>(y: f64, dydt: F, h: f64) -> f64
where
    F: Fn(f64) -> f64,
{
    let k1 = h * dydt(y);
    let k2 = h * dydt(y + 0.5 * k1);
    let k3 = h * dydt(y + 0.5 * k2);
    let k4 = h * dydt(y + k3);
    y + (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
}

// fn find_interpolation_points(history: &Vec<(f64, f64)>, t: f64) -> (f64, f64, f64, f64) {
//     let mut q_prev = 0.0;
//     let mut t_prev = 0.0;
//     let mut q_next = 0.0;
//     let mut t_next = 0.0;
    
//     for &(HT, hq) in history.iter() {
//         if HT <= t {
//             t_prev = HT;
//             q_prev = hq;
//         } else {
//             t_next = HT;
//             q_next = hq;
//             break;
//         }
//     }
//     (q_prev, t_prev, q_next, t_next)
// }

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
    let mut q = 0.0;
    let mut q_prime = 0.0;
    let mut p = 1.0; 
    let mut t = 0.0; 
    // let mut history: Vec<(f64, f64)> = Vec::new();
    let mut results: Vec<(f64, f64, f64)> = Vec::new();

    while t < 2.5 {
        // Compute
        // let delayed_t = t - TAU;
        // if delayed_t >= 0.0 {
        //     let (q_prev, t_prev, q_next, t_next) = find_interpolation_points(&history, delayed_t);
        //     let delayed_q = interpolate(delayed_t, q_prev, q_next, t_prev, t_next, t);
        //     p = ALPHA1 * ALPHA2 * p + delayed_q; // Example update, adjust as necessary
        // }

        // Compute the next values in a RK4 step
        q_prime = rk4(q_prime, |q| dq_prime_dt(p, q), HT);
        q = rk4(q, |q| dq_dt(q_prime), HT);

        // Save to history
        // history.push_back((t, q));
        println!("t = {:3.2e}, Q = {:3.2e}", t, q_prime);
        results.push((t, q_prime, q_prime));

        t += HT;
    }
    plot_results(&results).expect("Failed to plot results");
}

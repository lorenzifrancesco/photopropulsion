use std::f64::consts::PI;
// Add to Cargo.toml: roots = "0.0.8"
use roots::{find_root_brent, Convergency, SimpleConvergency};

// Physical constants
const H_PLANCK: f64 = 6.62607015e-34;  // Planck constant (J⋅s)
const C_LIGHT: f64 = 299792458.0;       // Speed of light (m/s)
const K_BOLTZMANN: f64 = 1.380649e-23;  // Boltzmann constant (J/K)
const F0: f64 = 2.819e14;

/// Compute Planck spectrum: I(ω) = (ℏω³)/(2π²c² * (exp(ℏω/kBT) - 1))
#[inline]
fn planck_spectrum(frequency: f64, temperature: f64) -> f64 {
    if temperature <= 0.0 {
        return 0.0;
    }

    let hf_over_kt = H_PLANCK * frequency / (K_BOLTZMANN * temperature);

    // Avoid overflow for large hf_over_kt
    if hf_over_kt > 700.0 {
        return 0.0;
    }

    let exp_term = hf_over_kt.exp() - 1.0;
    if exp_term <= 0.0 {
        return 0.0;
    }

    (H_PLANCK * frequency.powi(3)) / (2.0 * PI * PI * C_LIGHT * C_LIGHT * exp_term)
}

/// Compute RHS integral using adaptive quadrature
#[inline]
fn compute_rhs_integral<F>(
    temperature: f64,
    emissivity_fn: &F,
    freq_min: f64,
    freq_max: f64,
    n_points: usize,
) -> f64
where
    F: Fn(f64) -> f64,
{
    if n_points < 2 {
        return 0.0;
    }

    // Log-spaced frequency grid for better sampling
    let log_min = freq_min.ln();
    let log_max = freq_max.ln();
    let dlog = (log_max - log_min) / (n_points - 1) as f64;

    let mut integral = 0.0;
    let mut prev_freq = freq_min;
    let mut prev_integrand = emissivity_fn(freq_min/F0) * planck_spectrum(freq_min, temperature);

    for i in 1..n_points {
        let log_freq = log_min + i as f64 * dlog;
        let freq = log_freq.exp();
        let integrand = emissivity_fn(freq/F0) * planck_spectrum(freq, temperature);

        // Trapezoidal rule
        let df = freq - prev_freq;
        integral += 0.5 * df * (prev_integrand + integrand);

        prev_freq = freq;
        prev_integrand = integrand;
    }

    integral
}

/// Residual function for root finding
#[inline]
fn residual_function<F>(
    temperature: f64,
    p_absorbed: f64,
    emissivity_fn: &F,
    coefficient: f64,
    freq_min: f64,
    freq_max: f64,
    n_points: usize,
) -> f64
where
    F: Fn(f64) -> f64,
{
    if temperature <= 0.0 {
        return p_absorbed;
    }

    let rhs = coefficient * compute_rhs_integral(temperature, emissivity_fn, freq_min, freq_max, n_points);
    p_absorbed - rhs
}

fn find_temperature_root<F>(
    p_absorbed: f64,
    emissivity_fn: &F,
    coefficient: f64,
    freq_min: f64,
    freq_max: f64,
    n_points: usize,
    t_min: f64,
    t_max: f64,
    tolerance: f64,
) -> Option<f64>
where
    F: Fn(f64) -> f64,
{
    let residual = |t: f64| -> f64 {
        residual_function(t, p_absorbed, emissivity_fn, coefficient, freq_min, freq_max, n_points)
    };
    let mut convergency = SimpleConvergency { eps: tolerance, max_iter: 10000 };
    let convergency_trait: &mut dyn Convergency<f64> = &mut convergency;
    
    match find_root_brent(t_min, t_max, &residual, convergency_trait) {
        Ok(root) => Some(root),
        Err(_) => None,
    }
}

/// Solve for equilibrium temperature given absorbed power
/// 
/// Solves: P_absorbed = 2πd² ∫ ε(ω) * I(ω, T) dω
/// 
/// # Arguments
/// * `p_absorbed` - Absorbed power in Watts
/// * `diameter` - Sail diameter in meters  
/// * `emissivity_fn` - Function that returns emissivity for given frequency (Hz)
/// * `freq_min` - Minimum frequency for integration (Hz)
/// * `freq_max` - Maximum frequency for integration (Hz)
/// * `n_points` - Number of integration points (default: 1000)
/// * `tolerance` - Convergence tolerance (default: 1e-6)
/// * `t_bounds` - Temperature search bounds (T_min, T_max) in K (default: (1.0, 10000.0))
/// 
/// # Returns
/// * `Option<f64>` - Equilibrium temperature in K, or None if no solution found
/// 
/// # Example
/// ```rust
/// // Linear emissivity function
/// let emissivity = |freq: f64| 0.5 + 0.3 * (freq / 1e13);
/// 
/// let temperature = solve_temperature(
///     1e-12,           // 1 pW absorbed power
///     1e-6,            // 1 micrometer diameter
///     &emissivity,     // emissivity function
///     1e12,            // 1 THz min frequency
///     1e15,            // 1000 THz max frequency
///     Some(1000),      // integration points
///     Some(1e-6),      // tolerance
///     Some((1.0, 10000.0)), // temperature bounds
/// );
/// ```
pub fn solve_temperature<F>(
    p_absorbed: f64,
    diameter: f64,
    emissivity_fn: &F,
    freq_min: f64,
    freq_max: f64,
    n_points: Option<usize>,
    tolerance: Option<f64>,
    t_bounds: Option<(f64, f64)>,
) -> Option<f64>
where
    F: Fn(f64) -> f64,
{
    if p_absorbed <= 0.0 {
        return Some(0.0);
    }

    if diameter <= 0.0 || freq_min >= freq_max {
        return None;
    }

    let n_points = n_points.unwrap_or(1000);
    let tolerance = tolerance.unwrap_or(1e-6);
    let (t_min, t_max) = t_bounds.unwrap_or((1.0, 10000.0));

    let coefficient = 2.0 * PI * diameter * diameter;
    let ftr = find_temperature_root(
        p_absorbed,
        emissivity_fn,
        coefficient,
        freq_min,
        freq_max,
        n_points,
        t_min,
        t_max,
        tolerance,
    );
    // println!("Temperature found: {:?}", ftr);
    ftr
}

#[cfg(test)]
mod tests {
    use crate::io::{constant_interpolator, linear_interpolator};

    use super::*;
    
    #[test]
    fn test_solve_temperature() {
        // Linear emissivity function
        // let emissivity = |freq: f64| 0.5 + 0.3 * (freq / 1e13);
        let emissivity = linear_interpolator("input/reflectivity/freq/simple.csv")
            .expect("Failed to create linear interpolator");
        let temperature = solve_temperature(
            1e-6*50e9,          
            10.0,            
            &emissivity,
            1e10,
            1e15,
            Some(1000),
            Some(1e-6),
            Some((1.0, 10000.0)),
        );
        println!("Computed temperature: {:?}", temperature);
        assert!(temperature.is_some());
        assert!(temperature.unwrap() > 0.0);
    }
}
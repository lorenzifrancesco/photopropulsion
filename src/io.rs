
use csv::Writer;
use std::path::Path;
use std::error::Error;
use csv::ReaderBuilder;
pub fn save_results_to_csv(output: &Path, y: &Vec<(f64, f64, f64, f64, f64)>) {
  // Create a CSV writer
  let mut writer = Writer::from_path(output).expect("Failed to create a CSV Writer");

  // Write the header
  let header = vec!["Time".to_string(), "q".to_string(), "Q".to_string(), "P".to_string(), "T".to_string()];
  writer.write_record(&header).expect("Failed writing header");
  let steps = y.len();
  // Write the rows
  let mut row = vec!["ciao".to_string(); 5]; 
  for i in 0..steps {
      row[0] = y[i].0.to_string();
      row[1] = y[i].1.to_string();
      row[2] = y[i].2.to_string();
      row[3] = y[i].3.to_string();
      row[4] = y[i].4.to_string();
      writer.write_record(&row).expect("Failed to write row");
  }

  // Flush the writer
  writer.flush().expect("Failed to write the buffer");
}

pub fn save_spectrum_to_csv(output: &Path, y: &(Vec<f64>, Vec<Vec<f64>>)) {
  // Create a CSV writer
  let mut writer = Writer::from_path(output).expect("Failed to create a CSV Writer");

  // Write the header
  let header: Vec<String> = (0..y.0.len()).map(|i| format!("Frequency {}", i)).collect();
  writer.write_record(&header).expect("Failed to write header");

  let steps = y.1.len();
  let n_frequencies = y.0.len();
  // Write the rows
  let mut row = vec!["ciao".to_string(); n_frequencies]; 
  for i in 0..steps {
      for j in 0..n_frequencies {
      row[j] = (y.1)[i][j].to_string();
      }
      writer.write_record(&row).expect("Failed to write row");
  }

  // Flush the writer
  writer.flush().expect("Failed to write the buffer");
}

pub fn save_spectral_components_to_csv(output: &Path, y: &mut Vec<Vec<(f64, f64)>>) {
  // Create a CSV writer
  let mut writer = Writer::from_path(output).expect("Failed to create a CSV Writer");
  let maximum_n_lines = y.last().expect("defective spectrum").len();
  let n_steps = y.len();
for i in 0..y.len() {
        let mut padded = vec![(0.0, 0.0); maximum_n_lines];
        let start_index = maximum_n_lines - y[i].len();
        padded[start_index..].copy_from_slice(&y[i]);
        y[i] = padded;
  }
  // Write the header
  let header: Vec<String> = (0..maximum_n_lines).map(|i| format!("f {}", i)).collect();
  writer.write_record(&header).expect("Failed to write header");

  // Write the rows
  let mut row = vec!["ciao".to_string(); maximum_n_lines]; 
  for i in 0..n_steps {
      for j in 0..maximum_n_lines {
      row[j] = (y[i])[j].0.to_string();
      }
      writer.write_record(&row).expect("Failed to write frequency row");
      for j in 0..maximum_n_lines {
      row[j] = (y[i])[j].1.to_string();
      }
      writer.write_record(&row).expect("Failed to write power row");
  }

  // Flush the writer
  writer.flush().expect("Failed to write the buffer");
}


type DataPoint = (f64, f64);

fn read_reflectivity_from_csv(file_path: &str) -> Result<Vec<DataPoint>, Box<dyn Error>> {
    let mut rdr = ReaderBuilder::new().from_path(file_path)?;
    let mut data_points = Vec::new();

    for result in rdr.records() {
        let record = result?;
        let x: f64 = record[0].parse()?;
        let y: f64 = record[1].parse()?;
        data_points.push((x, y));
    }

    data_points.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());

    Ok(data_points)
}


pub fn linear_interpolator(file_path: &str) -> Result<Box<dyn Fn(f64) -> f64>, Box<dyn Error>> {
  let data_points = read_reflectivity_from_csv(file_path)?;

  let interpolator = move |x: f64| -> f64 {
      if data_points.is_empty() {
          panic!("No data points available for interpolation");
      }
      // If x is out of bounds, extrapolate using the first/last segment
      if x <= data_points[0].0 {
          let (x0, y0) = data_points[0];
          let (x1, y1) = data_points[1];
          let result = y0 + (x - x0) * (y1 - y0) / (x1 - x0);
          if result > 0.0 {
            return result
          } else{
              return 0.0
          }
      }
      if x >= data_points[data_points.len() - 1].0 {
          let (x0, y0) = data_points[data_points.len() - 2];
          let (x1, y1) = data_points[data_points.len() - 1];
          let result = y0 + (x - x0) * (y1 - y0) / (x1 - x0);
          if result > 0.0 {
            return result
          } else{
              return 0.0
          }
      }

      // Find the interval [x0, x1] where x0 <= x <= x1
      for i in 0..data_points.len() - 1 {
          let (x0, y0) = data_points[i];
          let (x1, y1) = data_points[i + 1];

          if x0 <= x && x <= x1 {
              return y0 + (x - x0) * (y1 - y0) / (x1 - x0);
          }
      }

      unreachable!()
  };

  Ok(Box::new(interpolator))
}

pub fn constant_interpolator(value: f64) -> Result<Box<dyn Fn(f64) -> f64>, Box<dyn Error>> {
  let interpolator = move |_x_: f64| -> f64 {
    value
  };
  Ok(Box::new(interpolator))
}
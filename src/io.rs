
use csv::Writer;
use plotters::prelude::*;
use std::path::Path;

pub fn plot_results(results: &Vec<(f64, f64, f64, f64)>) -> Result<(), Box<dyn std::error::Error>> {
  let root = BitMapBackend::new("media/q_prime.png", (600, 400)).into_drawing_area();
  root.fill(&WHITE)?;

  let mut chart = ChartBuilder::on(&root)
      .caption("", ("sans-serif", 1))
      .margin(10)
      .x_label_area_size(50)
      .y_label_area_size(50)
      .build_cartesian_2d(
          0.0..results.last().unwrap().0,
          results.iter().map(|&(t, _, _, _)| t).fold(0./0., f64::min)..results.iter().map(|&(t, _, _, _)| t).fold(0./0., f64::max),
      )?;

  chart.configure_mesh().draw()?;

  chart
      .draw_series(LineSeries::new(
          results.iter().map(|&(t, q, _, _)| (t, q)),
          &RED,
      ))?
      .label("q(t)")
      .legend(|(x, y)| PathElement::new([(x, y), (x + 20, y)], &RED));

  chart
      .draw_series(LineSeries::new(
          results.iter().map(|&(t, _, q_prime, _)| (t, q_prime)),
          &BLUE,
      ))?
      .label("Q(t)")
      .legend(|(x, y)| PathElement::new([(x, y), (x + 20, y)], &BLUE));

  chart
      .draw_series(LineSeries::new(
          results.iter().map(|&(t, _, _, fourth_value)| (t, fourth_value)),
          &GREEN,
      ))?
      .label("Fourth Value")
      .legend(|(x, y)| PathElement::new([(x, y), (x + 20, y)], &GREEN));

  chart.configure_series_labels().draw()?;
  Ok(())
}

pub fn save_results_to_csv(output: &Path, y: &Vec<(f64, f64, f64, f64)>) {
  // Create a CSV writer
  let mut writer = Writer::from_path(output).expect("Failed to create a CSV Writer");

  // Write the header
  let header = vec!["Time".to_string(), "q".to_string(), "Q".to_string(), "P".to_string()];
  writer.write_record(&header).expect("Failed writing header");
  let steps = y.len();
  // Write the rows
  let mut row = vec!["ciao".to_string(); 4]; 
  for i in 0..steps {
      row[0] = y[i].0.to_string();
      row[1] = y[i].1.to_string();
      row[2] = y[i].2.to_string();
      row[3] = y[i].3.to_string();
      writer.write_record(&row).expect("Failed to write row");
  }

  // Flush the writer
  writer.flush().expect("Failed to write the buffer");
}

pub fn save_spectrum_to_csv(output: &Path, y: &Vec<Vec<f64>>) {
  // Create a CSV writer
  let mut writer = Writer::from_path(output).expect("Failed to create a CSV Writer");

  // Write the header
  let header = vec!["F".to_string(), "P".to_string()];
  writer.write_record(&header).expect("Failed writing header");
  let steps = y[0].len();
  // Write the rows
  let mut row = vec!["ciao".to_string(); 2]; 
  for i in 0..steps {
      row[0] = y[0][i].to_string();
      row[1] = y[1][i].to_string();
      writer.write_record(&row).expect("Failed to write row");
  }

  // Flush the writer
  writer.flush().expect("Failed to write the buffer");
}
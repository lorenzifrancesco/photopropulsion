#! /bin/bash
echo "==== running...  ===="
cargo run
echo "==== plotting... ===="
python src/spectral_components.py
python src/plotter.py
echo "====    done     ===="
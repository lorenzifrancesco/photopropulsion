#! /bin/bash
echo "==== running...  ===="
cargo run
echo "==== plotting... ===="
python src/plotter.py
echo "====    done     ===="
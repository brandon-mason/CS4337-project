#!/bin/bash
# Activation script for the Sheet Music Player virtual environment

echo "Activating Sheet Music Player virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated!"
echo ""
echo "Available commands:"
echo "  python main.py                           # Run demo mode"
echo "  python test_sheet_music.py               # Generate test images"
echo "  python main.py your_sheet_music.png      # Play sheet music from image"
echo "  python example_usage.py                  # Run example usage"
echo ""
echo "To deactivate, run: deactivate"

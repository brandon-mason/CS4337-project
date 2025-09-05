#!/bin/bash
# Activation script for the Sheet Music Player virtual environment

echo "Activating Sheet Music Player virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated!"
echo ""
echo "Available commands:"
echo "  python main.py                           # Run demo mode"
echo "  python main.py your_sheet_music.png      # Play sheet music from image"
echo "  python gradio_interface.py               # Run Gradio interface"
echo ""
echo "To deactivate, run: deactivate"

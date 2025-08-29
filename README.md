# Computer Vision Sheet Music Player

A Python-based computer vision project that reads clean, computer-generated sheet music and plays it using FluidSynth. The system can recognize and play whole notes, half notes, quarter notes, eighth notes, and sixteenth notes.

## Features

- **Computer Vision**: Uses OpenCV for image processing and music notation detection
- **Note Recognition**: Detects musical notes from whole notes to sixteenth notes
- **Audio Playback**: Uses FluidSynth for high-quality MIDI audio synthesis
- **Staff Detection**: Automatically detects staff lines and maps note positions
- **Flexible Tempo**: Adjustable playback tempo (beats per minute)
- **Multiple Note Types**: Supports various note durations and positions

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- FluidSynth
- A SoundFont file (.sf2) for audio synthesis

## Installation

1. **Clone or download this project**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FluidSynth system dependencies**:

   **On macOS**:
   ```bash
   brew install fluid-synth
   ```

   **On Ubuntu/Debian**:
   ```bash
   sudo apt-get install fluidsynth
   ```

   **On Windows**:
   Download FluidSynth from the official website or use a package manager like Chocolatey.

4. **Download a SoundFont file** (optional):
   - Download a free SoundFont like "FluidR3_GM.sf2"
   - Place it in the project directory or specify the path when running

## Usage

### Basic Usage

1. **Generate test sheet music** (for testing):
   ```bash
   python test_sheet_music.py
   ```

2. **Run the demo** (plays a C major scale):
   ```bash
   python main.py
   ```

3. **Play sheet music from an image**:
   ```bash
   python main.py your_sheet_music.png
   ```

### Advanced Usage

**Specify tempo**:
```bash
python main.py sheet_music.png --tempo 140
```

**Use a custom SoundFont**:
```bash
python main.py sheet_music.png --soundfont /path/to/your/soundfont.sf2
```

**Enable debug mode**:
```bash
python main.py sheet_music.png --debug
```

### Command Line Options

- `image_path`: Path to the sheet music image file
- `--tempo`: Tempo in beats per minute (default: 120)
- `--soundfont`: Path to SoundFont file (.sf2)
- `--debug`: Enable debug mode with additional logging

## How It Works

### 1. Image Preprocessing
- Converts image to grayscale
- Applies Gaussian blur to reduce noise
- Uses adaptive thresholding for better contrast
- Performs morphological operations to clean up the image

### 2. Staff Line Detection
- Uses Hough Line Transform to detect horizontal lines
- Groups nearby lines to identify the five staff lines
- Calculates staff spacing for note positioning

### 3. Note Detection
- Finds contours in the processed image
- Filters by size to identify note heads
- Analyzes fill ratio to determine note duration:
  - Hollow circles = whole notes
  - Partially filled = half notes
  - Solid circles = quarter/eighth/sixteenth notes

### 4. Note Mapping
- Maps y-positions to musical notes based on staff lines
- Supports notes from C4 to C6 (treble clef range)
- Determines note duration based on visual characteristics

### 5. Audio Playback
- Uses FluidSynth for MIDI synthesis
- Plays notes with appropriate durations
- Supports adjustable tempo

## Supported Note Types

| Note Type | Duration | Visual Characteristics |
|-----------|----------|----------------------|
| Whole Note | 4 beats | Hollow circle, no stem |
| Half Note | 2 beats | Hollow circle with stem |
| Quarter Note | 1 beat | Solid circle with stem |
| Eighth Note | 0.5 beats | Solid circle with stem and flag |
| Sixteenth Note | 0.25 beats | Solid circle with stem and double flag |

## Supported Notes

The system currently supports notes in the treble clef range:
- C4, D4, E4, F4, G4, A4, B4
- C5, D5, E5, F5, G5, A5, B5
- C6

## File Structure

```
project/
├── sheet_music_player.py    # Main player class
├── main.py                  # Command line interface
├── test_sheet_music.py      # Test image generator
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── test_sheet_music_*.png  # Generated test images
```

## Troubleshooting

### Common Issues

1. **"No SoundFont found" warning**:
   - Download a SoundFont file (.sf2) and specify the path
   - Common free SoundFonts: FluidR3_GM.sf2, GeneralUser GS v1.471.sf2

2. **"No staff lines detected"**:
   - Ensure the image has clear, horizontal staff lines
   - Try adjusting image contrast or using a cleaner image
   - The system works best with computer-generated sheet music

3. **"No notes detected"**:
   - Check that notes are clearly visible and properly sized
   - Ensure notes are positioned on or near staff lines
   - Try the test images first to verify the system works

4. **Audio not playing**:
   - Verify FluidSynth is properly installed
   - Check that a SoundFont is loaded
   - Ensure your system's audio is working

### Performance Tips

- Use high-resolution, clean images for best results
- Ensure good contrast between notes and background
- Computer-generated sheet music works better than handwritten
- Avoid complex backgrounds or watermarks

## Limitations

- Currently optimized for treble clef only
- Works best with computer-generated sheet music
- Limited to single-line melodies (no chords)
- Requires clear, well-formatted sheet music
- Note detection accuracy depends on image quality

## Future Enhancements

- Support for bass clef and other clefs
- Chord recognition and playback
- Time signature detection
- Dynamic and articulation recognition
- Support for handwritten sheet music
- Real-time sheet music processing

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the project.

## License

This project is open source and available under the MIT License.

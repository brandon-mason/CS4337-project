# Computer Vision Sheet Music Player

A Python-based computer vision project that reads clean, computer-generated sheet music and exports it to midi and audio. The system can recognize and play quarter notes, with plans to add whole notes, half notes, eighth notes, and sixteenth notes.

## Features

- **Computer Vision**: Uses OpenCV for image processing and music notation detection
- **Note Recognition**: Detects musical notes from whole notes to sixteenth notes
- **MIDI File Generation**: Generates a MIDI file based on what is read from the sheet music
- **Audio File Generation**: Renders an audio file from the generated MIDI file
- **Staff Detection**: Automatically detects staff lines and maps note positions
- **Flexible Tempo**: Adjustable playback tempo (beats per minute)
- **Multiple Note Types**: Supports various note durations and positions

## Requirements

- Python 3.13 (Likely works on other versions but untested.)
- OpenCV
- NumPy
- A SoundFont file (.sf2) for audio synthesis

## Installation

1. **Clone or download this project**
```bash
git clone https://github.com/brandon-mason/CS4337-project.git
```

2. **Create a virtual environment**:
```bash
python3 -m venv .venv
```

3. **Activate the environment**:
```bash
source .venv/bin/activate
# or use the helper script:
source activate.sh
```

4. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

5. **Download a SoundFont file** (optional):
   - Download a free SoundFont
   - Place it in the soundfonts folder in the project directory 

## Usage

### Basic Usage (Make sure the virtual environment is running)

1. **Run the Gradio interface**:
```bash
python gradio_interface.py
```

OR

1. **Run the demo** (plays a C major scale):
```bash
python main.py
```

2. **Play sheet music from an image**:
```bash
python main.py <your_sheet_music>.png
```
Replace your_sheet_music.png with the name of a file in preview_directory

### Advanced Usage

**Specify tempo**:
```bash
python main.py sheet_music.png --tempo 140
```

**Use a custom SoundFont**:
```bash
python main.py sheet_music.png --soundfont soundfont_file_name.sf2
```

**Save Generated Images**:
```bash
python main.py sheet_music.png --preview
```

### Command Line Options

- `image_path`: Path to the sheet music image file
- `--tempo`: Tempo in beats per minute (default: 120)
- `--soundfont`: Path to SoundFont file (.sf2)
- `--preview`: Save preprocessed images to the preview_directory folder

## How It Works

### 1. Image Preprocessing

### 2. Staff Line Detection

### 3. Note Detection

### 4. Note Mapping

### 5. Audio Playback
- Uses MidiUtil to create a midi file
- Uses sf2_loader to generate a wav file from the midi file
- Supports adjustable tempo

## Note Types

| Supported | Note Type | Duration | Visual Characteristics |
|-----------|-----------|----------|----------------------|
| N | Whole Note | 4 beats | Hollow circle, no stem |
| N | Half Note | 2 beats | Hollow circle with stem |
| Y | Quarter Note | 1 beat | Solid circle with stem |
| N | Eighth Note | 0.5 beats | Solid circle with stem and flag |
| N | Sixteenth Note | 0.25 beats | Solid circle with stem and double flag |

## Supported Notes

The system currently supports notes in the treble clef range:
- C4, D4, E4, F4, G4, A4, B4, C5

## File Structure

```
project/
├── preview_directory/      # Directory where saved preprocessed images are stored
├── soundfonts/             # Soundfonts storage
├── test_cases/             # Sheet music storage
├── main.py                 # Command line interface
├── sheet_music_player.py   # Sheet music processing
├── requirements.txt        # Python dependencies
└── README.md               # This file
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
   - Ensure notes are positioned on or between staff lines
   - Try the provided test images first to verify the system works

4. **Audio not playing**:
   - Check that a SoundFont is loaded
   - Ensure your system's audio is working

### Performance Tips

- Use high-resolution, clean images for best results
- Ensure good contrast between notes and background
- Computer-generated sheet music works better than handwritten
- Avoid complex backgrounds or watermarks

## Limitations

- Currently optimized for treble clef and key of C major only
- Only detects quarter notes
- Works best with computer-generated sheet music
- Limited to single-line melodies (no chords)
- Requires clear, well-formatted sheet music
- Note detection accuracy depends on image quality

## Future Enhancements

- Recognition of more note subdivisions
- Chord recognition and playback

## TODO

- Refine note sizes that are detected

## License

This project is open source and available under the MIT License.

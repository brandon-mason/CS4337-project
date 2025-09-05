#!/usr/bin/env python3
"""
Main script for the Sheet Music Player project.
This script demonstrates how to use the SheetMusicPlayer class to read and play sheet music.
"""

import argparse
import sys
import os
from sheet_music_player import SheetMusicPlayer

def main():
    """Main function to run the sheet music player."""
    parser = argparse.ArgumentParser(
        description="Computer Vision Sheet Music Player",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py sheet_music.png
  python main.py sheet_music.png --tempo 140
  python main.py sheet_music.png --soundfont /path/to/soundfont.sf2
        """
    )
    
    parser.add_argument(
        "image_path",
        default='c-major.png',
        help="Path to the sheet music image file"
    )
    
    parser.add_argument(
        "--tempo",
        type=float,
        default=120.0,
        help="Tempo in beats per minute (default: 120)"
    )
    
    parser.add_argument(
        "--soundfont",
        type=str,
        default='Pokemon_Black_and_White.sf2',
        help="Path to SoundFont file (.sf2)"
    )
    
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Save preview images showing processing steps and detected notes"
    )
    
    args = parser.parse_args()
    
    # Check if image file exists
    image_path = f"test_cases/{args.image_path}"
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        sys.exit(1)
    
    soundfont_path = f"soundfonts/{args.soundfont}"
    
    # Create and configure the player
    player = SheetMusicPlayer(soundfont_path)
    
    try:
        # Play the sheet music
        print(f"Playing sheet music: {args.image_path}")
        print(f"Tempo: {args.tempo} BPM")
        print("Press Ctrl+C to stop playback")
        print("-" * 50)

        player.play_sheet_music_path(args.image_path, args.tempo, save_preview=args.preview)
        
    except KeyboardInterrupt:
        print("\nPlayback interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    # finally:
        # player.cleanup()

def demo_mode():
    """Run in demo mode with a simple test pattern."""
    print("Running in demo mode...")
    print("This will play a simple C major scale")
    
    player = SheetMusicPlayer()
    
    try:
        # Play a simple C major scale
        scale_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C4 to C5
        note_names = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
        
        print("Playing C major scale...")
        for i, (note, name) in enumerate(zip(scale_notes, note_names)):
            print(f"Playing {name}")
            player.play_note(note, 0.5)  # Half second per note
        
        print("Demo complete!")
        
    except Exception as e:
        print(f"Error in demo mode: {e}")
    finally:
        player.cleanup()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, run demo mode
        demo_mode()
    else:
        main()

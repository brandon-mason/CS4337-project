import string
import cv2
import numpy as np
import fluidsynth
import os
import time
from typing import List, Tuple, Dict, Optional
import logging

class SheetMusicPlayer:
    """
    A computer vision-based sheet music player that reads musical notation
    and plays it using FluidSynth.
    
    Supports whole notes, half notes, quarter notes, eighth notes, and sixteenth notes.
    """
    
    def __init__(self, soundfont: str = None):
        """
        Initialize the sheet music player.
        
        Args:
            soundfont_path: Path to a SoundFont file (.sf2). If None, will try to use default.
        """
        self.fs = None
        self.soundfont_path = soundfont
        self.note_durations = {
            'whole': 4.0,
            'half': 2.0,
            'quarter': 1.0,
            'eighth': 0.5,
            'sixteenth': 0.25
        }
        
        # MIDI note mapping for treble clef (C4 to C6)
        self.note_mapping = {
            'C4': 60, 'D4': 62, 'E4': 64, 'F4': 65, 'G4': 67, 'A4': 69, 'B4': 71,
            'C5': 72, 'D5': 74, 'E5': 76, 'F5': 77, 'G5': 79, 'A5': 81, 'B5': 83,
            'C6': 84
        }
        
        self.setup_logging()
        self.initialize_fluidsynth()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_fluidsynth(self):
        """Initialize FluidSynth with a SoundFont."""
        try:
            self.fs = fluidsynth.Synth()
            self.fs.start()
            
            # Try to load SoundFont
            if self.soundfont_path and os.path.exists(self.soundfont_path):
                sfid = self.fs.sfload(self.soundfont_path)
                self.fs.program_select(0, sfid, 0, 8)
                self.logger.info(f"Loaded SoundFont: {self.soundfont_path}")
            else:
                # Try to find a default SoundFont
                default_paths = [
                    "Pokemon_Black_and_White.sf2"
                ]
                
                for path in default_paths:
                    soundfont_path = f"soundfonts/{path}"
                    if os.path.exists(soundfont_path):
                        sfid = self.fs.sfload(soundfont_path)
                        self.fs.program_select(0, sfid, 0, 0)
                        self.logger.info(f"Loaded default SoundFont: {soundfont_path}")
                        break
                else:
                    self.logger.warning("No SoundFont found. Audio playback may not work.")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize FluidSynth: {e}")
            self.fs = None

    def preview_image(self, image: np.ndarray, name: string="image.png"):
        cv2.imshow(name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # def preprocess_image(self, image_path: str, save_preview: bool = False) -> np.ndarray:
    #     """
    #     Preprocess the sheet music image for better note detection.
        
    #     Args:
    #         image_path: Path to the sheet music image
    #         save_preview: Whether to save preview images of processing steps
            
    #     Returns:
    #         Preprocessed image as numpy array
    #     """
    #     # Read image
    #     image = cv2.imread(image_path)
    #     if image is None:
    #         raise ValueError(f"Could not read image: {image_path}")
        
    #     # Convert to grayscale
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #     # Invert the image
    #     inverted = cv2.bitwise_not(gray)
        
    #     # Apply Gaussian blur to reduce noise
    #     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
    #     # Apply adaptive thresholding
    #     thresh = cv2.adaptiveThreshold(
    #         blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    #     )
        
    #     # Morphological operations to clean up the image
    #     kernel = np.ones((3, 3), np.uint8)
    #     cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    #     cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        
    #     # Save preview images if requested
    #     if save_preview:
    #         base_name = os.path.splitext(os.path.basename(image_path))[0]
    #         try:
    #             os.makedirs('preview_directory', exist_ok=True)
    #             print(f"Directory 'preview_directory' created or already exists.")
    #         except OSError as e:
    #             print(f"Error creating directory 'preview_directory': {e}")

    #         os.chdir('preview_directory')

    #         # Save original
    #         cv2.imwrite(f"{base_name}_original.png", image)

    #         # Save inverted
    #         cv2.imwrite(f"{base_name}_inverted.png", inverted)
            
    #         # Save grayscale
    #         cv2.imwrite(f"{base_name}_grayscale.png", gray)
            
    #         # Save blurred
    #         cv2.imwrite(f"{base_name}_blurred.png", blurred)
            
    #         # Save thresholded
    #         cv2.imwrite(f"{base_name}_threshold.png", thresh)
            
    #         # Save final cleaned
    #         cv2.imwrite(f"{base_name}_cleaned.png", cleaned)
            
    #         self.logger.info(f"Preview images saved: {base_name}_*.png")
        
    #     return cleaned
    
    def detect_staff_lines(self, image: np.ndarray) -> List[Dict]:
        """
        Detect horizontal staff lines in the sheet music by color.
        
        Args:
            image: Original sheet music image
            
        Returns:
            List of staff line dictionaries with coordinates
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define range for black/dark lines (staff lines are usually black)
        # You can adjust these values based on your image
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 50])
        
        # Create mask for dark lines
        mask = cv2.inRange(hsv, lower_black, upper_black)
        self.preview_image(mask, "mask")
        
        # Find horizontal lines using morphological operations
        # Create horizontal kernel
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (105, 1))
        
        # Detect horizontal lines
        horizontal_lines = cv2.morphologyEx(mask, cv2.MORPH_OPEN, horizontal_kernel)
        self.preview_image(horizontal_lines, "hl")
        
        # Find contours of horizontal lines
        contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        staff_lines = []
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by aspect ratio (horizontal lines should be wide and thin)
            if w > 100 and h < 10:  # Wide and thin
                center_y = y + h // 2
                staff_lines.append({
                    "y": center_y,
                    "x1": x,
                    "x2": x + w,
                    "width": w,
                    "height": h
                })
        
        # Group nearby lines and sort by y-coordinate
        staff_lines = sorted(staff_lines, key=lambda x: x["y"])
        grouped_lines = []
        
        for line in staff_lines:
            if not grouped_lines or abs(line["y"] - grouped_lines[-1]["y"]) > 5:
                grouped_lines.append(line)
        
        return grouped_lines[:5]  # Return top 5 lines (typical staff)

    def resize_by_staff_height(self, original_image: np.ndarray, staff_lines: List[Dict]):
        """
        Check the size of the staff and resize the image accordingly.
        
        Args:
            original_image: Original sheet music image
            staff_lines: The array of staff line dictionaries calculated by detect_staff_lines
            
        Returns:
            Resized image and recalculated staff line dictionaries
            OR
            Original image and staff line dictionaries
        """
        bottom_line = staff_lines[0]["y"]
        top_line = staff_lines[len(staff_lines) - 1]["y"]

        for line in staff_lines:
            if line["y"] < bottom_line:
                bottom_line = line["y"]
            elif line["y"] > top_line:
                top_line = line["y"]

        staff_height = top_line - bottom_line

        # Resize the image to keep the size of the staff consistent across all images(staff height should be around 100 pixels tall)
        if not (staff_height > 90 and staff_height < 100):
            scalar = 100 / staff_height
            resized_image = cv2.resize(original_image, None, fx=scalar, fy=scalar, interpolation=cv2.INTER_LINEAR)
            # self.preview_image(resized_image)

            # Recalculate the staff dimensions based on the new image size
            new_staff_lines = []
            for line in staff_lines:
                new_line = line
                for key in line:
                    new_line[key] = int(line[key] * scalar)
                
                new_staff_lines.append(new_line)

            return resized_image, new_staff_lines

        return original_image, staff_lines
    
    def detect_notes_by_intersection(self, image_name: str, image: np.ndarray, staff_lines: List[Dict], save_preview: bool = False) -> List[Dict]:
        """
        Detect musical notes by checking intersections with staff lines.
        
        Args:
            image: Sheet music image
            staff_lines: List of staff line dictionaries
            save_preview: Whether to save the visualization detection image
            
        Returns:
            List of detected notes with their properties
        """
        notes = []

        # Convert to grayscale for better note detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Use the binary image directly - we'll filter contours instead
        note_heads = binary.copy()
        
        # Also create a version that detects hollow circles (whole notes)
        # Use morphological operations to find circular shapes
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        hollow_circles = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Find contours of potential notes (both filled and hollow)
        contours_filled, _ = cv2.findContours(note_heads, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_hollow, _ = cv2.findContours(hollow_circles, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Combine both sets of contours
        contours = contours_filled + contours_hollow
        
        # Create visualization image
        vis_image = image.copy()
        
        # Draw all contours for debugging
        cv2.drawContours(vis_image, contours, -1, (0,255,0), 1)
        
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            # Filter by size to find note heads - look for more circular note heads
            aspect_ratio = w / h if h > 0 else 0

            # Look for note heads: circular/square objects that are not too thin
            # Filter out tenuto marks (very thin horizontal lines) and staff lines (very wide)
            # Also look for smaller objects that might be note heads
            is_note_head = ((15 < w < 125 and 10 < h < 125 and 0.4 < aspect_ratio < 2.5 and w * h > 20) or
                           (15 < w < 125 and 10 < h < 125 and 0.5 < aspect_ratio < 2.0 and w * h > 50))
            
            if is_note_head:
                # Check if this contour intersects with any staff line
                note_center_y = y + h // 2
                note_center_x = x + w // 2
                
                # Check intersection with staff lines
                intersecting_line = None
                min_distance = float('inf')
                
                for staff_line in staff_lines:
                    line_y = staff_line["y"]
                    line_x1 = staff_line["x1"]
                    line_x2 = staff_line["x2"]
                    
                    # Check if note is within the horizontal range of the staff line
                    if line_x1 <= note_center_x <= line_x2:
                        # Calculate vertical distance to this staff line
                        distance = abs(note_center_y - line_y)
                        
                        # Find the closest staff line within reasonable distance
                        if distance < min_distance and distance < 300:  # Much more tolerant
                            min_distance = distance
                            intersecting_line = staff_line
                
                if intersecting_line:
                    # This is likely a note on a staff line
                    # Determine note type based on fill (solid vs hollow)
                    roi = note_heads[y:y+h, x:x+w]
                    filled_ratio = np.sum(roi == 255) / (w * h)
                    
                    # Determine note duration based on fill ratio
                    if filled_ratio > 0.6:
                        duration = 'quarter'  # Solid note head
                    elif filled_ratio > 0.2:
                        duration = 'half'     # Partially filled
                    else:
                        duration = 'whole'    # Hollow note head
                    
                    # Map y-position to note name
                    note_name = self.map_position_to_note(note_center_y, [line["y"] for line in staff_lines])
                    
                    if note_name:
                        notes.append({
                            'x': x,
                            'y': y,
                            'note': note_name,
                            'duration': duration,
                            'midi_note': self.note_mapping.get(note_name, 60),
                            'staff_line': intersecting_line
                        })
                        
                        # Draw detection on visualization
                        cv2.rectangle(vis_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(vis_image, f"{note_name} ({duration})", 
                                   (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        
                        # Draw center point
                        cv2.circle(vis_image, (note_center_x, note_center_y), 3, (255, 0, 0), -1)
        
        # Draw staff lines on visualization
        for staff_line in staff_lines:
            cv2.line(vis_image, (staff_line["x1"], staff_line["y"]), 
                    (staff_line["x2"], staff_line["y"]), (255, 0, 0), 2)

        if save_preview:
            try:
                os.makedirs('preview_directory', exist_ok=True)
                print(f"Directory 'preview_directory' created or already exists.")
            except OSError as e:
                print(f"Error creating directory 'preview_directory': {e}")

            os.chdir('preview_directory')

            # Save original
            cv2.imwrite(f"{image_name.split(".")[0]}_detection.png", vis_image)
            
            self.logger.info(f"Preview image saved: {image_name.split(".")[0]}_detection.png")

        self.preview_image(vis_image, f"{image_name.split(".")[0]}_detection_visualization")
        
        # Sort notes by x-position (left to right)
        notes.sort(key=lambda x: x['x'])
        
        return notes
    
    def map_position_to_note(self, y_pos: int, staff_lines: List[int]) -> Optional[str]:
        """
        Map a y-position to a musical note based on staff lines.
        
        Args:
            y_pos: Y-coordinate of the note
            staff_lines: List of staff line y-coordinates
            
        Returns:
            Note name (e.g., 'C4', 'D4') or None if not found
        """
        if len(staff_lines) < 5:
            return None
        
        # Calculate staff spacing
        staff_spacing = (staff_lines[-1] - staff_lines[0]) / 4
        
        # Calculate position relative to staff
        relative_pos = (y_pos - staff_lines[0]) / staff_spacing
        
        # Map to note names (simplified mapping)
        note_positions = {
            -2: 'C6', -1.5: 'B5', -1: 'A5', -0.5: 'G5', 0: 'F5',
            0.5: 'E5', 1: 'D5', 1.5: 'C5', 2: 'B4', 2.5: 'A4',
            3: 'G4', 3.5: 'F4', 4: 'E4', 4.5: 'D4', 5: 'C4'
        }

        # Find closest position
        closest_pos = min(note_positions.keys(), key=lambda x: abs(x - relative_pos))
        
        if abs(closest_pos - relative_pos) < 0.5:  # Tolerance
            return note_positions[closest_pos]
        
        return None
    
    def detect_note_duration(self, image: np.ndarray, note_region: Tuple[int, int, int, int]) -> str:
        """
        Detect the duration of a note based on its visual characteristics.
        
        Args:
            image: Preprocessed image
            note_region: (x, y, w, h) of the note region
            
        Returns:
            Note duration ('whole', 'half', 'quarter', 'eighth', 'sixteenth')
        """
        x, y, w, h = note_region
        roi = image[y:y+h, x:x+w]
        
        # Count filled pixels
        filled_pixels = np.sum(roi == 255)
        total_pixels = w * h
        fill_ratio = filled_pixels / total_pixels
        
        # Analyze note characteristics
        if fill_ratio < 0.2:
            return 'whole'  # Hollow note head
        elif fill_ratio < 0.5:
            return 'half'   # Partially filled
        elif fill_ratio < 0.8:
            return 'quarter'  # Solid note head
        else:
            # Check for flags/beams to determine eighth/sixteenth
            # This is a simplified approach
            return 'eighth'
    
    def play_note(self, midi_note: int, duration: float, velocity: int = 100):
        """
        Play a single note using FluidSynth.
        
        Args:
            midi_note: MIDI note number
            duration: Duration in seconds
            velocity: Note velocity (0-127)
        """
        if self.fs is None:
            self.logger.warning("FluidSynth not initialized. Cannot play note.")
            return
        
        try:
            self.fs.noteon(0, midi_note, velocity)
            time.sleep(duration)
            self.fs.noteoff(0, midi_note)
        except Exception as e:
            self.logger.error(f"Error playing note {midi_note}: {e}")
    
    def play_sheet_music(self, image_name: str, tempo: float = 120.0, save_preview: bool = False):
        """
        Read and play sheet music using color-based detection for staff lines and note intersections.
        
        Args:
            image_path: Path to the sheet music image
            tempo: Tempo in beats per minute
            save_preview: Whether to save preview images of processing steps
        """
        try:
            self.logger.info(f"Processing sheet music: {image_name}")
            
            # Read original image
            image_path = f"test_cases/{image_name}"
            original_image = cv2.imread(image_path)
            if original_image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Detect staff lines
            staff_lines = self.detect_staff_lines(original_image)
            if not staff_lines:
                self.logger.error("No staff lines detected")
                return

            # Resize image based on staff size
            resized_image, resized_staff_lines = self.resize_by_staff_height(original_image, staff_lines)
            
            self.logger.info(f"Detected {len(resized_staff_lines)} staff lines")

            if len(staff_lines) != 5:
                self.logger.error("Invalid sheet music format")
                return

            # Detect notes by intersection
            notes = self.detect_notes_by_intersection(image_name, resized_image, staff_lines, save_preview)

            if not notes:
                self.logger.error("No notes detected")
                return
            
            self.logger.info(f"Detected {len(notes)} notes")
            
            # Calculate beat duration
            beat_duration = 60.0 / tempo
            
            # Play notes
            self.logger.info("Starting playback...")
            for i, note in enumerate(notes):
                duration = self.note_durations[note['duration']] * beat_duration
                self.logger.info(f"Playing {note['note']} ({note['duration']}) for {duration:.2f}s")
                self.play_note(note['midi_note'], duration)
            
            self.logger.info("Playback complete")
            
        except Exception as e:
            self.logger.error(f"Error processing sheet music: {e}")
    
    def cleanup(self):
        """Clean up FluidSynth resources."""
        if self.fs:
            self.fs.delete()
            self.fs = None

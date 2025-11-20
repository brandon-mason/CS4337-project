import os
import time
from typing import List, Tuple, Dict, Optional
import logging

import cv2
import numpy as np

import sf2_loader as sf

from generate_audio import AudioGenerator

class SheetMusicPlayer:
    """
    A computer vision-based sheet music player that reads musical notation
    and plays it using sf2_loader.
    
    Currently supports quarter notes.
    """
    
    def __init__(self, soundfont: str='soundfonts/Pokemon_Black_and_White.sf2'):
        """
        Initialize the sheet music player.
        
        Args:
            soundfont_path: Path to a SoundFont file (.sf2). If None, will try to use default.
        """
        self.loader = None
        self.soundfont_path = soundfont
        self.note_durations = {
            'whole': 4.0,
            'half': 2.0,
            'quarter': 1.0,
            'eighth': 0.5,
            'sixteenth': 0.25,
            'rest_whole': 4.0,
            'rest_half': 2.0,
            'rest_quarter': 1.0,
            'rest_eighth': 0.5,
            'rest_sixteenth': 0.25
        }
        self.save_preview = False

        # Initialize soundfont loader
        self.loader = sf.sf2_loader(self.soundfont_path)
        
        # MIDI note mapping for treble clef (C4 to C6)
        self.note_mapping = {
            'C4': 60, 'D4': 62, 'E4': 64, 'F4': 65, 'G4': 67, 'A4': 69, 'B4': 71,
            'C5': 72, 'D5': 74, 'E5': 76, 'F5': 77, 'G5': 79, 'A5': 81, 'B5': 83,
            'C6': 84
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def preview_image(self, image: np.ndarray, name: str="image.png"):
        """
        Displays the provided image in a window.
        This should only be used for debugging in CLI mode.
        
        Args:
            image: The image to display
            name: The name of the window
            
        Returns:
            Preprocessed image as numpy array
        """
        cv2.imshow(name, image)
        cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return
    
    def preprocess_image(self, image: np.ndarray, save_preview: bool = False, image_name = "image") -> np.ndarray:
        """
        Preprocess the sheet music image for better note detection.
        
        Args:
            image_path: Path to the sheet music image
            save_preview: Whether to save preview images of processing steps
            
        Returns:
            Preprocessed image as numpy array
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Light contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)

        # Adaptive threshold with larger block size and smaller constant
        # Larger blockSize (e.g., 51-101) preserves more detail
        # Smaller C value (e.g., 5-8) makes threshold less aggressive
        thresh = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 
            blockSize=101,  # Increased from 35
            C=3            # Reduced from 11
        )

        return thresh
    
    def detect_staff_lines(self, image: np.ndarray, save_preview: bool=False, image_name: str = "image") -> List[Dict]:
        """
        Detect horizontal staff lines in the sheet music by color.
        
        Args:
            image: Original sheet music image
            
        Returns:
            List of staff line dictionaries with coordinates
        """
        processed_image = self.preprocess_image(image, save_preview, image_name)

        # Find horizontal lines using morphological operations
        # Create horizontal kernel
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (105, 1))
        
        # Detect horizontal lines
        horizontal_lines = cv2.morphologyEx(processed_image, cv2.MORPH_OPEN, horizontal_kernel)
        # self.preview_image(horizontal_lines, "hl")
        
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

    def detect_notes_by_intersection(self, image: np.ndarray, staff_lines: List[Dict], save_preview: bool = False, image_name: str = "image", original_image: np.ndarray = None) -> List[Dict]:
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

        # Create visualization image
        vis_image = original_image.copy()
        viss_image = image.copy()

        contours, _ = self.extract_note_contours_from_clean(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        cv2.drawContours(vis_image, contours, -1, (0,255,0), 1)
        
        for contour in contours:
            points = contour.reshape(-1, 2)
            x, y, w, h = cv2.boundingRect(contour)
            
            if w < 10 or h < 10:
                continue
            # Calculate the center for this contour (for both notes and rests)
            cx = x + w / 2
            cy = y + h / 2   

            roi = image[y:y+h, x:x+w]

            # Check if this contour is a rest
            rest_type = self.detect_rest(contour, image)
            if rest_type:
                notes.append({
                    'x': cx,
                    'y': cy,
                    'note': rest_type,
                    'duration': rest_type,
                    'midi_note': 0  # No MIDI for rests
                })
                continue
            
            # Find widest horizontal section
            horizontal_splits = 5
            max_width = 0
            notehead_y_center = y + h // 2
            
            for i in range(horizontal_splits):
                y_pos = y + (i * h) // horizontal_splits
                y_next = y + ((i + 1) * h) // horizontal_splits
                
                mask = (points[:, 1] >= y_pos) & (points[:, 1] < y_next)
                slice_pts = points[mask]
                
                if len(slice_pts) > 0:
                    width = slice_pts[:, 0].max() - slice_pts[:, 0].min()

                    if width > max_width:
                        max_width = width
                        notehead_y_center = (y_pos + y_next) // 2
            
            # Get points near the widest region (note head)
            y_tolerance = h // 4
            mask = np.abs(points[:, 1] - notehead_y_center) < y_tolerance
            head_points = points[mask]

            topmost = None
            bottommost = None
            leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
            rightmost = tuple(contour[contour[:, :, 0].argmax()][0])

            if len(head_points) > 0:
                topmost = tuple(head_points[head_points[:, 1].argmin()])
                bottommost = tuple(head_points[head_points[:, 1].argmax()])
            else:
                topmost = tuple(points[points[:, 1].argmin()])
                bottommost = tuple(points[points[:, 1].argmax()])

            top = topmost[1]
            bottom = bottommost[1]
            left = leftmost[0]
            right = rightmost[0]


            cy = top + (bottom - top) / 2
            cx = left + (right - left) / 2
            note_name = self.map_position_to_note(cy, [line["y"] for line in staff_lines])

            

            mask = np.zeros_like(image)
            cv2.drawContours(mask, [contour], -1, 255, -1)

            roi = image[top:bottom, left:right]
            filled_ratio = np.sum(roi == 0) / ((right - left) * (bottom - top))
            # For notes
            duration = None
            #1. Flag-based duration for 8th/16th (returns None for no flags)
            duration_flag, flag_count = self.detect_note_flags(contour, image)
            if (bottom - top) <= 0 or (right - left) <= 0:
                continue  # skip malformed contours
            if duration_flag and filled_ratio > 0.37:
                duration = duration_flag
            else:
            # Determine note duration based on fill ratio
                if filled_ratio > 0.45:
                    duration = 'quarter'  # Solid note head
                elif filled_ratio > 0.25:
                    duration = 'half'     # Partially filled
                else:
                    duration = 'whole'    # Hollow note head
            print(f"x={cx}, y={cy}, filled_ratio={filled_ratio:.2f}, flag_cnts={flag_count}, assigned:{duration}")
            

            note_name = self.map_position_to_note(cy, [line["y"] for line in staff_lines])
            
            if note_name:
                notes.append({
                    'x': cx,
                    'y': cy,
                    'note': note_name,
                    'duration': duration,
                    'midi_note': self.note_mapping.get(note_name, 60),
                })
                
                # Draw detection on visualization
                cv2.rectangle(vis_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(vis_image, f"{note_name} ({duration})", 
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(vis_image, f"Filled Ratio({filled_ratio:.1f})", 
                            (x, y + h + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                cv2.circle(vis_image, (int(cx), int(cy)), 3, (0, 0, 255), -1)

        self.preview_image(vis_image, f"{image_name.split(".")[0]}_detection_visualization")
        # self.preview_image(viss_image, f"{image_name.split(".")[0]}_outer")
        

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
        elif fill_ratio < 0.4:
            return 'half'   # Partially filled
        elif fill_ratio < 0.6:
            return 'quarter'  # Solid note head
        else:
            # Check for flags/beams to determine eighth/sixteenth
            # This is a simplified approach
            return 'eighth'

    
    def detect_note_flags(self, contour, image) -> Tuple[Optional[str], int]:
        """
        Detect note duration based on presence of flags (eighth, sixteenth).
        Returns: 'quarter', 'eighth', or 'sixteenth'
        """
        x, y, w, h = cv2.boundingRect(contour)
        roi = image[y:y+h, x:x+w]
        
        # Only look for stems
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(2, h//3)))
        stem_img = cv2.morphologyEx(roi, cv2.MORPH_OPEN, vertical_kernel)
        stem_cnts, _ = cv2.findContours(stem_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # If not stem found
        if len(stem_cnts) == 0:
            return None, 0

        # Estimate stem orientation
        stem_pixels = np.column_stack(np.where(stem_img > 0))
        stem_y_mean = np.mean(stem_pixels[:, 0]) if stem_pixels.size > 0 else h //2
        head_center_y = h // 2

        #If stem tip is above notehead, look for lfag at top else at bottom
        if stem_y_mean < head_center_y:
            flag_region = roi[:int(h * 0.20),:]
        else:
            flag_region = roi[int(h * 0.80):,:]
        
         # Now: check for flags to the right/below stem base
        flag_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(2, w//18), 3))

        flag_img = cv2.morphologyEx(flag_region, cv2.MORPH_OPEN, flag_kernel)
        flag_cnts, _ = cv2.findContours(flag_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #Filter by area
        min_flag_area = 12 #may need to adjust
        min_flag_width = max(4, w // 10)
        flag_region_height = flag_region.shape[0]
        max_flag_width_fraction = 0.6
        
        flag_cnts_filtered = []    
        for cnt  in flag_cnts:
            x2,y2,w2,h2 = cv2.boundingRect(cnt)
            if (
                cv2.contourArea(cnt) > min_flag_area and w2 > min_flag_width and w2 < max_flag_width_fraction * w
            ):
                if abs(y2) < 4 or abs((y2 + h2) - flag_region_height) < 4:
                    flag_cnts_filtered.append(cnt)
        
        print(f"x={x}, y={y}, w={w}, h={h}, flag_cnts={len(flag_cnts_filtered)}")
        flag_cnts = flag_cnts_filtered
        
        flag_count = len(flag_cnts)
        if len(flag_cnts) == 1:
            return 'eighth', flag_count
        elif len(flag_cnts) >= 2:
            return 'sixteenth', flag_count
        return None, flag_count
        
    
    def detect_rest(self, contour, image) -> Optional[str]:
        x, y, w, h = cv2.boundingRect(contour)
        roi = image[y:y+h, x:x+w]
        # Guarantee ROI is grayscale
        if len(roi.shape) == 3:
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi = roi.astype(np.uint8)
        quarter_template = cv2.imread('rest_templates/quarter_rest.png', 0)
        half_template = cv2.imread('rest_templates/half_rest.png', 0)
        whole_template = cv2.imread('rest_templates/whole_rest.png', 0)
        eigth_template = cv2.imread('rest_templates/eighth_rest.png', 0)
        sixteenth_template = cv2.imread('rest_templates/sixteenth_rest.png', 0)
        if quarter_template is None:
            return None
        # If ROI is too small or too large, skip to avoid false matches
        if roi.shape[0] < 10 or roi.shape[1] < 10:
            return None
     
        # Resize roi to match template size (or template to roi size)
        # For robustness, handle both cases
        try:
            resized_template = cv2.resize(quarter_template, (roi.shape[1], roi.shape[0]))
            cv2.imwrite("rest_roi_debug.png", roi)
            cv2.imwrite("rest_template_debug.png", resized_template)
        except Exception as e:
            print(f"Template resize error: {e}")
            return None
        rest = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(rest)
        if max_val > 0.3:  # You may tune this threshold
            return "rest_quarter"
        print(f"Rest ROI shape: {roi.shape}, max_val: {max_val}")
        return None
    
    def play_note(self, note_name: str, duration: float, velocity: int = 100, tempo: float = 120.0):
        """
        Play a single note using sf2_loader.
        
        Args:
            note_name: MIDI note number
            duration: Duration in seconds
            velocity: Note velocity (0-127)
        """
        if self.loader is None:
            self.logger.warning("sf2_loader not initialized. Cannot play note.")
            return
        
        try:
            self.loader.play_note(note_name=note_name, duration=duration, volume=velocity, bpm=tempo)
            time.sleep(duration)
        except Exception as e:
            self.logger.exception(f"Error playing note {note_name}: {e}")
            
    def play_sheet_music_image(self, original_image: np.ndarray, tempo: float = 120.0, save_preview: bool = False, image_name: str = "image"):
        """
        Read and play sheet music using color-based detection for staff lines and note intersections.
        
        Args:
            image_path: Path to the sheet music image
            tempo: Tempo in beats per minute
            save_preview: Whether to save preview images of processing steps
        """
        try:
            self.save_preview = save_preview
            self.logger.info(f"Processing sheet music: ")
            
            # Initialize AudioGenerator
            generator = AudioGenerator(self.soundfont_path, self.note_mapping, self.note_durations)
            
            # Detect staff lines
            staff_lines = self.detect_staff_lines(original_image, self.save_preview)

            if not staff_lines:
                self.logger.exception("No staff lines detected")
                return

            # Resize image based on staff size
            resized_image, resized_staff_lines = self.resize_by_staff_height(original_image, staff_lines)
            cleaned_image = self.remove_staff_lines(resized_image)
            
            self.logger.info(f"Detected {len(resized_staff_lines)} staff lines")

            if len(staff_lines) != 5:
                self.logger.exception("Invalid sheet music format")
                return

            # Detect notes by intersection
            notes = self.detect_notes_by_intersection(cleaned_image, staff_lines, save_preview, image_name)

            if not notes:
                self.logger.exception("No notes detected")
                return
            
            self.logger.info(f"Detected {len(notes)} notes")

            notes = [n for n in notes if 'duration' in n]
            for n in notes:
                if 'duration' not in n:
                    print(f"WARNING: Skipping note missing duration: {n}")

            # Generate MIDI file from note data
            out_dir = "output"
            self.logger.info('Generating MIDI...')
            generator.generate_midi(notes=notes, tempo=tempo, out_dir=out_dir)
            self.logger.info('MIDI Generated!')

            # Generate audio file from MIDI file
            midi_file = "midi.mid"
            self.logger.info('Generating Audio File...')
            generator.generate_audio(midi_file=midi_file, out_dir=out_dir)
            self.logger.info('Audio File Generated!')

            self.logger.info('All done!')
            
        except Exception as e:
            self.logger.exception(f"Error processing sheet music: {e}")

    def play_sheet_music_path(self, image_name: str, tempo: float=120.0, save_preview: bool=False):
        """
        Read and play sheet music using color-based detection for staff lines and note intersections.
        
        Args:
            image_path: Path to the sheet music image
            tempo: Tempo in beats per minute
            save_preview: Whether to save preview images of processing steps
        """
        try:
            # Initialize AudioGenerator
            generator = AudioGenerator(self.soundfont_path, self.note_mapping, self.note_durations)

            self.logger.info(f"Processing sheet music: {image_name}")
            # Read original image
            image_path = f"test_cases/{image_name}"
            original_image = cv2.imread(image_path)
            if original_image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Detect staff lines
            staff_lines = self.detect_staff_lines(original_image)
            if not staff_lines:
                self.logger.exception("No staff lines detected")
                return

            # Resize image based on staff size
            resized_image, resized_staff_lines = self.resize_by_staff_height(original_image, staff_lines)
            
            self.logger.info(f"Detected {len(resized_staff_lines)} staff lines")

            if len(staff_lines) != 5:
                self.logger.exception("Invalid sheet music format")
                return

            # Detect notes by intersection
            
            cleaned_image = self.remove_staff_lines(resized_image)
            refilled_image = self.refill_notes(cleaned_image)
            self.preview_image(refilled_image, "Without staff lines")
            notes = self.detect_notes_by_intersection(refilled_image, staff_lines, save_preview, image_name, original_image=resized_image)

            if not notes:
                self.logger.exception("No notes detected")
                return

            self.logger.info(f"Detected {len(notes)} notes, {tempo}")

            # Calculate beat duration
            beat_duration = 60.0 / tempo
            for note in notes:
                if "duration" not in note:
                    print(f"ERROR: Note missing duration: {note}")

            # Generate MIDI file from note data
            out_dir = "output"
            self.logger.info('Generating MIDI...')
            generator.generate_midi(notes = notes, tempo = tempo, out_dir = out_dir)
            self.logger.info('MIDI Generated!')

            # Generate audio file from MIDI file
            midi_file = "midi.mid"
            self.logger.info('Generating Audio File...')
            generator.generate_audio(midi_file=midi_file, out_dir=out_dir)
            self.logger.info('Audio File Generated!')

            # Play notes
            self.logger.info("Starting playback...")
            for i, note in enumerate(notes):
                key = note['duration'] if note['duration'] in self.note_durations else 'quarter'
                duration = self.note_durations[key] * beat_duration
                if 'rest' in note['note']:
                    self.logger.info(f"Rest for {duration:.2f}s")
                    time.sleep(duration)  # silence
                else:
                    self.logger.info(f"Playing {note['note']} ({note['duration']}) for {duration:.2f}s")
                    self.play_note(note_name=note['note'], duration=duration, tempo=tempo)
            self.logger.info("Playback complete")
            
        except Exception as e:
            self.logger.exception(f"Error processing sheet music: {e}")

    def remove_staff_lines(self, image: np.ndarray) -> np.ndarray:
        """
        Remove staff lines from a sheet music image.
        
        Args:
            image: Original sheet music image (BGR or grayscale)
        
        Returns:
            Image with staff lines removed
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Threshold to get binary image (invert to make staff lines white)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Define horizontal kernel (same as in detect_staff_lines)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 1))
        
        # Detect horizontal lines
        detected_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        
        # Subtract the staff lines from the binary image
        no_staff = cv2.subtract(binary, detected_lines)
        
        # Invert back to normal (black lines on white)
        cleaned = cv2.bitwise_not(no_staff)
        if len(cleaned.shape) == 2:
            cleaned = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
        
        return cleaned
    
    def refill_notes(self, image):
        """
        Restore note heads that were partially removed with staff line removal.
        Uses morphological operations to close gaps and refill circles.
        
        Args:
            image: Cleaned BGR or grayscale image (after staff line removal)
        
        Returns:
            Image with note heads refilled
        """
        # Convert to grayscale if necessary
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Convert to binary (invert so black = background, white = foreground)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

        # Close small gaps in note heads 
        # Try a circular/elliptical kernel that roughly matches note size
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Optionally, dilate slightly to thicken notes ---
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dilated = cv2.dilate(closed, kernel_dilate, iterations=1)

        # Invert back to normal (black notes on white) ---
        refilled = cv2.bitwise_not(dilated)
        if len(refilled.shape) == 2:
            refilled = cv2.cvtColor(refilled, cv2.COLOR_GRAY2BGR)
        return refilled

    def extract_note_contours_from_clean(self, image):
        """
        Extracts note (symbol) contours from a staff-line-removed, binarized sheet music image.
        Args:
            img_nostaff (np.ndarray): Binarized image from which staff lines have been removed.
        Returns:
            contours (list): List of note contours found in the image.
            binary_contour_img (np.ndarray): Image with detected contours drawn.
        """
        # Ensure the image is binary (if not already)
        img_nostaff = None
        if len(image.shape) == 3:
            # Convert to grayscale
            img_nostaff = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            img_nostaff = image
            
        _, binary = cv2.threshold(img_nostaff, 128, 255, cv2.THRESH_BINARY_INV)

        # Find external contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Optional: create an image for visualizing contours
        contour_img = np.zeros_like(binary)
        cv2.drawContours(contour_img, contours, -1, 255, thickness=2)
        return contours, contour_img
import gradio as gr
from sheet_music_player import SheetMusicPlayer

# class GradioInterface:
#     def __init__(self, fn, inputs, outputs, title=None, description=None):
#         self.interface = gr.Interface(fn=fn, inputs=inputs, outputs=outputs, title=title, description=description)

#     def launch(self, **kwargs):
#         self.interface.launch(**kwargs)

#     def build_interface(self):
#         return self.interface.build()

player = SheetMusicPlayer()

# def wrapper(image, tempo=120.0, image_name="image", save_preview=''):
#     save_prev = len(save_preview) > 0 and save_preview[0] == "Save"
#     player.play_sheet_music_image(image, tempo, save_prev, image_name)

#     image_preview = f'preview_directory/{image_name}/{image_name}_detection.png' if save_prev else ''
    
#     if save_prev:
#         gr.Image(value=image_preview, type="filepath")
#     else:
#         gr.Image(visible=False)

#     return "output/output.wav", 

# sheet_music_interface = gr.Interface(
#     fn=wrapper,
#     inputs=[
#         "image", 
#         gr.Slider(minimum=60, maximum=200, value=120.0, randomize=False, label="Tempo"),
#         gr.Textbox(
#             label="Image Name",
#             value="image",
#         ),
#         gr.CheckboxGroup(["Save"], label = "Save Previews:"),
#     ],
#     outputs=[gr.Audio(label="Generated Audio", streaming=True, type='filepath')],
# )

# sheet_music_interface.launch()



import base64


def wrapper2(image, tempo, image_name, save_preview):
    save_prev = len(save_preview) > 0 and save_preview[0] == "Save"
    player.play_sheet_music_image(image, tempo, save_prev, image_name)

    audio_path = f"output/output.wav"
    image_path = f"preview_directory/{image_name}_preview.png" if save_prev else None
    return audio_path, image_path


# === Vintage CSS Theme ===
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond&family=Great+Vibes&display=swap');

/* === Global Background === */
body {
  background-color: #f4e9d8;
  background-image: url('https://www.transparenttextures.com/patterns/old-wall.png');
  background-repeat: repeat;
  color: #2f1b0c;
  font-family: 'EB Garamond', serif;
  overflow-x: hidden;
}

/* === Container === */
.gradio-container {
  max-width: 1000px !important;
  width: 90% !important;
  margin: 40px auto !important;
  padding: 40px;
  background: #f8f1e4;
  border: 4px double #c2a477;
  border-radius: 10px;
  box-shadow: 0 0 8px rgba(0,0,0,0.1);
}

/* === Title Section === */
h1 {
  text-align: center;
  font-family: 'Great Vibes', cursive;
  font-size: 3rem;
  color: #2f1b0c;
  text-shadow: 1px 1px #c2a477;
  margin-bottom: 0;
}
p {
  text-align: center;
  font-style: italic;
  color: #3c2a1a;
  margin-top: 5px;
  margin-bottom: 25px;
}

/* === Images === */
img[alt="music logo"] {
  display: block;
  margin: 25px auto;
  border-radius: 12px;
  width: 300px;
  height: auto;
  border: 3px solid #c2a477;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
}

/* === Panels === */
.gr-box {
  background: #f8f1e4 !important;
  border: 2px solid #c2a477 !important;
  border-radius: 8px !important;
  box-shadow: inset 0 0 5px rgba(0,0,0,0.05);
}

/* === Buttons === */
button {
  background: #d6b889 !important;
  border: 2px solid #a67544 !important;
  color: #2f1b0c !important;
  font-family: 'EB Garamond', serif !important;
  font-size: 1.1rem !important;
  padding: 10px 24px !important;
  border-radius: 6px !important;
  transition: all 0.2s ease-in-out !important;
}
button:hover {
  background: #e9d3a7 !important;
  transform: translateY(-1px);
}

/* === Slider === */
input[type="range"]::-webkit-slider-thumb {
  background: #a67544 !important;
}
input[type="range"]::-webkit-slider-runnable-track {
  background: #d6b889 !important;
}

/* === Decorative Dividers === */
hr.staff {
  border: none;
  border-top: 2px solid #c2a477;
  width: 90%;
  margin: 1.5rem auto;
  position: relative;
}
hr.staff::before, hr.staff::after {
  content: "♪";
  font-family: 'Great Vibes', cursive;
  color: #a67544;
  position: absolute;
  top: -0.7rem;
}
hr.staff::before { left: 5px; }
hr.staff::after { right: 5px; }

/* === Responsive === */
@media (max-width: 900px) {
  .gradio-container {
    padding: 20px;
  }
  img[alt="music logo"] {
    width: 200px;
  }
}
img[alt="music footer"] {
  background-color: #f8f1e4;
  padding: 8px 0;
  width: 100%;
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
  border-top: 2px solid #c2a477;
  border-bottom: 4px double #c2a477;
  border-radius: 0 0 10px 10px;
}

"""

with gr.Blocks(css=custom_css) as demo:
    # Header image
    with open("images/pic1.png", "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")
    gr.HTML(f"""
    <div style='text-align:center; margin-bottom:10px;'>
      <h1>Sheet Music Audio Converter</h1>
      <p>Bring your notes to life, the old-fashioned way.</p>
      <img src='data:image/png;base64,{encoded_image}' alt='music logo'>
    </div>
    <hr class="staff">
    """)

    # Inputs and outputs
    image = gr.Image(label="Upload Sheet Music")
    tempo = gr.Slider(minimum=60, maximum=200, value=120.0, label="Tempo")
    name = gr.Textbox(label="Image Name", value="image")
    save = gr.CheckboxGroup(["Save"], label="Save Previews:")
    output_audio = gr.Audio(label="Generated Audio", streaming=True, type='filepath')
    output_image = gr.Image(label="Detected Notes Preview")

    submit_btn = gr.Button("Generate Audio")

    submit_btn.click(
        fn=wrapper2, 
        inputs=[image, tempo, name, save], 
        outputs=[output_audio, output_image]
    )

    with open("images/pic4.png", "rb") as f:
        encoded_image2 = base64.b64encode(f.read()).decode("utf-8")
    gr.HTML(f"""
    <hr class="staff">
    <img src='data:image/png;base64,{encoded_image2}' 
         alt='music footer' 
         style='width: 100%; max-width: 100%; height: auto; display: block; 
                margin: 0 auto; border: 3px double #c2a477; 
                border-radius: 0 0 10px 10px; box-shadow: 0 -2px 5px rgba(0,0,0,0.1);'>
    """)


demo.launch()

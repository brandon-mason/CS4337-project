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


def wrapper2(image, tempo, image_name, save_preview):
    save_prev = len(save_preview) > 0 and save_preview[0] == "Save"

    # Run your CV + audio pipeline
    player.play_sheet_music_image(image, tempo, save_prev, image_name)

    audio_path = "output/output.wav"

    if save_prev:
        image_path = f"preview_directory/{image_name}/{image_name}_detection.png"
    else:
        image_path = None

    # Return filepaths / None, NOT components
    return audio_path, image_path


custom_css = """
body {
  background: linear-gradient(135deg, #1b1b2f, #16213e);
  color: #e0e0e0;
  font-family: 'Poppins', sans-serif;
}

.gradio-container {
  max-width: 1400px !important;   /* wider overall */
  width: 90% !important;           /* use 90% of the viewport width */
  margin: 40px auto !important;    /* some breathing room top/bottom */
  border-radius: 20px;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
  background-color: rgba(255,255,255,0.03);
  padding: 40px 60px;
}


h1, h2, h3 {
  text-align: center;
  color: #fff;
  font-weight: 600;
  letter-spacing: 1px;
}

button {
  background: linear-gradient(90deg, #6a11cb, #2575fc) !important;
  border: none !important;
  border-radius: 10px !important;
  color: white !important;
  font-weight: 600 !important;
  padding: 10px 20px !important;
  transition: all 0.25s ease-in-out !important;
}
button:hover {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(106,17,203,0.6);
}

label {
  font-weight: 600;
  color: #a0c4ff !important;
}

.gr-box {
  border-radius: 15px !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  background: rgba(255,255,255,0.05) !important;
}

/* Floating music notes */
@keyframes floatNotes {
  0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
  50% { opacity: 1; }
  100% { transform: translateY(-10vh) rotate(360deg); opacity: 0; }
}
.note {
  position: fixed;
  bottom: -50px;
  font-size: 25px;
  color: #c77dff;
  animation: floatNotes 10s linear infinite;
  z-index: -1;
}
.note:nth-child(2) { left: 15%; animation-duration: 12s; animation-delay: 2s; color: #9d4edd; }
.note:nth-child(3) { left: 45%; animation-duration: 9s; animation-delay: 4s; color: #7b2cbf; }
.note:nth-child(4) { left: 75%; animation-duration: 14s; animation-delay: 1s; color: #5a189a; }
"""
with gr.Blocks(css=custom_css, theme=gr.themes.Glass()) as demo:
    import base64

    # Encode image as base64 (you already have this part)
    with open("images/pic1.png", "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")

    gr.HTML(f"""
    <div style='text-align:center; margin-bottom:10px;'>
    <h1 style='margin-bottom:5px;'> Sheet Music → Audio Converter</h1>
    <p style='color:#cfcfcf; margin-top:0;'>Upload your sheet music and play your melody </p>
    <img src='data:image/png;base64,{encoded_image}' 
        alt='music logo' 
        width='360' 
        style='display:block; margin:20px auto; border-radius:20px; box-shadow:0 0 20px rgba(106,17,203,0.5);'>
    </div>

    <div class="note">♪</div>
    <div class="note">♫</div>
    <div class="note">♬</div>
    <div class="note">♩</div>
    """)


    image = gr.Image(label="Input")
    # output_image = 
    tempo = gr.Slider(minimum=60, maximum=200, value=120.0, randomize=False, label="Tempo")
    name = gr.Textbox(
            label="Image Name",
            value="image",
        )
    save = gr.CheckboxGroup(["Save"], label = "Save Previews:")
    output_audio = gr.Audio(label="Generated Audio", streaming=True, type='filepath')
    output_image = gr.Image()

    submit_btn = gr.Button("Submit")

    submit_btn.click(
        fn=wrapper2, 
        inputs=[image, tempo, name, save], 
        outputs=[output_audio, output_image])
    
#demo.serve_static_file("images/pic1.png")
demo.launch()
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
    player.play_sheet_music_image(image, tempo, save_prev, image_name)

    if save_prev:
        # Show both, supplying filepaths for image and audio
        return (
            gr.Audio(value="output/output.wav", visible=True),
            gr.Image(value=f"preview_directory/{image_name}/{image_name}_detection.png", visible=True),
        )
    else:
        return (
            gr.Audio(value="output/output.wav", visible=True),
            gr.Image(value=None, visible=False),
        )

with gr.Blocks() as demo:
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

demo.launch()
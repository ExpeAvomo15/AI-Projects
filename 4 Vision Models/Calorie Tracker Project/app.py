"""
app.py

Gradio frontend for the Calorie Tracker project.
Allows uploading a food image, analyzes with backend.py and displays the result
in a user-friendly way (HTML) and also the raw JSON.

Requirements: gradio, pillow, backend.py in the same directory.
"""

import gradio as gr
import json
from backend import analyze_image

def process_image(img, progress=gr.Progress()):
    if img is None:
        return "<div style='color:red;'>Please upload an image.</div>", ""
    progress(0, desc="Preparing analysis...")
    result = analyze_image(img)
    progress(1, desc="Analysis completed!")
    if "error" in result:
        return f"<div style='color:red;'>Error: {result['error']}</div>", result.get("raw_output", "")
    html = f"""
    <div style='font-family:Arial,sans-serif;line-height:1.4'>
      <h2 style='color:#2b7a78'>Analysis Result</h2>
      <p><b>Food:</b> {result.get('food_name','—')}</p>
      <p><b>Serving:</b> {result.get('serving_description','—')}</p>
      <p><b>Calories:</b> <span style='color:#d9534f;font-size:1.2em'>{result.get('calories','—')}</span></p>
      <p><b>Fat:</b> {result.get('fat_grams','—')} g</p>
      <p><b>Protein:</b> {result.get('protein_grams','—')} g</p>
      <p><b>Confidence:</b> {result.get('confidence_level','—')}</p>
    </div>
    """
    return html, json.dumps(result, ensure_ascii=False, indent=2)

def launch_app():
    with gr.Blocks(title="Calorie Tracker") as demo:
        gr.Markdown("## 🥗 Calorie Tracker — Analyze your food")
        with gr.Row():
            img_in = gr.Image(type="pil", label="Upload an image")
            btn = gr.Button("Analyze")
        with gr.Row():
            out_html = gr.HTML()
            out_json = gr.Textbox(label="Raw JSON", lines=12)
        btn.click(process_image, inputs=img_in, outputs=[out_html, out_json])
        demo.launch()

if __name__ == "__main__":
    launch_app()
import json
import os
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont

def generate_midpoint_gif(num1, num2, pdf_path="midpoint_trick.pdf", output_dir="."):
    midpoint = (num1 + num2) // 2
    distance = abs(num1 - midpoint)
    midpoint_square = midpoint * midpoint
    distance_square = distance * distance
    final_answer = midpoint_square - distance_square

    template_frames = convert_from_path(pdf_path)

    def draw_text_centered(draw, text, center, font, fill="black"):
        x, y = center
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        x_text = x - text_w / 2
        y_text = y - text_h / 2
        draw.text((x_text, y_text), text, font=font, fill=fill)

    font_large = ImageFont.load_default(size = 52)

    # Text placements for all 12 frames
    overlay_data = [
        # 1. Place numbers at top
        [{"text": f"{num1}             {num2}", "center": (1000, 200)}],

        # 2. Midpoint text
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)}],

        # 3. Summation text
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)}],

        # 4. Summation solution
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)},
         {"text": f"{midpoint}", "center": (1500, 300)}],

        # 5. Distance calc
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)},
         {"text": f"{midpoint}", "center": (1500, 300)},
         {"text": f"{num1}      {num2} ", "center": (525, 415)}],

        # 6. Distance calc in red box
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)},
         {"text": f"{midpoint}", "center": (1500, 300)},
         {"text": f"{num1}      {num2} ", "center": (525, 415)},
         {"text": f"{distance}", "center": (900, 450)}],

        # 7. Away text with distance
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)},
         {"text": f"{midpoint}", "center": (1500, 300)},
         {"text": f"{num1}      {num2} ", "center": (525, 415)},
         {"text": f"{distance}", "center": (900, 450)},
         {"text": f"{midpoint}", "center": (450, 615)}, # blue box
         {"text": f"{distance}", "center": (700, 615)},# red box
         {"text": f"{num1}                 {num2}", "center": (1325, 615)}], 

        # 8. Blue number bottom
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)},
         {"text": f"{midpoint}", "center": (1500, 300)},
         {"text": f"{num1}      {num2} ", "center": (525, 415)},
         {"text": f"{distance}", "center": (900, 450)},
         {"text": f"{midpoint}", "center": (450, 615)}, # blue box
         {"text": f"{distance}", "center": (700, 615)},# red box
         {"text": f"{num1}                 {num2}", "center": (1325, 615)},
         {"text": f"{midpoint}", "center": (450, 800)}], # blue number bottom

        # 9. Midpoint squared
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)},
         {"text": f"{midpoint}", "center": (1500, 300)},
         {"text": f"{num1}      {num2} ", "center": (525, 415)},
         {"text": f"{distance}", "center": (900, 450)},
         {"text": f"{midpoint}", "center": (450, 615)}, # blue box
         {"text": f"{distance}", "center": (700, 615)},# red box
         {"text": f"{num1}                 {num2}", "center": (1325, 615)},
         {"text": f"{midpoint}", "center": (450, 800)},# blue number bottom
         {"text": f"{midpoint_square}", "center": (800, 800)}], # blue number bottom square

        # 10. Red number bottom
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)},
         {"text": f"{midpoint}", "center": (1500, 300)},
         {"text": f"{num1}      {num2} ", "center": (525, 415)},
         {"text": f"{distance}", "center": (900, 450)},
         {"text": f"{midpoint}", "center": (450, 615)}, # blue box
         {"text": f"{distance}", "center": (700, 615)},# red box
         {"text": f"{num1}                 {num2}", "center": (1325, 615)},
         {"text": f"{midpoint}", "center": (450, 800)},# blue number bottom
         {"text": f"{midpoint_square}", "center": (800, 800)},# blue number bottom square
         {"text": f"{distance}", "center": (1100, 800)}], # red number bottom 

        # 11. Distance squared
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)},
         {"text": f"{midpoint}", "center": (1500, 300)},
         {"text": f"{num1}      {num2} ", "center": (525, 415)},
         {"text": f"{distance}", "center": (900, 450)},
         {"text": f"{midpoint}", "center": (450, 615)}, # blue box
         {"text": f"{distance}", "center": (700, 615)},# red box
         {"text": f"{num1}                 {num2}", "center": (1325, 615)},
         {"text": f"{midpoint}", "center": (450, 800)},# blue number bottom
         {"text": f"{midpoint_square}", "center": (800, 800)},# blue number bottom square
         {"text": f"{distance_square}", "center": (1100, 800)}], # red number bottom square

        # 12. Final solution top and bottom
        [{"text": f"{num1}             {num2}", "center": (1000, 200)},
         {"text": f"{num1}      {num2} ", "center": (675, 300)},
         {"text": f"{num1}      {num2}", "center": (1100, 275)},
         {"text": f"{midpoint}", "center": (1500, 300)},
         {"text": f"{num1}      {num2} ", "center": (525, 415)},
         {"text": f"{distance}", "center": (900, 450)},
         {"text": f"{midpoint}", "center": (450, 615)}, # blue box
         {"text": f"{distance}", "center": (700, 615)},# red box
         {"text": f"{num1}                 {num2}", "center": (1325, 615)},
         {"text": f"{midpoint}", "center": (450, 800)},# blue number bottom
         {"text": f"{midpoint_square}", "center": (800, 800)},# blue number bottom square
         {"text": f"{distance_square}", "center": (1100, 800)},# red number bottom square
         {"text": f"{final_answer}", "center": (1250, 200)},  # solution top
         {"text": f"{final_answer}", "center": (1000, 900)}], # solution bottom
    ]

    frames = []
    for i, overlays in enumerate(overlay_data):
        frame = template_frames[i].convert("RGB")
        draw = ImageDraw.Draw(frame)
        for item in overlays:
            draw_text_centered(draw, item["text"], item["center"], font_large)
        frames.append(frame)

    output_gif_path = f"{output_dir}/{num1}x{num2}.gif"
    os.makedirs(os.path.dirname(output_gif_path), exist_ok=True)
    frames[0].save(output_gif_path, save_all=True, append_images=frames[1:], duration=1000, loop=0)

    return output_gif_path

# Now, load the JSON and generate the GIFs
with open("midpoint_problems.json", "r") as f:
    problems_data = json.load(f)


for difficulty, problems in problems_data.items():
    print(f"Generating GIFs for difficulty: {difficulty}")
    for item in problems:
        parts = item["problem"].split("×")
        num1 = int(parts[0].strip())
        num2 = int(parts[1].strip())
        output_dir = f"midpointgifs/{difficulty}"
        try:
            gif_path = generate_midpoint_gif(num1, num2, pdf_path="midpoint_trick.pdf", output_dir=output_dir)
            print(f"✓ {item['problem']} → {gif_path}")
        except Exception as e:
            print(f"✗ Failed on {item['problem']}: {e}")

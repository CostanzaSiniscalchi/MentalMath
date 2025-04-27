import json
import os
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont

def generate_square5_gif(num, pdf_path="squared_5.pdf", output_dir="."):
    if num % 10 != 5:
        raise ValueError("This function only supports numbers ending in 5.")

    x = num // 10
    product = x * (x + 1)
    final_answer = num * num

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

    # --- Text placements for each frame ---
    overlay_data = [
        # 1. Show the problem at the top
        [{"text": f"{num}", "center": (900, 250)}],
        
        # 2. Drop the number below
        [{"text": f"{num}", "center": (900, 250)},
         {"text": f"{num}", "center": (1000, 350)}],
        
        # 3. Cut off 5, place x left of ×
        [{"text": f"{num}", "center": (925, 250)},
         {"text": f"{num}", "center": (1000, 350)},
         {"text": f"{x}", "center": (900, 465)}],  # Left side of ×
        
        # 4. Multiply x × (x+1) above ×
        [{"text": f"{num}", "center": (925, 250)},
         {"text": f"{num}", "center": (1000, 350)},
         {"text": f"{x}              {x+1}", "center": (1000, 465)}],  # Above 

        # 5. Same thing (show again)
        [{"text": f"{num}", "center": (925, 250)},
         {"text": f"{num}", "center": (1000, 350)},
         {"text": f"{x}              {x+1}                    {product}", "center": (1125, 465)}],
        
        # 6. Solution appears
        [{"text": f"{num}", "center": (925, 250)},
         {"text": f"{product}", "center": (1000, 465)},   # Top center
         {"text": f"{product}", "center": (875, 725)},   # Left bottom under arrow
         {"text": "25", "center": (1150, 725)}],         # Right bottom under arrow
        
        # 7. Merge to form final number
        [{"text": f"{num}", "center": (925, 250)},
         {"text": f"{product}", "center": (875, 725)},   # Left bottom under arrow
         {"text": "25", "center": (1150, 725)},
         {"text": f"{final_answer}", "center": (1000, 800)}],  # Merged number below arrows
        
        # 8. Final solution on top
        [{"text": f"{num}", "center": (925, 250)},
        {"text": f"{final_answer}", "center": (1150, 250)},
        {"text": f"{product}", "center": (1000, 465)},   # Top center
         {"text": f"{product}", "center": (875, 725)},   # Left bottom under arrow
         {"text": "25", "center": (1150, 725)},          # Right bottom under arrow
         {"text": f"{final_answer}", "center": (1000, 800)}]
    ]

    frames = []
    for i, overlays in enumerate(overlay_data):
        frame = template_frames[i].convert("RGB")
        draw = ImageDraw.Draw(frame)
        for item in overlays:
            draw_text_centered(draw, item["text"], item["center"], font_large)
        frames.append(frame)

    output_gif_path = f"{output_dir}/{num}_sq.gif"
    os.makedirs(os.path.dirname(output_gif_path), exist_ok=True)
    frames[0].save(output_gif_path, save_all=True, append_images=frames[1:], duration=1000, loop=0)

    return output_gif_path


# Now, load the JSON and generate the GIFs
with open("square5.json", "r") as f:
    problems_data = json.load(f)

for difficulty, problems in problems_data.items():
    print(f"Generating GIFs for difficulty: {difficulty}")
    for item in problems:
        problem_text = item["problem"].replace("\u00b2", "")
        num = int(problem_text)
        output_dir = f"square5gifs/{difficulty}"
        try:
            gif_path = generate_square5_gif(num, pdf_path="squared_5.pdf", output_dir=output_dir)
            print(f"✓ {item['problem']} → {gif_path}")
        except Exception as e:
            print(f"✗ Failed on {item['problem']}: {e}")

import json

# Your function from before
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont

def generate_11x_gif(num, pdf_path="11trick.pdf", output_dir="."):
    if not (10 <= num <= 999):
        raise ValueError("Only supports numbers from 10 to 999.")
    
    template_frames = convert_from_path(pdf_path)
    
    digits = [int(d) for d in str(num)]
    n = len(digits)

    if n == 2:
        d1, d2 = digits
        digit_sum = d1 + d2
        if digit_sum > 9:
            carry, mid_digit = divmod(digit_sum, 10)
            d1_final = d1 + carry
        else:
            d1_final = d1
            mid_digit = digit_sum
        overlay_core = [
            { "text": f"{d1}                     {d2}", "center": (980, 515) },
            { "text": f"{d1}    {d1}     {d2}    {d2}", "center": (980, 515) },
            { "text": f"{d1}      {digit_sum}      {d2}", "center": (980, 515) },
            { "text": f"{d1_final}      {mid_digit}      {d2}", "center": (980, 515) },
        ]
    elif n == 3:
        d1, d2, d3 = digits
        mid1 = d1 + d2
        mid2 = d2 + d3
        digits_final = []
        carry = 0
        for part in [mid1, mid2]:
            if part + carry > 9:
                c, v = divmod(part + carry, 10)
                digits_final.append(v)
                carry = c
            else:
                digits_final.append(part + carry)
                carry = 0
        d1_final = d1 + carry
        overlay_core = [
            { "text": f"{d1}                 {d2}                {d3}", "center": (980, 515) },
            { "text": f"{d1}   {mid1}   {mid2}   {d3}", "center": (980, 515) },
            { "text": f"{d1_final}   {digits_final[0]}   {digits_final[1]}   {d3}", "center": (980, 515) },
        ]
    else:
        raise ValueError("Only supports 2 or 3 digit numbers.")

    final_answer = num * 11

    def draw_text_centered(draw, text, center, font, box_size=(300, 60), fill="black"):
        x, y = center
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        x_text = x - text_w / 2
        y_text = y - text_h / 2
        draw.text((x_text, y_text), text, font=font, fill=fill)

    font = ImageFont.load_default(size=52)

    top_frame = { "text": f"{num}", "center": (850, 190) }
    sol_top = { "text": f"{final_answer}", "center": (1200, 190) }
    num_frame = { "text": f"{num}", "center": (980, 340) }
    sol_bottom = { "text": f"{final_answer}", "center": (980, 700) }

    overlay_data = [
        [top_frame],
        [top_frame, num_frame],
        [top_frame, num_frame],
        [top_frame, num_frame, overlay_core[0]],
        *([[top_frame, num_frame, overlay_core[i]] for i in range(1, len(overlay_core))]),
        [top_frame, sol_top, num_frame, overlay_core[-1], sol_bottom]
    ]

    frames = []
    for i, overlays in enumerate(overlay_data):
        frame = template_frames[i].convert("RGB")
        draw = ImageDraw.Draw(frame)
        for item in overlays:
            draw_text_centered(draw, item["text"], item["center"], font)
        frames.append(frame)

    output_gif_path = f"{output_dir}/11x{num}_sol.gif"
    frames[0].save(output_gif_path, save_all=True, append_images=frames[1:], duration=1000, loop=0)
    return output_gif_path


# Now, load the JSON and generate the GIFs
with open("multiply11.json", "r") as f:
    problems_data = json.load(f)

for difficulty, problems in problems_data.items():
    print(f"Generating GIFs for difficulty: {difficulty}")
    for item in problems:
        num_str = item["problem"].split("×")[1].strip()
        num = int(num_str)
        try:
            gif_path = generate_11x_gif(num, pdf_path="11trick.pdf", output_dir=f"mult11gifs/{difficulty}")
            print(f"✓ {item['problem']} → {gif_path}")
        except Exception as e:
            print(f"✗ Failed on {item['problem']}: {e}")

from PIL import Image, ImageDraw, ImageFont
import os

def create_ocr_visualization(
        image_path: str,
        detections: list[dict],
        output_path: str
):
    # open image
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)   # ✅ use ImageDraw, not Image

    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    for detection in detections:
        text = detection["text"]
        confidence = detection["confidence"]
        box = detection["bounding_box"]

        if len(box) != 4:
            continue

        x1, y1, x2, y2 = box

        # draw rectangle box
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

        label = f"{text} ({confidence:.2f})"

        # calculate text size
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # label background
        draw.rectangle([
            x1,
            max(0, y1 - text_height - 4),
            x1 + text_width + 6,
            y1
        ], fill="red")

        # label text
        draw.text(
            (x1 + 3, max(0, y1 - text_height - 2)),
            label,
            fill="white",
            font=font
        )

    # ✅ save once after loop
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)

    return output_path

from app.services.ocr_service import OCRService
from app.services.ocr_visualization_service import (
    create_ocr_visualization
)


# -----------------------------------------
# 1. Image path
# -----------------------------------------

image_path = r"uploads\Screenshot (689)_enhanced.png"

output_path = r"uploads\Screenshot (689)_ocr.png"


# -----------------------------------------
# 2. Run OCR
# -----------------------------------------

print("Creating OCR service...")

ocr_service = OCRService()

print("Running OCR...")

ocr_data = ocr_service.process_image(
    image_path
)

print("OCR completed.")

# -----------------------------------------
# 3. Get ALL detections from OCR
# -----------------------------------------

detections = ocr_data["detections"]

print(
    f"Total detections: {len(detections)}"
)


# -----------------------------------------
# 4. Create visualization
# -----------------------------------------

result = create_ocr_visualization(
    image_path=image_path,
    detections=detections,
    output_path=output_path
)


# -----------------------------------------
# 5. Print result
# -----------------------------------------

print("Visualization created successfully!")

print("Output:", result)
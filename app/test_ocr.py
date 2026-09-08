from app.services.ocr_service import OCRService

image_path = r"uploads\Screenshot (689)_enhanced.png"

print("STEP 1: Creating OCR service")

ocr_service = OCRService()

print("STEP 2: Running OCR")

result = ocr_service.process_image(image_path)

print("STEP 3: OCR FINISHED")

print("RESULT:")
print(result)
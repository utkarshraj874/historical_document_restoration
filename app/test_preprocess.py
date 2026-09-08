from app.services.image_service import preprocess_image


image_path = r"uploads\Screenshot (689).png"

print("STEP 1: Starting preprocessing...")

try:
    enhanced_path = preprocess_image(image_path)

    print("STEP 2: Preprocessing successful!")
    print("Enhanced image:", enhanced_path)

except Exception as e:
    print("PREPROCESSING ERROR:", e)
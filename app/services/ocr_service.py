
import time


class OCRUnavailableError(RuntimeError):
    """Raised when the optional PaddleOCR runtime is not available."""


class OCRService:

    def __init__(self):
        # Import PaddleOCR only when an OCR request is made.  Importing it at
        # module load time prevents the entire FastAPI application from
        # starting when a serverless deployment does not include PaddleOCR.
        try:
            from paddleocr import PaddleOCR
        except ModuleNotFoundError as exc:
            if exc.name == "paddleocr":
                raise OCRUnavailableError(
                    "OCR is not available in this deployment because the "
                    "PaddleOCR runtime is not installed."
                ) from exc
            raise

        self.ocr = PaddleOCR(lang="en", device="cpu")

    def process_image(self, image_path: str):

        start_time = time.perf_counter()

        result = self.ocr.predict(image_path)

        processing_time = (
            time.perf_counter() - start_time
        )

        detections = []
        all_text = []
        all_scores = []

        # PaddleOCR returns a list
        for page in result:

            # -----------------------------
            # Extract OCR fields
            # -----------------------------

            texts = page.get("rec_texts", [])
            scores = page.get("rec_scores", [])
            boxes = page.get("rec_boxes", [])

            # -----------------------------
            # Process every detected text
            # -----------------------------

            for text, score, box in zip(
                texts,
                scores,
                boxes
            ):

                # Convert numpy values to Python types
                text = str(text)
                confidence = float(score)

                bounding_box = [
                    int(value)
                    for value in box
                ]

                detections.append({
                    "text": text,
                    "confidence": confidence,
                    "bounding_box": bounding_box
                })

                all_text.append(text)
                all_scores.append(confidence)

        # -----------------------------
        # Combine all text
        # -----------------------------

        raw_text = "\n".join(all_text)

        # -----------------------------
        # Average confidence
        # -----------------------------

        if all_scores:

            average_confidence = (
                sum(all_scores) /
                len(all_scores)
            )

        else:

            average_confidence = 0.0

        return {
            "raw_text": raw_text,
            "average_confidence": average_confidence,
            "detections": detections,
            "processing_time": processing_time,
            "language": "en"
        }


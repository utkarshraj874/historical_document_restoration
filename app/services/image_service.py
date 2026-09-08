import os
import cv2


def preprocess_image(
    input_path: str,
    output_path: str | None = None
):
    """
    Enhance document image while preserving
    the original appearance and colors.
    """

    # -----------------------------------------
    # 1. Check input
    # -----------------------------------------

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Image not found: {input_path}"
        )

    # -----------------------------------------
    # 2. Read image
    # -----------------------------------------

    image = cv2.imread(input_path)

    if image is None:
        raise ValueError(
            f"Could not read image: {input_path}"
        )

    # -----------------------------------------
    # 3. Convert to LAB
    # -----------------------------------------

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l_channel, a_channel, b_channel = cv2.split(lab)

    # -----------------------------------------
    # 4. Mild contrast enhancement
    # -----------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=1.5,
        tileGridSize=(8, 8)
    )

    enhanced_l = clahe.apply(l_channel)

    # -----------------------------------------
    # 5. Put channels back
    # -----------------------------------------

    enhanced_lab = cv2.merge(
        (
            enhanced_l,
            a_channel,
            b_channel
        )
    )

    enhanced = cv2.cvtColor(
        enhanced_lab,
        cv2.COLOR_LAB2BGR
    )

    # -----------------------------------------
    # 6. Mild sharpening
    # -----------------------------------------

    blurred = cv2.GaussianBlur(
        enhanced,
        (0, 0),
        1
    )

    enhanced = cv2.addWeighted(
        enhanced,
        1.15,
        blurred,
        -0.15,
        0
    )

    # -----------------------------------------
    # 7. Output path
    # -----------------------------------------

    if output_path is None:

        directory = os.path.dirname(input_path)

        filename = os.path.basename(input_path)

        name, extension = os.path.splitext(
            filename
        )

        output_path = os.path.join(
            directory,
            f"{name}_enhanced{extension}"
        )

    # -----------------------------------------
    # 8. Save
    # -----------------------------------------

    success = cv2.imwrite(
        output_path,
        enhanced
    )

    if not success:
        raise ValueError(
            f"Could not save enhanced image: {output_path}"
        )

    return output_path
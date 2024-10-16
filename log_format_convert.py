import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2
import rawpy
import numpy as np
import imageio

# Function to apply d-log curve
def d_log_curve(linear_rgb):
    # Assuming d-log follows a curve similar to other log profiles
    a = 0.17883277  # DJI d-log parameter, adjust as needed
    b = 0.28466892
    c = 0.55991073
    
    # Efficient application to the entire array using numpy operations
    d_log = np.where(
        linear_rgb > 0.01,
        a * np.log10(linear_rgb + b) + c,
        linear_rgb * 5.6  # Approximation for very dark regions
    )
    return d_log

# Function to apply s-log3 curve (Sony Log)
def s_log3_curve(linear_rgb):
    # Parameters for s-log3 from Sony white papers
    s_log = np.where(
        linear_rgb >= 0.011,
        (420.0 + np.log10(linear_rgb * 261.5 + 1.0) / np.log10(10) * 155.0) / 1023.0,
        (linear_rgb * (171.2102946929 / 0.011)) / 1023.0
    )
    return s_log

# Process DNG file and apply log curves
def process_dng(input_file, output_file_d_log, output_file_s_log):
    # Read raw image data from DNG
    with rawpy.imread(input_file) as raw:
        # Convert raw image to RGB float32 image (linear)
        rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=16)
    # Resize the image
    height, width = rgb.shape[:2]
    new_height = 480
    new_width = int(width * (new_height / height))
    rgb_resized = cv2.resize(rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
    linear_rgb = rgb_resized / 65535.0  # Normalize to range [0, 1]

    # Apply d-log and s-log3 curves
    d_log_image = d_log_curve(linear_rgb)
    s_log_image = s_log3_curve(linear_rgb)

    # # Convert back to 16-bit format (scaling to the range [0, 65535])
    # d_log_image_16bit = np.clip(d_log_image * 65535, 0, 65535).astype(np.uint16)
    # s_log_image_16bit = np.clip(s_log_image * 65535, 0, 65535).astype(np.uint16)

    # Save the 16-bit images
    imageio.imwrite(output_file_d_log, d_log_image.astype(np.float32), format='exr')
    imageio.imwrite(output_file_s_log, s_log_image.astype(np.float32), format='exr')

    # # Save to 8-bit PNG for visualization
    # imageio.imwrite(output_file_d_log, (d_log_image * 255).clip(0, 255).astype(np.uint8))
    # imageio.imwrite(output_file_s_log, (s_log_image * 255).clip(0, 255).astype(np.uint8))


# Example usage
input_dng = 'test/DJI_20240806140437_0001.DNG'  # Path to your DNG file
output_d_log = 'test/output_d_log_16bit.exr'  # Output image with d-log applied (16-bit)
output_s_log = 'test/output_s_log_16bit.exr'  # Output image with s-log3 applied (16-bit)
# output_d_log = 'test/output_d_log_16bit.png'  # Output image with d-log applied (16-bit)
# output_s_log = 'test/output_s_log_16bit.png'  # Output image with s-log3 applied (16-bit)

process_dng(input_dng, output_d_log, output_s_log)

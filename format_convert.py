import numpy as np
import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2
import rawpy
import imageio

AUTO_BRIGHT_THR = 0.001

def raw_to_srgb(raw_image_path, output_path):
    # Open the RAW image
    with rawpy.imread(raw_image_path) as raw:
        # Process the RAW image
        rgb = raw.postprocess(gamma=(1,1), use_camera_wb=True, no_auto_bright=False, auto_bright_thr=AUTO_BRIGHT_THR, output_bps=16)

    # Resize the image
    height, width = rgb.shape[:2]
    new_width = 1024
    new_height = int(height * (new_width / width))
    rgb_resized = cv2.resize(rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Convert to float32 and scale to [0, 1]
    rgb_float = rgb_resized.astype(np.float32) / 65535.0

    # Apply sRGB transformation
    rgb_srgb = np.where(rgb_float <= 0.0031308,
                        12.92 * rgb_float,
                        1.055 * np.power(rgb_float, 1/2.4) - 0.055)

    # Scale to [0, 255] and convert to 8-bit
    rgb_8bit = (rgb_srgb * 255).clip(0, 255).astype(np.uint8)

    # Save as JPG
    cv2.imwrite(output_path, cv2.cvtColor(rgb_8bit, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 100])

def raw_to_linear(raw_image_path, output_path):
    # Open the RAW image
    with rawpy.imread(raw_image_path) as raw:
        # Process the RAW image
        rgb = raw.postprocess(gamma=(1,1), use_camera_wb=True, no_auto_bright=False, auto_bright_thr=AUTO_BRIGHT_THR, output_bps=16)
    # Resize the image
    height, width = rgb.shape[:2]
    new_width = 1024
    new_height = int(height * (new_width / width))
    rgb_resized = cv2.resize(rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Save as 16-bit TIFF
    imageio.imwrite(output_path, rgb_resized, format="tiff")

def raw_to_log(raw_image_path, output_path):
    # Open the RAW image
    with rawpy.imread(raw_image_path) as raw:
        # Process the RAW image
        rgb = raw.postprocess(gamma=(1,1), use_camera_wb=True, no_auto_bright=False, auto_bright_thr=AUTO_BRIGHT_THR, output_bps=16)

    # Resize the image
    height, width = rgb.shape[:2]
    new_width = 1024
    new_height = int(height * (new_width / width))
    rgb_resized = cv2.resize(rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Convert to float32
    rgb_float = rgb_resized.astype(np.float32)

    # Apply natural log to non-zero values
    rgb_log = np.zeros_like(rgb_float)
    non_zero_mask = rgb_float > 0
    rgb_log[non_zero_mask] = np.log(rgb_float[non_zero_mask])

    # output the max value
    print("Max value: ", np.max(rgb_log))

    # Save as float32 EXR
    imageio.imwrite(output_path, rgb_log, format="tiff")

# Example usage:
# raw_to_srgb("test/DJI_20240806140437_0001.DNG", "test/output_srgb.jpg")
# raw_to_linear("test/DJI_20240806140437_0001.DNG", "test/output_linear.tiff")
# raw_to_log("test/DJI_20240806140437_0001.DNG", "test/output_log.exr")
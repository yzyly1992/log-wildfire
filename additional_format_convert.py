import numpy as np
import rawpy
import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2
import imageio

AUTO_BRIGHT_THR = 0.001

def raw_to_xyz(raw_image_path, output_path=None):
    with rawpy.imread(raw_image_path) as raw:
        # Process the RAW image directly to XYZ
        xyz = raw.postprocess(
            gamma=(1,1), use_camera_wb=True, 
            no_auto_bright=False, 
            auto_bright_thr=AUTO_BRIGHT_THR,
            output_color=rawpy.ColorSpace.XYZ,
            output_bps=16
        )

    # Resize the image
    height, width = xyz.shape[:2]
    new_width = 1024
    new_height = int(height * (new_width / width))
    xyz_resized = cv2.resize(xyz, (new_width, new_height), interpolation=cv2.INTER_AREA)


    # Normalize to [0, 1] range
    xyz_float = xyz_resized.astype(np.float32) / 65535.0
    # Save as EXR
    if output_path is not None: 
        imageio.imwrite(output_path, xyz_float, format="tiff")
    return xyz_float

def xyz_to_ucs(xyz):
    X, Y, Z = xyz[:, :, 0], xyz[:, :, 1], xyz[:, :, 2]
    u_prime = 4 * X / (X + 15 * Y + 3 * Z)
    v_prime = 9 * Y / (X + 15 * Y + 3 * Z)
    
    # Calculate L*
    L_star = np.where(Y > 0.008856,
                      116 * Y ** (1/3) - 16,
                      903.3 * Y)
    
    # Calculate u* and v*
    u_star = 13 * L_star * (u_prime - 0.19793943)
    v_star = 13 * L_star * (v_prime - 0.46831096)
    
    return np.stack([L_star, u_star, v_star], axis=-1)

def xyz_to_lms(xyz):
    # Bradford transformation matrix
    bradford_matrix = np.array([
        [ 0.8951,  0.2664, -0.1614],
        [-0.7502,  1.7135,  0.0367],
        [ 0.0389, -0.0685,  1.0296]
    ])
    return np.dot(xyz, bradford_matrix.T)

def xyz_to_oklab(xyz):
    # XYZ to LMS
    lms_matrix = np.array([
        [ 0.8190224,  0.3619062,  -0.1288286],
        [ 0.0329836,  0.9292868,   0.0361308],
        [ 0.0481771,  0.2642656,   0.6335478]
    ])
    lms = np.dot(xyz, lms_matrix.T)

    # Non-linear transformation
    lms_non_linear = np.cbrt(lms)
    
    # LMS to Oklab
    oklab_matrix = np.array([
        [ 0.2104542553,  0.7936177850, -0.0040720468],
        [ 1.9779984951, -2.4285922050,  0.4505937099],
        [ 0.0259040371,  0.7827717662, -0.8086757660]
    ])
    return np.dot(lms_non_linear, oklab_matrix.T)

def raw_to_ucs(raw_image_path, output_path):
    xyz = raw_to_xyz(raw_image_path)
    ucs = xyz_to_ucs(xyz)
    imageio.imwrite(output_path, ucs.astype(np.float32), format="tiff")

def raw_to_lms(raw_image_path, output_path):
    xyz = raw_to_xyz(raw_image_path)
    lms = xyz_to_lms(xyz)
    imageio.imwrite(output_path, lms.astype(np.float32), format="tiff")

def raw_to_oklab(raw_image_path, output_path):
    xyz = raw_to_xyz(raw_image_path)
    oklab = xyz_to_oklab(xyz)
    imageio.imwrite(output_path, oklab.astype(np.float32), format="tiff")

# Example usage:
# raw_to_xyz("test/DJI_20240806140437_0001.DNG", "output_ucs.exr")
# raw_to_ucs("test/DJI_20240806140437_0001.DNG", "output_ucs.exr")
# raw_to_lms("test/DJI_20240806140437_0001.DNG", "output_lms.exr")
# raw_to_oklab("test/DJI_20240806140437_0001.DNG", "output_oklab.exr")
import os
from log_format_convert import process_dng

def batch_d_s_log(input_dir, d_output_dir, s_output_dir):
    # Create output directories if they do not exist
    os.makedirs(d_output_dir, exist_ok=True)
    os.makedirs(s_output_dir, exist_ok=True)
    
    # Process each DNG file in the input directory using raw_to_log
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.DNG'):
                input_path = os.path.join(root, file)
                d_output_path = os.path.join(d_output_dir, file.replace('.DNG', '.tiff'))
                s_output_path = os.path.join(s_output_dir, file.replace('.DNG', '.tiff'))
                process_dng(input_path, d_output_path, s_output_path)


if __name__ == "__main__":
    input_dir = 'test/test_dng'  # Path to the input directory
    d_output_dir = 'test/test_d_log'  # Path to the output directory
    s_output_dir = 'test/test_s_log'  # Path to the output directory

    batch_d_s_log(input_dir, d_output_dir, s_output_dir)
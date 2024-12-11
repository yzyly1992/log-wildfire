import os
from additional_format_convert import raw_to_ucs

def batch_ucs(input_dir, output_dir):
    # Create output directories if they do not exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each DNG file in the input directory using raw_to_log
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.DNG'):
                input_path = os.path.join(root, file)
                output_path = os.path.join(output_dir, file.replace('.DNG', '.tiff'))
                raw_to_ucs(input_path, output_path)

if __name__ == "__main__":
    input_dir = 'test/train_dng'  # Path to the input directory
    output_dir = 'test/train_ucs'  # Path to the output directory

    batch_ucs(input_dir, output_dir)
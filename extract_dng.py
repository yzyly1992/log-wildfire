import json
import os
import shutil

def load_image_names_from_json(json_file):
    """Load image names from a JSON file."""
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Extract file names
    image_names = [img['file_name'] for img in data.get('images', [])]
    return image_names

def format_image_names(image_names):
    """Format image names to the desired output."""
    formatted_names = []
    for name in image_names:
        formatted_name = name.split('.rf')[0].replace('_jpg', '.DNG')
        formatted_names.append(formatted_name)
    return formatted_names

def find_and_copy_images(formatted_names, target_folder, output_folder):
    """Find images in the target folder and copy them to the output folder."""
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Walk through the target folder
    for root, _, files in os.walk(target_folder):
        for file in files:
            if file in formatted_names:
                # Construct full file path
                source_path = os.path.join(root, file)
                destination_path = os.path.join(output_folder, file)
                shutil.copy2(source_path, destination_path)  # Copy file with metadata
                print(f"Copied: {source_path} to {destination_path}")

def main(json_file, target_folder, output_folder):
    image_names = load_image_names_from_json(json_file)
    formatted_names = format_image_names(image_names)
    find_and_copy_images(formatted_names, target_folder, output_folder)

if __name__ == "__main__":
    # Define your file paths here
    json_file = 'test/train_annotations.coco.json'  # Path to your JSON file
    target_folder = '/home/david-yang/Downloads/Drone Data'  # Path to the folder to search images
    output_folder = 'test/train_dng'  # Path to the output folder

    main(json_file, target_folder, output_folder)

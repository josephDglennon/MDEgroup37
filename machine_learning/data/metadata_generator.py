import os

def get_file_names(directory):
    file_names = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            file_names.append(filename)
    return file_names

def replace_underscores_with_commas(file_names):

    return [filename.replace('_', ',') for filename in file_names]

def write_to_file(file_names, output_file):
    with open(output_file, 'w') as f:
        for filename in file_names:
            f.write(filename + '\n')

if __name__ == "__main__":
    # Directory containing the files
    directory = "drone_A/A/test/mic1"

    # Output file name
    output_file = "meta.txt"

    # Get file names
    file_names = get_file_names(directory)

    # Replace underscores with commas
    file_names_with_commas = replace_underscores_with_commas(file_names)

    # Write file names with commas to the output file
    write_to_file(file_names_with_commas, output_file)

    print(f"File names written to '{output_file}' with underscores replaced by commas.")

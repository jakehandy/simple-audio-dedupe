# Simple audio dedupe

A simple Python script to detect exact duplicate audio files in a specified directory. The script computes an MD5 hash for each audio file and groups files with matching hashes as duplicates. You can either output the duplicate file pairs to a CSV file or delete the duplicates automatically (via a command-line toggle).

## Features

- **Audio File Detection:** Scans a directory for audio files (supports common extensions like `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`, `.m4a`).
- **Duplicate Detection:** Computes an MD5 hash for each file and identifies exact duplicates.
- **Flexible Output Options:**
  - **CSV Mode:** Write duplicate file pairs (original and duplicate) to a CSV file.
  - **Delete Mode:** Remove duplicate files (keeps the first instance in each duplicate group).

## Prerequisites

- **Python 3.6+**: Ensure you have Python 3 installed on your system.
- No external Python packages are required; the script uses standard libraries.

## Installation

1. **Download the Script:**
   - Clone this repository or download the `simple-audio-dedupe.py` file directly.

2. **Make the Script Executable (Optional for Unix/Linux/Mac):**
   ```bash
   chmod +x simple-audio-dedupe.py
   ```


## Usage

Run the script from the command line with the following syntax:

```bash
python simple-audio-dedupe.py <directory> [--action {csv,delete}] [--csv_file CSV_FILE]
```

### Command-Line Arguments

- `<directory>`: The path to the directory containing your audio files.
- `--action`: (Optional) Determines the operation mode.
  - `csv` (default): Writes duplicate file pairs to a CSV file.
  - `delete`: Deletes duplicate files (preserving the first file found in each duplicate group).
- `--csv_file`: (Optional) The name or path of the CSV file where duplicates will be recorded. Defaults to `duplicates.csv`. This option is only used when `--action` is set to `csv`.

### Examples

1. **Output Duplicates to CSV:**
   ```bash
   python simple-audio-dedupe.py /path/to/audio/files --action csv --csv_file duplicates.csv
   ```

2. **Delete Duplicate Files:**
   ```bash
   python simple-audio-dedupe.py /path/to/audio/files --action delete
   ```

## How It Works

1. **File Hashing:**  
   The script reads each audio file in chunks and computes its MD5 hash. Files with the same content produce the same hash.

2. **Duplicate Identification:**  
   Files are grouped by their computed hash. If a group contains more than one file, it indicates duplicates.

3. **Handling Duplicates:**
   - **CSV Mode:**  
     For each group of duplicates, the first file is considered the original, and each additional file is paired with it in the CSV output.
   - **Delete Mode:**  
     The script deletes all duplicate files, preserving only the first file in each group.

## License

This project is licensed under the MIT License.

## Disclaimer

Use this script at your own risk. It is highly recommended to back up your files before running deletion operations.

## Contributing

Contributions are welcome! If you have suggestions, improvements, or bug fixes, please fork the repository and submit a pull request.

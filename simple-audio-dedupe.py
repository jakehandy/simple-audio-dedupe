#!/usr/bin/env python3
"""
A Python script to detect exact duplicate audio files in a specified directory.

The script computes a hash (MD5) for each audio file (based on its binary content)
and groups files that have the same hash. For each group of duplicate files,
the first file is considered the "original" and subsequent files are flagged as duplicates.

The script offers two modes (toggled via a command-line argument):
    1. CSV mode: Write duplicate file pairs to a CSV file.
       Each row contains:
         - File 1 (original file)
         - File 2 (duplicate file)
         - Duplicate flag (set to TRUE)
    2. Delete mode: Delete duplicate files (all but the first file in each duplicate group).

Usage:
    python simple-audio-dedupe.py <directory> [--action {csv,delete}] [--csv_file CSV_FILE]

Example:
    python simple-audio-dedupe.py /path/to/audio/files --action csv --csv_file duplicates.csv
    python simple-audio-dedupe.py /path/to/audio/files --action delete
"""

import os
import sys
import argparse
import hashlib
import csv

# ANSI escape codes for colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def update_progress(current, total, prefix="Processing", bar_length=40):
    """
    Display or update a progress bar in the terminal.

    Args:
        current (int): Current progress count.
        total (int): Total count.
        prefix (str, optional): Text prefix for the progress bar.
        bar_length (int, optional): Character length of the progress bar.
    """
    fraction = current / total
    filled_length = int(bar_length * fraction)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f"\r{prefix}: |{bar}| {current}/{total} files")
    sys.stdout.flush()


def compute_hash(file_path, chunk_size=8192):
    """
    Compute the MD5 hash of a file.

    Reads the file in chunks to handle large files without loading them entirely
    into memory.

    Args:
        file_path (str): Path to the file.
        chunk_size (int, optional): Size (in bytes) of each read chunk. Defaults to 8192.

    Returns:
        str: The hexadecimal MD5 hash of the file.
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks and update the hash
            while chunk := f.read(chunk_size):
                hash_md5.update(chunk)
    except Exception as e:
        print(f"\n{RED}Error reading file {file_path}: {e}{RESET}")
        return None
    return hash_md5.hexdigest()


def find_duplicates(directory, audio_extensions=None):
    """
    Scan the specified directory for audio files and group duplicates based on their hash.

    Only files whose extension is in the provided list of audio_extensions are considered.
    If no extension list is provided, a default set of common audio extensions is used.

    Args:
        directory (str): Path to the directory to scan.
        audio_extensions (set, optional): Set of allowed audio file extensions. Defaults to None.

    Returns:
        dict: A dictionary where each key is a file hash and the value is a list of file paths
              having that hash.
    """
    if audio_extensions is None:
        # Set of common audio file extensions (in lowercase)
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'}

    hash_dict = {}
    entries = os.listdir(directory)
    total_entries = len(entries)

    for i, entry in enumerate(entries, start=1):
        update_progress(i, total_entries, prefix="Scanning files")
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            ext = os.path.splitext(entry)[1].lower()
            if ext in audio_extensions:
                file_hash = compute_hash(full_path)
                if file_hash:
                    hash_dict.setdefault(file_hash, []).append(full_path)
    sys.stdout.write("\n")
    return hash_dict


def write_duplicates_to_csv(duplicates, csv_file_path="duplicates.csv"):
    """
    Write duplicate file pairs to a CSV file.

    For each group of duplicate files (files with the same hash), the first file is
    considered the original and each subsequent file is written as a duplicate pair.

    The CSV file will have a header with the columns: "File 1", "File 2", "Duplicate".

    Args:
        duplicates (dict): Dictionary mapping file hashes to lists of file paths.
        csv_file_path (str, optional): Output CSV file path. Defaults to "duplicates.csv".
    """
    total_pairs = sum(len(file_list) - 1 for file_list in duplicates.values() if len(file_list) > 1)
    pair_count = 0

    try:
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["File 1", "File 2", "Duplicate"])

            for file_hash, file_list in duplicates.items():
                if len(file_list) > 1:
                    original = file_list[0]
                    for duplicate in file_list[1:]:
                        csv_writer.writerow([original, duplicate, "TRUE"])
                        pair_count += 1
                        update_progress(pair_count, total_pairs, prefix="Writing CSV")
            sys.stdout.write("\n")
        print(f"{GREEN}CSV file with duplicates written to: {csv_file_path}{RESET}")
    except Exception as e:
        print(f"\n{RED}Error writing CSV file: {e}{RESET}")


def delete_duplicates(duplicates):
    """
    Delete duplicate audio files.

    For each group of duplicate files (files with the same hash), the first file is
    considered the original and is kept, while all other files are deleted.

    Args:
        duplicates (dict): Dictionary mapping file hashes to lists of file paths.
    """
    total_duplicates = sum(len(file_list) - 1 for file_list in duplicates.values() if len(file_list) > 1)
    deleted_count = 0

    for file_hash, file_list in duplicates.items():
        if len(file_list) > 1:
            original = file_list[0]
            for duplicate in file_list[1:]:
                try:
                    os.remove(duplicate)
                    deleted_count += 1
                    update_progress(deleted_count, total_duplicates, prefix="Deleting duplicates")
                except Exception as e:
                    print(f"\n{RED}Error deleting file {duplicate}: {e}{RESET}")
    sys.stdout.write("\n")
    print(f"{GREEN}Deleted {deleted_count} duplicate file(s).{RESET}")


def main():
    """
    Main function to parse command line arguments, detect duplicate audio files,
    and perform the requested action (write to CSV or delete duplicates).
    """
    parser = argparse.ArgumentParser(
        description="Find and handle duplicate audio files in a directory."
    )
    parser.add_argument(
        "directory",
        help="Path to the directory containing audio files."
    )
    parser.add_argument(
        "--action",
        choices=["csv", "delete"],
        default="csv",
        help="Action to perform: 'csv' to write duplicates to a CSV file, 'delete' to remove duplicate files."
    )
    parser.add_argument(
        "--csv_file",
        default="duplicates.csv",
        help="Name of the CSV file to write duplicate pairs to (only used when action is 'csv')."
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"{RED}Error: {args.directory} is not a valid directory.{RESET}")
        sys.exit(1)

    # Print a banner
    print(f"{YELLOW}======================================")
    print("      Simple Audio Dedupe")
    print("======================================")
    print(f"{RESET}")

    print(f"{YELLOW}Scanning directory: {args.directory}{RESET}")
    duplicates = find_duplicates(args.directory)

    # Count duplicate groups and files
    duplicate_groups = sum(1 for files in duplicates.values() if len(files) > 1)
    duplicate_files = sum(len(files) - 1 for files in duplicates.values() if len(files) > 1)

    if duplicate_groups == 0:
        print(f"{GREEN}No duplicate audio files found.{RESET}")
        return

    print(f"{YELLOW}Found {duplicate_groups} duplicate group(s) with {duplicate_files} duplicate file(s).{RESET}")

    # Perform the selected action based on the toggle
    if args.action == "csv":
        write_duplicates_to_csv(duplicates, args.csv_file)
    elif args.action == "delete":
        delete_duplicates(duplicates)
    else:
        print(f"{RED}Unknown action. Exiting.{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
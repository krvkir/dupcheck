import os
import hashlib
import sqlite3
import logging
from typing import List
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_database(db_path: str):
    """Database setup."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create a table for central directory.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_hashes (
            path TEXT NOT NULL,
            size INTEGER NOT NULL,
            is_central BOOLEAN NOT NULL,
            hash TEXT NOT NULL
        )
    ''')
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_path ON file_hashes (path)')
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_hash ON file_hashes (hash)')
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_is_central ON file_hashes (is_central)')
    conn.commit()
    conn.close()


def calculate_hash(file_path: str) -> str:
    """Calculate the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def save_hash(
        db_path: str, file_path: str, file_hash: str, is_central: bool = False):
    """Save file hash to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO file_hashes (path, size, is_central, hash)
        VALUES (?, ?, ?, ?)
    ''', (file_path, os.path.getsize(file_path), is_central, file_hash))
    conn.commit()
    conn.close()
    logging.info(f"Processed and saved: {file_path}")


def get_cached_hash(db_path: str, file_path: str):
    """
    For a given file path outside the central dir, check if its hash
    was already calculated. If so, return it.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT hash, size FROM file_hashes
        WHERE path = ?
    ''', (file_path,))
    result = cursor.fetchone()
    conn.close()
    if result and result[1] == os.path.getsize(file_path):
        return result[0]
    return None


def check_for_duplicates(db_path: str, file_path: str) -> List[str]:
    """Check for duplicates against the database."""
    # If there is such a path and file size didn't change, use cached value.
    file_hash = get_cached_hash(db_path, file_path)
    if not file_hash:
        # ... if no entry found, calculate hash and save it.
        file_hash = calculate_hash(file_path)
        save_hash(db_path, file_path, file_hash, is_central=False)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT path FROM file_hashes WHERE is_central AND hash = ?
    ''', (file_hash,))
    duplicates = cursor.fetchall()
    conn.close()
    logging.info(f"Checked for duplicates: {file_path}")
    return [dup[0] for dup in duplicates]


def process_file(db_path: str, file_path: str):
    """Process a single file from a central directory."""
    file_hash = get_cached_hash(db_path, file_path)
    if not file_hash:
        file_hash = calculate_hash(file_path)
        save_hash(db_path, file_path, file_hash, is_central=True)


def process_central_directory(db_path: str, dir_path: str, max_workers: int=4):
    """Main function to process a directory with multi-threading"""
    setup_database(db_path)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for root, dirs, files in os.walk(dir_path):
            file_paths = [os.path.join(root, file) for file in files]
            executor.map(lambda p: process_file(db_path, p), file_paths)


def check_file(db_path: str, file_path: str):
    """Check a file for duplicates and print the result."""
    duplicates = check_for_duplicates(db_path, file_path)
    if not duplicates:
        print(f"{file_path} is unique!")
        # for dup in duplicates:
        #     print(f" - {dup}")


def check_directory(db_path: str, check_dir_path: str):
    """Process files in another directory to check for duplicates"""
    for root, dirs, files in os.walk(check_dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            check_file(db_path, file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            check_directory(db_path, dir_path)

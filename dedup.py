import os
import hashlib
import sqlite3
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_database(db_path: str):
    """ Database setup """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_hashes (
            path TEXT NOT NULL,
            hash TEXT NOT NULL
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON file_hashes (hash)')
    conn.commit()
    conn.close()


def calculate_hash(file_path: str) -> str:
    """Function to calculate the MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def save_hash(db_path: str, file_path: str, file_hash: str):
    """Function to save file hash to the database (only used for central directory)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO file_hashes (path, hash) VALUES (?, ?)', (file_path, file_hash))
    conn.commit()
    conn.close()
    logging.info(f"Processed and saved: {file_path}")


def check_for_duplicates(db_path: str, file_path: str) -> List[str]:
    """Function to check for duplicates against the database"""
    file_hash = calculate_hash(file_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM file_hashes WHERE hash = ?', (file_hash,))
    duplicates = cursor.fetchall()
    conn.close()
    logging.info(f"Checked for duplicates: {file_path}")
    return [dup[0] for dup in duplicates]


def process_file(db_path: str, file_path: str):
    """Process a single file"""
    file_hash = calculate_hash(file_path)
    save_hash(db_path, file_path, file_hash)


def process_central_directory(db_path: str, dir_path: str, max_workers: int=4):
    """Main function to process a directory with multi-threading"""
    setup_database(db_path)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for root, dirs, files in os.walk(dir_path):
            file_paths = [os.path.join(root, file) for file in files]
            executor.map(lambda p: process_file(db_path, p), file_paths)



def process_check_directory(db_path: str, check_dir_path: str):
    """Process files in another directory to check for duplicates"""
    for root, dirs, files in os.walk(check_dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            duplicates = check_for_duplicates(db_path, file_path)
            if duplicates:
                print(f"Duplicates for {file_path}:")
                for dup in duplicates:
                    print(f" - {dup}")


# Example usage
db_path = 'file_hashes.db'
central_dir_path = '~/tasks'
check_dir_path = './'

process_central_directory(db_path, central_dir_path)
process_check_directory(db_path, check_dir_path)

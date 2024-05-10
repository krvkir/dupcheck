#!/usr/bin/python

import argparse
import os

from dupcheck import (
    setup_database,
    process_central_directory,
    process_file,
    check_directory,
    check_file,
)

# Parse arguments and run appropriate function
def main():
    parser = argparse.ArgumentParser(description='Process directories for file hashing and duplicate checking.')
    parser.add_argument('db_path', help='Path to the SQLite database file.')
    parser.add_argument('dir_path', help='Path to the directory/file to process.')
    parser.add_argument('--mode', choices=['process', 'check'], help='Mode to run: "process" to add to database, "check" to find duplicates.')

    args = parser.parse_args()

    setup_database(args.db_path)

    if args.mode == 'process':
        if os.path.isdir(args.dir_path):
            process_central_directory(
                args.db_path,
                args.dir_path,
            )
        elif os.path.isfile(args.dir_path):
            process_file(
                args.db_path,
                args.dir_path,
            )
        else:
            parser.print_help()
    elif args.mode == 'check':
        if os.path.isdir(args.dir_path):
            check_directory(
                args.db_path,
                args.dir_path,
            )
        elif os.path.isfile(args.dir_path):
            check_file(
                args.db_path,
                args.dir_path,
            )
        else:
            parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

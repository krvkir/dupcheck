import os
from ranger.core.linemode import LinemodeBase
from ranger.api import register_linemode
from ranger.api.commands import Command

from dupcheck import (
    setup_database,
    process_central_directory,
    process_file,
    check_directory,
    check_file,
    check_for_duplicates,
)

@register_linemode
class DuplicatesLinemode(LinemodeBase):
    name = "dupcheck"

    uses_metadata = False

    db_path = os.path.expanduser('~/.config/dupcheck/db.sqlite')

    def __init__(self, *args, **kwargs):
        setup_database(self.db_path)
        super().__init__(*args, **kwargs)

    # def filetitle(self, file, metadata):
    #     return file.relative_path

    # def infostring(self, file, metadata):
    #     return file.user

    def filetitle(self, file, metadata):
        string = "  "
        is_unique = True
        if file.is_directory:
            is_unique = self.has_directory_unique_files(file.path)
        else:
            is_unique = self.is_file_unique(file.path)
        if not is_unique:
            string = '✓ '
        return string + file.relative_path

    def is_file_unique(self, file_path):
        duplicates = check_for_duplicates(self.db_path, file_path)
        if duplicates:
            return False
        return True

    def has_directory_unique_files(self, check_dir_path):
        for root, dirs, files in os.walk(check_dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                is_unique = self.is_file_unique(file_path)
                if is_unique:
                    return True
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                has_unique = self.has_directory_unique_files(dir_path)
                if has_unique:
                    return True
        return False


class duplist(Command):
    """
    :duplist

    Runs a Python script to check the current directory for duplicates.
    """
    db_path = os.path.expanduser('~/.config/dupcheck/db.sqlite')

    def execute(self):
        if self.fm.thisfile.is_directory:
            self.fm.notify(
                "This command does not operate on directories", bad=True)
        else:
            file_path = self.fm.thisfile.path
            self.fm.notify(f"Duplicates for {file_path}:")
            duplicates = check_for_duplicates(self.db_path, file_path)
            if duplicates:
                for duplicate in duplicates:
                    self.fm.notify(f"{duplicate}")
            else:
                self.fm.notify(f"This file is unique.")

    def tab(self, tabnum):
        return self._tab_directory_content()

# DupCheck: Semi-manual File Deduplicator for Personal Archives

DupCheck is a tool for semi-manual file sorting and deduplication.

Existing deduplication tools find duplicates efficiently but the task they solve is too general: to find all the copies of a given file.

But usually the files one needs to sort out are organized in folders, and there are several distinguished folders one wants to keep per files in. E.g. you move from one laptop to another and make a backup of all your homedir, hoping you'll sort out your files later. Or you backup your phone data before flashing. Or you have several old HDDs which contents you partly copied to your current working machine.

So the task is usually the following:

* you have a directory where you want to eventually keep all your files;
* you have several (dozens?) other directories with some files, partially duplicating each other;
* the versions of those files and directories may vary, and you want to pick up the newest one to keep;
* you want to control the process manually but wish to know which files you already saved inside your dedicated place;

Now enters DupCheck:

1. You define a *central directory* (or several ones) where you want to eventually put your files.
2. DupCheck indexes this directory for you.
3. Now for any file on the file system you can check if it is contained inside your central directory.

The utility is integrated with Ranger file manager: you can switch to special modeline which shows for each file, does it exist in central directory or not. For a folder, you can run `dupcheck` command and find out how many non-duplicated files are in it.

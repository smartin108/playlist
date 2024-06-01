"""

Playlist Maker

Creates an m3u playlist in the target folder consisting of all media in that folder and all subfolders.
Also creates playlists in any subfolders using the same MO.

2022 10 09 - First coding

Implementation instructions:
*   create a batch file consisting of the following code and put a shortcut to the batch file in the SendTo folder:
        python "C:/Users/Z40/Documents/Python/Playlist/PythonPlaylist.py" %*
*   enjoy playlist creation on the right-click "Sent To..." menu. Works on multiple folders!

Known issues:
*   failed conversion of unicode is unhandled
*   can't create some playlists possibly because path name is too long?
*   expects folder input only / doesn't adjust for file input (yet)

"""

from os import walk
from os import path
from os import listdir
from sys import exit
from sys import argv
from sys import exc_info
from time import sleep
from collections import namedtuple

folderitem = namedtuple('folderitem', ['root_path', 'relative_path', 'files'])

# files with blacklist extension are excluded from playlists if this is true:
BLACKLIST_ACTIVE = True
blacklist = ['m3u','txt','nfo','jpg','jpeg','png','gif','report','db','doc']


def quit(hold=False):
    if hold:
        input('\nPress Enter to exit...')
    else:
        print('\nSuccess!\n')
        print('\nExiting in a few seconds...')
        sleep(5)
    exit


def extension(filename):
    return filename.split('.')[-1]


def get_folders(root_path):
    """
    Walks the folder structure from root_path
    Returns a list of folder paths (fully qualified) and dictionary of file names (name only)
    """
    folders = []
    files = {}
    for root, dir_names, file_names in walk(root_path):
        folders.append(path.join(root,''))
        files[path.join(root,'')] = file_names
    return folders, files


def get_complete_file_list(folders, files):
    """
    Refactors the folder and file lists and returns a custom data structure consisting of
        the fully qualified root path (for every folder)
        the relative path of every subordinate folder
        the list of files in that subordinate folder
    """
    complete_file_list = []
    for base in folders:
        base_listed = path.join(base,'').split('\\')
        base_len = len(base_listed)
        relative_file_list = []
        for other_folder in folders:
            other_listed = path.join(other_folder,'').split('\\')
            other_len = len(other_listed)
            if base in other_folder:
                relative_file_list.append(folderitem(
                    root_path=base, 
                    relative_path='\\'.join(other_listed[-(other_len-base_len+1):]), 
                    files=files[other_folder]))
        if relative_file_list:
            complete_file_list.append(relative_file_list)
    return complete_file_list


def write_playlist(complete_file_list):
    errors = False
    for i in complete_file_list:
        folder_name = i[0].root_path.split('\\')[-2]  # [-2] because the path terminates with '\'
        playlist_name = i[0].root_path + f'{folder_name}.m3u'
        # print(playlist_name)
        try:
            with open(playlist_name, 'w') as f:
                for j in i:
                    for line in j.files:
                        if extension(line) not in blacklist:
                            # there can be unicode encoding problems here:
                            if j.relative_path and j.relative_path != '\\':
                                # print(f'{j.relative_path} {line}')
                                f.write(f'{j.relative_path}{line}\n')
                            else:
                                f.write(f'{line}\n')
        except FileNotFoundError:
            print(f'\n    >>> could not create playlist {playlist_name}\n')
            errors = True
    return errors


def main():
    errors = False
    print('\nPlaylist Maker')
    if BLACKLIST_ACTIVE:
        print(f'\n    Excluding file extensions {", ".join(sorted(blacklist))}\n')
    try:
        paths = argv[1:]
        paths = [r"\\NAS2021_4TB\music\Bulgarian"]
    except IndexError as e:
        print(f'Syntax: MakePlaylist.py < folder | file >')
        quit()

    for path in paths:
        folders, files = get_folders(path)
        complete_file_list = get_complete_file_list(folders, files)
        print(f'    writing playlists...')
        for i in folders:
            # this bit is deceptive because the entire list of things 
            # the script *should* do is printed, then it actually tries to do the work.
            print(f'        {i}')
        found_errors = write_playlist(complete_file_list)
        if found_errors:
            errors = True
    return errors


if __name__ == '__main__':
    # main()
    try:
        dirty_exit = main()
        if dirty_exit:
            print('\n>>> There were some errors. Scroll up to view.\n')
        quit(hold=dirty_exit)
    except Exception as e:
        _, _, tb = exc_info()
        lineno = tb.tb_lineno
        input('wtf error? (press any key to reveal) ')
        print(f'unhandled exception:\n{e}\n')
        print(f'at line number {lineno}\n')
        print(f'this script was invoked with\n{argv[1:]}\n')
        quit(hold=True)
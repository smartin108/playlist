"""

Playlist Maker

Creates an m3u playlist in the target folder consisting of all media in that folder and all subfolders.
Also creates playlists in any subfolders using the same MO.

2022 10 09 - First coding
2022 11 07 - Small improvements in report out, errors are better visualized
2023 05 05 - v_02 (Cinco De Mayo release) - collect and output a summary of exceptions, if any
2023 11 29 - v_02.02 (29tho D'eleveno) - improve specificity of folder detection, clean up output a bit, enhance instructions

Implementation instructions:
*   create a batch file consisting of the following code and put a shortcut to the batch file in the SendTo folder:
        python "C:/Users/<user>/Documents/Python/Playlist/PythonPlaylist.py" %*

Upgrading Code
*   if you wish to avoid editing the batch file every time you deploy,
    *   save a versioned copy of your code
    *   also save a copy with the name "PythonPlaylist.py" with no versioning
    *   profit

*   enjoy playlist creation on the right-click "Send To..." menu. Works on multiple folders!

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
from sys import stdout
from time import sleep
from collections import namedtuple

class RuntimeExceptions():
    def __init__(self):
        self.d = {}
    def add(self, message):
        try:
            self.d[message] += 1
        except KeyError:
            self.d[message] = 1
    def show(self):
        return self.d


rex = RuntimeExceptions()
folderitem = namedtuple('folderitem', ['root_path', 'relative_path', 'files'])

# files with blacklist extension are excluded from playlists if this is true:
BLACKLIST_ACTIVE = True
blacklist = ['m3u','txt','nfo','jpg','jpeg','png','gif','report','db','doc']


def quit(hold=False):
    if hold:
        input('\nPress Enter to exit...')
    else:
        pause = 5
        print('\nSuccess!\n\n')
        for t in range(pause, 0, -1):
            print(f'\rExiting in {t}... ',end='')
            stdout.flush()
            sleep(1)
    exit()


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


def write_playlist(path, complete_file_list):

    def ascii_encoding(some_path):
        return some_path.encode(encoding='ascii',  errors='namereplace').decode()

    errors = False
    warnings = False
    trunc_path = len(path.split('\\'))
    print(f'    writing playlists...')
    for folder_group in complete_file_list:
        folder_name = folder_group[0].root_path.split('\\')[-2]  # [-2] because the path terminates with '\'
        playlist_name = folder_group[0].root_path + f'{folder_name}.m3u'
        display_name = '\\'.join(playlist_name.split("\\")[trunc_path-1:])
        if len(display_name) > 100:
            display_name = display_name[:98] + '...'
        print(f'        {display_name}')
        try:
            with open(playlist_name, 'w') as f:
                for folder_item in folder_group:
                    for file_name in folder_item.files:
                        if extension(file_name).lower() not in blacklist:
                            try:
                                if folder_item.relative_path and folder_item.relative_path != '\\':
                                    relative_path_to_write = f'{folder_item.relative_path}'
                                    if relative_path_to_write != ascii_encoding(relative_path_to_write):
                                        warnings = True
                                        rex.add('folder contains non-ascii characters')
                                        print(f'            > {folder_item.relative_path}{file_name}')
                                        print(f'            !     folder contains non-ascii characters:')
                                        print(f'            > {ascii_encoding(relative_path_to_write)}\n')
                                    f.write(f'{relative_path_to_write}\n')
                                else:
                                    relative_path_to_write = f'{file_name}'
                                    if relative_path_to_write != ascii_encoding(relative_path_to_write):
                                        warnings = True
                                        rex.add('file contains non-ascii characters')
                                        print(f'            > {file_name}')
                                        print(f'            !     file contains non-ascii characters:')
                                        print(f'            > {ascii_encoding(relative_path_to_write)}\n')
                                    f.write(f'{file_name}\n')
                            except Exception as e:
                                errors = True
                                print(f'            !>> {folder_item.relative_path}{file_name}')
                                print(f'            !>> {e}\n')
        except Exception as e:
            errors = True
            print(f'\n            !>> {e}\n')
    return errors, warnings


def main():
    # errors = False
    print('\nPlaylist Maker')
    if BLACKLIST_ACTIVE:
        print(f'\n    Excluding file extensions {", ".join(sorted(blacklist))}\n')
    try:
        paths = argv[1:]
        # paths = [r"\\NAS2021_4TB\music\Bulgarian"]
        # paths = [r"\\NAS2021_4TB\music\Classical"]
        # paths = [r"\\NAS2021_4TB\music\Bulgarian\Bulgarian Voices Angelite & Huun-Huur-Tu, the"]
    except IndexError as e:
        print(f'Syntax: MakePlaylist.py < folder | file >')
        quit()
    if paths:
        for path in paths:
            folders, files = get_folders(path)
            complete_file_list = get_complete_file_list(folders, files)
            found_errors, found_warnings = write_playlist(path, complete_file_list)
        return found_errors, found_warnings
    else:
        return False, False


if __name__ == '__main__':
    try:
        dirty_exit_errors, dirty_exit_warnings = main()
        if dirty_exit_errors:
            print('\n!>> There were some errors. Scroll up to view.\n')
            print(f'? > Warning summary: {rex.show()}\n')
        elif dirty_exit_warnings:
            print('\n? > There were warnings. Scroll up to view.')
            print(f'? > Warning summary: {rex.show()}\n')
        # quit(hold=True)
        quit(hold=dirty_exit_errors or dirty_exit_warnings)
    except Exception as e:
        _, _, tb = exc_info()
        lineno = tb.tb_lineno
        print('there were errors')
        print(f'unhandled exception:\n{e}\n')
        print(f'at line number {lineno}\n')
        print(f'this script was invoked with\n{argv[1:]}\n')
        quit(hold=True)
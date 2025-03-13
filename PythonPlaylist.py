"""

Playlist Maker

Creates an m3u playlist in the target folder consisting of all media in that folder and all subfolders.
Also creates playlists in any subfolders using the same MO.

"""

import os
from sys import argv
from sys import exc_info
from sys import stdout
from time import sleep
from collections import namedtuple


class RuntimeExceptions():
    def __init__(self):
        self.p = set()
    def add_path(self, path):
        self.p.add(path)
    def show_path(self):
        return self.p
    def __str__(self):
        return str(self.p)


folderitem = namedtuple('folderitem', ['root_path', 'relative_path', 'files'])
rex = RuntimeExceptions()



def blacklist():
    return ['m3u','txt','nfo','jpg','jpeg','png','gif','report','db','doc']


def BLACKLIST_ACTIVE():
    # files with blacklist extension are excluded from playlists if this is true:
    return True


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
    # folders = []
    files = {}
    for root, dir_names, file_names in os.walk(root_path):
        # folders.append(os.path.join(root,''))
        key = os.path.join(root,'')
        files[key] = file_names
        # print(folders)
        # print(files)
        _ = input('press...')
    return files
    # return folders, files


def end_path(full_path:str, depth:int=1, separator='\\'):
    """
    Return the rightmost segment(s) of a file path
    """

    depth += 1
    split_path = full_path.split(separator)
    return separator.join(split_path[-1*depth:])


def get_complete_file_list(files):
# def get_complete_file_list(folders, files):
    """
    Refactors the folder and file lists and returns a custom data structure consisting of
        the fully qualified root path (for every folder)
        the relative path of every subordinate folder
        the list of files in that subordinate folder
    """
    complete_file_list = []
    for base in files.keys():
    # for base in folders:
        base_listed = os.path.join(base,'').split('\\')
        base_len = len(base_listed)
        relative_file_list = []
        for other_folder in files.keys():
        # for other_folder in folders:
            other_listed = os.path.join(other_folder,'').split('\\')
            other_len = len(other_listed)
            if base in other_folder:
                relative_file_list.append(folderitem(
                    root_path=base, 
                    relative_path='\\'.join(other_listed[-(other_len-base_len+1):]), 
                    files=files[other_folder]))
        if relative_file_list:
            complete_file_list.append(relative_file_list)
    return complete_file_list


def write_playlist(playlist_path, complete_file_list):


    def ascii_encoding(some_path):
        return some_path.encode(encoding='ascii',  errors='namereplace').decode()


    def do_file_rules(folder_item, file_name, f):
        try:
            if file_name != ascii_encoding(file_name):
                warnings = True
                rex.add_path(f'{folder_item.root_path}{folder_item.relative_path}{file_name}\n')
            f.write(f'{file_name}\n')
        except Exception as e:
            errors = True
            rex.add_path(f'{folder_item.root_path}{folder_item.relative_path}{file_name}\n')
            rec.add_path(f'{e}')
            raise


    def do_write_playlist(folder_group, playlist_name):
        try:
            with open(playlist_name, 'w') as f:
                for folder_item in folder_group:
                    for file_name in folder_item.files:
                        do_file_rules(folder_item, file_name, f)
        except Exception as e:
            errors = True
            rex.add_path(f'{e}\n')
            # print(f'\n            !>> {e}\n')


    def do_folder_loop(folder_group):
        folder_name = folder_group[0].root_path.split('\\')[-2]  # [-2] because the path terminates with '\'
        playlist_name = folder_group[0].root_path + f'{folder_name}.m3u'
        print(folder_group)
        print(folder_name)
        print(playlist_name)
        # print(display_name)
        exit()
        # display_name = '\\'.join(playlist_name.split("\\")[trunc_path-1:])
        if len(display_name) > 100:
            display_name = display_name[:97] + '...'
        print(f'{display_name}')
        do_write_playlist(folder_group, playlist_name)



    errors = False
    warnings = False
    # trunc_path = len(playlist_path.split('\\'))
    print(f'\nWriting playlists...')
    for folder_group in complete_file_list:
        do_folder_loop(folder_group)
    return errors, warnings


def main():
    print('\nPlaylist Maker')
    if BLACKLIST_ACTIVE():
        print(f'\nExcluding file extensions {", ".join(sorted(blacklist()))}\n')
    try:
        paths_args = argv[1:]
        # paths = [r"\\NAS2021_4TB\music\Bulgarian"]
        # paths = [r"\\NAS2021_4TB\music\Classical"]
        # paths = [r"\\NAS2021_4TB\music\Wilco"]
        # paths = [r"\\NAS2021_4TB\music\Bulgarian\Bulgarian Voices Angelite & Huun-Huur-Tu, the"]
    except IndexError as e:
        print(f'Syntax: MakePlaylist.py <folder|file>')
        quit()
    if paths_args:
        for path_arg in paths_args:
            files = get_folders(path_arg)
            # folders, files = get_folders(path_arg)
            complete_file_list = get_complete_file_list(files)
            # complete_file_list = get_complete_file_list(folders, files)
            found_errors, found_warnings = write_playlist(path_arg, complete_file_list)
        return found_errors, found_warnings
    else:
        return False, False


if __name__ == '__main__':
    dirty_exit_errors, dirty_exit_warnings = main()
    print()
    print(rex)
    if dirty_exit_errors:
        print('\n!>> There were some errors. Scroll up to view.\n')
        print(f'? > Warning summary: {rex.show()}\n')
    elif dirty_exit_warnings:
        print('\n? > There were warnings. Scroll up to view.')
        print(f'? > Warning summary: {rex.show()}\n')
    quit(hold=dirty_exit_errors or dirty_exit_warnings)

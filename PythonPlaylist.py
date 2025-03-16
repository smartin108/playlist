"""

Playlist Maker

Creates an m3u playlist in the target folder consisting of all media in that folder and all subfolders.
Also creates playlists in any subfolders using the same MO.

"""

import os
from sys import argv
# from sys import exc_info
from sys import stdout
import re
from time import sleep
from collections import namedtuple
import pprint


class RuntimeExceptions():


    def __init__(self):
        self.p = {}
        self.f = {}
        self.errors = False
        self.warnings = False


    def add_path(self, user_path, path_depth, positions, descriptions, is_folder=False):
        if is_folder:
            print(f'is_folder: {user_path}\n{path_depth}\n{positions}\n{descriptions}')
        else:
            self.p[user_path] = [path_depth, positions, descriptions]


    def __str__(self):
        """
        Format the exceptions nicely
        """
        tmp = ''
        old_header = ''
        for k, v in self.p.items():

            """
            <header> is dirpath rooted at the folder where the script was
            invoked
            """
            header, fileref = os.path.split(k)
            if header != old_header:
                tmp += f'\n{header}\n'
                old_header = header

            """
            Each filename is indented under its dirpath
            """
            tmp += f'    {fileref}\n'

            """
            Now we mark the positions of the errant characters
            """
            positions = v[1]
            descriptions = v[2]
            if positions:
                tmpline = ''
                for i in range(len(positions)):
                    tmpline += f'{" "*(positions[i]-1)}{str(i+1)}'
                tmp += f'     {tmpline}\n'

            """
            Finally, list the unicode character names that were discovered
            """
            if descriptions:
                for i in range(len(descriptions)):
                    tmp += f'        {i+1} > {descriptions[i]}\n'

            tmp += '\n'
        return tmp


class FileNameParser():


    def __init__(self, full_path, invocation_depth):
        self.full_path = full_path.replace('\\','/')
        self.path_as_list = self.full_path.split('/')
        self.segments = len(self.path_as_list)
        self.invocation_depth = invocation_depth
        self.full_directory = '/'.join(self.path_as_list[:self.segments-2])
        self.current_directoy = self.full_directory[-1]
        self.stem, self.suffix = os.path.split(self.full_path)


    def __repr__(self):
        return path_item(\
            self.full_path,
            self.path_as_list,
            self.segments,
            self.invocation_depth,
            self.full_directory,
            self.current_directoy,
            self.stem,
            self.suffix
            )


folderitem = namedtuple('folderitem', ['root_path', 'relative_path', 'files'])
path_item = namedtuple('path_item', [
    'full_path', 
    'path_as_list', 
    'invocation_depth', 
    'full_directory',
    'current_directory', 
    'stem',
    'suffix'
    ])
rex = RuntimeExceptions()


def blacklist():
    return ['.m3u','.txt','.nfo','.jpg','.jpeg','.png','.gif','.report','.db','.doc']


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


def get_folders(root_path):
    """
    Walks the folder structure from root_path
    Returns a dictionary of file names keyed on the path
    """
    files = {}
    duds = {}
    for root, dir_names, file_names in os.walk(root_path):
        key = os.path.join(root,'')
        if BLACKLIST_ACTIVE():
            files[key] = list(f for f in file_names if os.path.splitext(f)[1] not in blacklist())
        else:
            files[key] = list(f for f in file_names)
    return files


def get_complete_file_list(files):
    """
    Refactors the folder and file lists and returns a custom data structure consisting of
        the fully qualified root path (for every folder)
        the relative path of every subordinate folder
        the list of files in that subordinate folder
    """
    complete_file_list = []
    for base in files.keys():
        base_as_list = os.path.join(base,'').split('\\')
        base_len = len(base_as_list)
        relative_file_list = []
        for other_folder in files.keys():
            other_as_list = os.path.join(other_folder,'').split('\\')
            other_len = len(other_as_list)
            if base in other_folder:
                relative_file_list.append(folderitem(
                    root_path=base, 
                    relative_path='\\'.join(other_as_list[-(other_len-base_len+1):]), 
                    files=files[other_folder]))
        if relative_file_list:
            complete_file_list.append(relative_file_list)
    return complete_file_list


def locate_non_ascii(ascii_ified_text, original_text=None):
    """
    If <ascii_ified_text> contains the results of 
        original_text.encode(errors='namereplace')   ,
    then this will return the replacement text and their character locations 
    with respect to <original_text>

    It's not necessary to provide <original_text>
    """
    pattern = r"[\\][N](\{.*?\})"
    matches = re.finditer(pattern, ascii_ified_text)
    positions = []
    descriptions = []
    prior_end = 0

    # <match> is the verbose description of a non-ascii character

    for match in matches:
        descriptions.append(match.group(1))
        if positions:
            """
            <positions> includes the space taken up by the replacement 
            text, so we subtract out the accumlated lengths of the 
            replacement text in order to know the positions of the 
            non-ascii characters in <original_text>
            """
            width = match.end() - match.start()
            positions.append(match.start() - prior_end + 1)
            prior_end = match.end()
        else:
            positions.append(match.start())
            prior_end = match.end()
    return positions, descriptions


def ascii_encoding(some_path):
    positions = None
    descriptions = None
    ascii_value = some_path.encode(encoding='ascii', errors='namereplace').decode()
    if ascii_value != some_path:
        positions, descriptions = locate_non_ascii(ascii_value)
        # print('0         1         2         3         4         5         6         7         8         9         0         1         2')
        # print('0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890')
        # print(some_path)
        # print(positions)
        # print(descriptions)
        # print()
    return ascii_value, positions, descriptions


def do_filename_rules(folder_item, path_depth, file_name, is_folder=False):
    ascii_name, positions, descriptions = ascii_encoding(file_name)
    if file_name != ascii_name:
        print(f'ascii fail: is_folder={is_folder} {file_name}')
        rex.warnings = True
        display_name = '\\'.join(os.path.join(folder_item.root_path,folder_item.relative_path,file_name).split('\\')[path_depth-1:])
        rex.add_path(display_name, path_depth, positions, descriptions, is_folder)
        # if is_folder:
        #     print()
        #     print(file_name)
        #     print(ascii_name)
        #     print(display_name)
        #     print(positions)
        #     print(descriptions)
        #     _ = input('press...')


def do_write_playlist(folder_group, path_depth, playlist_name):
    with open(playlist_name, 'w', encoding='utf-8') as f:
        for folder_item in folder_group:
            folder_depth = len(playlist_name.split("\\"))
            do_filename_rules(folder_item, path_depth, folder_item.root_path, is_folder=True)
            for file_name in folder_item.files:
                do_filename_rules(folder_item, path_depth, file_name)
                f.write(f'{file_name}\n')


def do_folder_loop(folder_group, path_depth):
    path_as_list = folder_group[0].root_path.split('\\') 
    folder_name = path_as_list[-2]
    playlist_name = os.path.join(folder_group[0].root_path, folder_name) + '.m3u'
    display_name = '\\'.join(playlist_name.split('\\')[path_depth-1:])
    if len(display_name) > 100:
        display_name = display_name[:87] + '...' + display_name[-10:]
    print(f'{display_name}')
    do_write_playlist(folder_group, path_depth, playlist_name)


def write_playlist(playlist_path, complete_file_list):
    path_depth = len(playlist_path.split('\\'))
    print(f'\nWriting playlists...')
    for folder_group in complete_file_list:
        do_folder_loop(folder_group, path_depth)


def main():
    print('\nPlaylist Maker')
    if BLACKLIST_ACTIVE():
        print(f'\nExcluding file extensions {", ".join(sorted(blacklist()))}')
    try:
        paths_args = argv[1:]
        # paths_args = [r"\\NAS2021_4TB\music\Bulgarian"]
        # paths_args = [r"\\NAS2021_4TB\music\Classical"]
        # paths_args = [r"\\NAS2021_4TB\music\Classical\Giacomo Puccini"]
        # paths_args = [r"\\NAS2021_4TB\music\Wilco"]
        # paths_args = [r"\\NAS2021_4TB\music\Bulgarian\Bulgarian Voices Angelite & Huun-Huur-Tu, the"]
    except IndexError as e:
        print(f'Syntax: MakePlaylist.py <folder|file>')
        quit()
    for path_arg in paths_args:
        files = get_folders(path_arg)
        pprint.pp(files, width=180)
        _ = input('press...')
        complete_file_list = get_complete_file_list(files)
        pprint.pp(complete_file_list, width=180)
        _ = input('press...')
        write_playlist(path_arg, complete_file_list)


if __name__ == '__main__':
    main()
    print()
    print(rex)
    quit(hold=rex.errors or rex.warnings)

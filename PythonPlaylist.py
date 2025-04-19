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
from clsPathParser import PathParser


class RuntimeExceptions():


    def __init__(self):
        self.p = {}
        self.f = {}
        self.errors = False
        self.warnings = False


    def add_path(self, user_path, path_depth, positions, descriptions, is_folder=False):
        if is_folder:
            self.p[user_path] = [path_depth, positions, descriptions]
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


folderitem = namedtuple('folderitem', ['root_path', 'relative_path', 'files'])
rex = RuntimeExceptions()


def blacklist():
    return ['.m3u','.txt','.nfo','.jpg','.jpeg','.png','.gif','.report','.db','.doc']


def BLACKLIST_ACTIVE():
    # files with blacklist extension are excluded from playlists if this is true:
    return True


def pause():
    _ = input('(paused)  ')


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


def locate_non_ascii(ascii_ified_text, original_text=None):
    """
    If <ascii_ified_text> contains the results of 
        original_text.encode(errors='namereplace')   ,
    then this will return the replacement text and their character locations 
    with respect to <original_text>

    It's not necessary to provide <original_text>
    """

    # <pattern> matches \N{VERBOSE DESCRIPTION OF NON-ASCII CHARACTER}
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


def ascii_rule(path_to_test):


    def ascii_test(user_string:str):
        return user_string.encode(encoding='ascii', errors='namereplace').decode()


    positions = None
    descriptions = None
    ascii_value = ascii_test(path_to_test)
    if ascii_value != path_to_test:
        positions, descriptions = locate_non_ascii(ascii_value)
    return ascii_value, positions, descriptions


def do_name_rules(user_path:PathParser):
    print(f'\n>>> user_path: {user_path}')
    if user_path.isdir:
        print(f'>>> user_path.isdir: {user_path.isdir}')
        ascii_name, positions, descriptions = ascii_rule(user_path.current_directory)
    else:
        print(f'>>> basename: {user_path.basename}')
        ascii_name, positions, descriptions = ascii_rule(user_path.basename)
        # ascii_name, positions, descriptions = ascii_rule(user_path.path_from_level(-1))
    if user_path.basename != ascii_name:
        rex.warnings = True
        print(f'failed ascii test: {user_path.basename} --> {ascii_name}')
        rex.add_path(user_path.displayname, user_path.invocation_depth, positions, descriptions, user_path.isdir)


def do_write_playlist(folder_group, path_depth, playlist_name):
    with open(playlist_name, 'w', encoding='utf-8') as f:
        for folder_item in folder_group:
            pobj = PathParser(folder_item.root_path, path_depth)
            do_name_rules(pobj)
            # do_name_rules(folder_item, path_depth, folder_item.root_path, is_folder=True)
            for file_name in folder_item.files:
                # print(f'>>> {pobj}')
                # print(f'>>> {folder_item.files}')
                # print(f'>>> {file_name}, {path_depth}')
                fileobj = PathParser(file_name, path_depth)
                do_name_rules(fileobj)
                if folder_item.relative_path and folder_item.relative_path != '\\':
                    relative_path_to_write = os.path.join(folder_item.relative_path, file_name)
                    f.write(f'{relative_path_to_write}\n')
                else:
                    relative_path_to_write = f'{file_name}'
                    f.write(f'{file_name}\n')


def do_folder_loop(folder_group, path_depth):
    pobj = PathParser(folder_group[0].root_path, path_depth)
    # print(pobj)

    path_as_list = folder_group[0].root_path.split('\\') 
    # print(path_as_list)

    folder_name = path_as_list[-2]
    # print(folder_name)

    playlist_name = os.path.join(folder_group[0].root_path, folder_name) + '.m3u'
    # print(playlist_name)

    # pause()
    
    display_name = pobj.path_from_level(path_depth)
    if len(display_name) > 100:
        display_name = display_name[:87] + '...' + display_name[-10:]
    print(f'{display_name}')
    do_write_playlist(folder_group, path_depth, playlist_name)


def write_playlist(playlist_root_path, list_of_folder_items):

    pobj = PathParser(playlist_root_path)

    """
    path_depth will be the index into (full path as list) where the 
    script was invoked
    """
    path_depth = pobj.segments - 1

    print(f'\nWriting playlists for {pobj.current_directory}')
    for folder_item in list_of_folder_items:
        do_folder_loop(folder_item, path_depth)
    print(f'\nDone writing playlists')


def get_complete_file_list(files):
    """
    Refactors the folder and file lists and returns a custom data structure 
    consisting of the fully qualified root path (for every folder) the 
    relative path of every subordinate folder the list of files in that 
    subordinate folder
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


def get_folders(root_path):
    """
    Walks the folder structure from root_path
    Returns a dictionary of file names keyed on the path
    """
    files = {}
    for root, dir_names, file_names in os.walk(root_path):
        key = os.path.join(root,'')
        if BLACKLIST_ACTIVE():
            files[key] = list(\
                f for f in file_names \
                if os.path.splitext(f)[1] not in blacklist())
        else:
            files[key] = list(f for f in file_names)
    return files


def main():
    print('\nPlaylist Maker')
    if BLACKLIST_ACTIVE():
        print(f'\nExcluding file extensions {", ".join(sorted(blacklist()))}')
    try:
        # paths_args = argv[1:]
        paths_args = [r"\\NAS2021_4TB\music\She & Him\Volume Two"]
        # paths_args = [r"\\NAS2021_4TB\music\10cc",r"\\NAS2021_4TB\music\A Killer’s Confession"]
        # paths_args = [r"\\NAS2021_4TB\music\Bulgarian"]   
        # paths_args = [r"\\NAS2021_4TB\music\Bulgarian\Bulgarian Voices Angelite & Huun-Huur-Tu, the"]
        # paths_args = [r"\\NAS2021_4TB\music\Classical"]
        # paths_args = [r"\\NAS2021_4TB\music\Classical\Giacomo Puccini"]
        # paths_args = [r"\\NAS2021_4TB\music\Wilco"]
    except IndexError as e:
        print(f'Syntax: MakePlaylist.py <folder|file>')
        quit()
    for path_arg in paths_args:
        files = get_folders(path_arg)
        complete_file_list = get_complete_file_list(files)
        write_playlist(path_arg, complete_file_list)
        print(rex)
    quit(hold=rex.errors or rex.warnings)


if __name__ == '__main__':
    main()

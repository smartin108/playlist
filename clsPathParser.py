from collections import namedtuple
from os import path

class PathParser():

    def __init__(self, full_path, invocation_depth=0):
        self.full_path = full_path.replace('\\','/')
        self.path_as_list = self.full_path.split('/')
        self.segments = len(self.path_as_list)
        self.invocation_depth = invocation_depth
        self.displayname = path.join(self.path_from_level(self.invocation_depth))
        self.basename = path.basename(self.full_path)
        # print(f'>>> {self.full_path}')
        if self.isdir():
            self.current_directory = self.path_as_list[-1]
            self.root, self.ext = '', ''
        elif self.segments > 1:
            self.current_directory = self.path_as_list[-2]
            self.root, self.ext = path.splitext(self.basename)
        else:
            self.current_directory = ''
            self.root, self.ext = path.splitext(self.basename)


    def path_from_level(self, level:int):
        if level == self.invocation_depth:
            return self.path_as_list[-1]
        else:
            return path.join(*self.path_as_list[level:])


    def path_to_level(self, level:int):
        return path.join(*self.path_as_list[:level])


    def isdir(self):
        return path.isdir(self.full_path)


    def isfile(self):
        return path.isfile(self.full_path)


    def __repr__(self):
        return path_item(\
            path.join(*self.path_as_list),
            self.isdir(),
            self.isfile(),
            self.path_as_list,
            self.segments,
            self.invocation_depth,
            self.displayname,
            self.current_directory,
            self.basename,
            self.ext
            )


    def __str__(self):
        return str(path_item(\
            path.join(*self.path_as_list),
            self.isdir(),
            self.isfile(),
            self.path_as_list,
            self.segments,
            self.invocation_depth,
            self.displayname,
            self.current_directory,
            self.basename,
            self.ext
            ))


path_item = namedtuple('path_item', [
    'full_path', 
    'isdir',
    'isfile',
    'path_as_list', 
    'segments',
    'invocation_depth', 
    'displayname',
    'current_directory', 
    'basename',
    'ext'
    ])
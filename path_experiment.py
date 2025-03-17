import os
from clsPathParser import PathParser

mypath = r"\\NAS2021_4TB\music\Bulgarian"
lenmypath = len(mypath.split('\\'))
invoke_point = lenmypath - 1


pobjs = []
for r, d, f in os.walk(mypath):
    print(f'{r}\n  {d}\n    {f}\n')
    if len(d) == 0:
        for fns in f:
            pobj = PathParser(os.path.join(r, fns), invoke_point)
            pobjs.append(pobj)
            print(pobj)
    else:
        pobj = PathParser(os.path.join(r), invoke_point)
        pobjs.append(pobj)
        print(pobj)
    print()

"""
the updated PathParser class is ready to use in the playlist maker

* you can ALWAYS reference the .displayname property for on-screen display (except you still have to shorten very long names)

* you can ALWAYS test the .basename property for ascii compliance

* len(.displayname) - len(.basename) should provide the padding you want to mark ascii conversion offenders on-screen

* your thought was to deploy lists of path_item objects as early as possible in the 
workflow, replacing the complicated folderitem objects wherever possible

"""
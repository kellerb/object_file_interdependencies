from __future__ import print_function

import json
import subprocess
import sys

class ObjectFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.requires, self.provides = get_requires_and_provides(self.filename)

    def __eq__(self, other):
        return self.filename == other.filename

    def __hash__(self):
        return hash(self.filename)

def get_requires_and_provides(filename):
    '''Brittle parsing of "nm -CD filename" to return (set(undefined symbols), set(defined symbols))'''
    nm_output = subprocess.check_output(['nm', '-CD', filename])
    provides_symbol_types = {'A', 'B', 'b', 'D', 'd', 'G', 'g', 'S', 's', 'T', 't'}
    provides = set()
    requires = set()
    for l in nm_output.splitlines():
        if l[17] in provides_symbol_types:
            provides.add(l[19:])
        elif l[17] == 'U':
            requires.add(l[19:])
    return requires, provides

def get_interdependency_dictionary(object_file_set):
    '''Returns dict of object file filename -> depended-on object file filename -> list of symbols'''
    d = {}
    for o in object_file_set:
        d[o.filename] = {}
        for o_other in object_file_set - set([o]):
            deps = []
            for requires in o.requires:
                if requires in o_other.provides:
                    deps.append(requires)
            if deps:
                d[o.filename][o_other.filename] = sorted(deps)
    return d

def main():
    if len(sys.argv) < 3:
        print('Call as: "{} <object_file_0> <object_file_1> [<object_file_2 ...]"'.format(sys.argv[0]))
        sys.exit(1)

    object_files = {ObjectFile(f) for f in sys.argv[1:]}
    print(json.dumps(get_interdependency_dictionary(object_files), sort_keys=True, indent=4))

if __name__ == '__main__':
    main()

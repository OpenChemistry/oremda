#!/usr/bin/env python3


def dict_to_docker_labels(d, delimiter='.'):

    path = ''
    labels = {}

    def recurse(cur):
        nonlocal path
        parent = path
        for key, value in cur.items():
            path = delimiter.join([parent, key]) if parent else key
            if isinstance(value, dict):
                recurse(value)
            else:
                labels[path] = str(value)

        path = parent

    recurse(d)
    return labels


if __name__ == '__main__':

    import json
    import sys

    if len(sys.argv) < 2:
        sys.exit('usage: <script> <json_file>')

    with open(sys.argv[1], 'r') as rf:
        d = json.load(rf)

    labels = dict_to_docker_labels(d)

    for key, value in labels.items():
        print(f'LABEL {key}={value}')

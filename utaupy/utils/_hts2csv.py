#! /usr/bin/env python3
# Copyright (c) 2020-2021 oatsu
"""
HTS-Full-Context-Label をCSVに変換してExcelで見るようにする。
"""
import re


def hts2csv(path_in, path_out):
    with open(path_in, mode='r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]

    keys = []
    keys.append('start')
    keys.append('end')
    keys.append(','.join([f'p{i+1}' for i in range(16)]))
    keys.append(','.join([f'a{i+1}' for i in range(5)]))
    keys.append(','.join([f'b{i+1}' for i in range(5)]))
    keys.append(','.join([f'c{i+1}' for i in range(5)]))
    keys.append(','.join([f'd{i+1}' for i in range(9)]))
    keys.append(','.join([f'e{i+1}' for i in range(60)]))
    keys.append(','.join([f'f{i+1}' for i in range(9)]))
    keys.append(','.join([f'g{i+1}' for i in range(2)]))
    keys.append(','.join([f'h{i+1}' for i in range(2)]))
    keys.append(','.join([f'i{i+1}' for i in range(2)]))
    keys.append(','.join([f'j{i+1}' for i in range(3)]))

    l = []
    l.append([','.join(keys)])

    for line in lines:
        line = re.sub('/.:', '@', line)
        line = re.split(f"[{re.escape(' =+-~!@#$%^&;_|[]')}]", line)
        l.append(line)
    l_of_str = [','.join(v) for v in l]
    s_out = '\n'.join(l_of_str)
    with open(path_out, mode='w', encoding='utf-8') as f:
        f.write(s_out)


def main():
    """
    フォルダかファイルを選択して変換
    """
    from glob import glob
    from os.path import isfile, join, splitext

    lab_dir = input('Select a directory or a LAB file: ').strip('"')
    lab_files = [lab_dir] if isfile(lab_dir) else glob(join(lab_dir, '*.lab'))

    for path_in in lab_files:
        path_out = f'{splitext(path_in)[0]}.csv'
        try:
            hts2csv(path_in, path_out)
        except Exception as e:
            raise Exception(f'Some exception was raised while processing {path_in}') from e


if __name__ == '__main__':
    main()

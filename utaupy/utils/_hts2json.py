#! /usr/bin/env python3
# Copyright (c) 2020-2021 oatsu
"""
HTSフルコンテキストラベルをJSONと相互変換する。
"""

import re


def _load_hts_lines(lines: list) -> dict:
    """
    文字列のリスト(行のリスト)をもとに値を登録する。
    """
    # ラベル情報のリスト
    labels = []
    # HTSフルコンテキストラベルの各行を読み取っていく
    for line in lines:
        line_split = line.split(maxsplit=2)
        # 1行分の辞書
        d_line = {}
        # 時刻の情報 [発声開始時刻, 発声終了時刻]
        d_line['time'] = list(map(int, line_split[0:2]))
        # コンテキスト部分を取り出す
        str_contexts = line_split[2]
        # コンテキスト文字列を /A: などの文字列で区切って一次元リストにする
        l_contexts = re.split('/.:', str_contexts)
        # 特定の文字でさらに区切って二次元リストにする
        delimiters = re.escape('=+-~∼!@#$%^ˆ&;_|[]')
        l_contexts_2d = [re.split((f'[{delimiters}]'), s) for s in l_contexts]
        # 各種コンテキストを辞書に登録する
        d_line.update(dict(
            zip(('p', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'), l_contexts_2d)))
        # ここからzipのもとのコード----------------------
        # d_line['p'] = l_contexts_2d[0]
        # d_line['a'] = l_contexts_2d[1]
        # d_line['b'] = l_contexts_2d[2]
        # d_line['c'] = l_contexts_2d[3]
        # d_line['d'] = l_contexts_2d[4]
        # d_line['e'] = l_contexts_2d[5]
        # d_line['f'] = l_contexts_2d[6]
        # d_line['g'] = l_contexts_2d[7]
        # d_line['h'] = l_contexts_2d[8]
        # d_line['i'] = l_contexts_2d[9]
        # d_line['j'] = l_contexts_2d[10]
        # ここまでzipのもとのコード----------------------

        # ラベル情報のリストに追加
        labels.append(d_line)
    return {'labels': labels}


def _load(path: str, encoding='utf-8') -> dict:
    """
    HTSフルコンテキストラベル(Sinsy用)のファイルを読み取り、辞書にする。
    """
    # ファイルを読み取って行のリストにする
    try:
        with open(path, mode='r', encoding=encoding) as f:
            lines = [line.rstrip('\r\n') for line in f.readlines()]
    except UnicodeDecodeError:
        with open(path, mode='r', encoding='cp932') as f:
            lines = [line.rstrip('\r\n') for line in f.readlines()]
    return _load_hts_lines(lines)


def _export_flatjson(d: dict, path) -> str:
    """
    JSON文字列でファイル出力する。
    1音素1行
    """
    s = ',\n'.join([f'        {str(d_line)}' for d_line in d['labels']])
    s = s.replace('\'', '"').replace('{', '{ ').replace('}', ' }')
    s = '{\n    \"labels\": [\n' + s + '\n    ]\n}\n'
    with open(path, mode='w', encoding='utf-8', newline='\n') as f:
        f.write(s)
    return s


def hts2json(path_lab_in, path_json_out):
    """
    HTSフルコンテキストラベルファイル(.lab) を
    JSONファイル(.json) に変換する。
    """
    _export_flatjson(_load(path_lab_in), path_json_out)


def main():
    """
    直接起動したときの動作。
    1つのラベルファイルをJSONに変換する。
    """
    from glob import glob
    from os.path import isfile, join, splitext

    lab_dir = input('Select a directory or a LAB file: ').strip('"')
    lab_files = [lab_dir] if isfile(lab_dir) else glob(join(lab_dir, '*.lab'))

    for path_in in lab_files:
        path_out = f'{splitext(path_in)[0]}.json'
        try:
            hts2json(path_in, path_out)
        except Exception as e:
            raise Exception(f'Some exception was raised while processing {path_in}') from e


if __name__ == '__main__':
    main()

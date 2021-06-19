#! /usr/bin/env python3
# coding: utf-8
"""
日本語とアルファベットの対応表を扱うモジュールです。
"""


def main():
    """呼び出されても特に何もしない"""
    print('平仮名とアルファベットの対応表を扱うモジュールです。')


def load(path, encoding='utf-8') -> dict:
    """テーブルを読み取ってインスタンス生成"""
    path = str(path).strip('\'"')
    if path.endswith('.table'):
        return load_table_file(path, encoding=encoding)
    if path.endswith('.conf'):
        return load_conf_file(path, encoding=encoding)
    raise ValueError(f'Input path must end with ".table" or ".conf".: {path}')


def load_table_file(path_table, encoding='utf-8') -> dict:
    """テーブルを読み取ってインスタンス生成"""
    # ファイル読み取り
    try:
        with open(path_table, mode='r', encoding=encoding) as f:
            lines = [line.strip() for line in f.readlines()]
    except UnicodeDecodeError:
        try:
            with open(path_table, mode='r', encoding='cp932') as f:
                lines = [line.strip() for line in f.readlines()]
        except UnicodeDecodeError:
            with open(path_table, mode='r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]
    # 辞書にする
    d_table = {}
    for line in lines:
        line_split = line.split()
        d_table[line_split[0]] = line_split[1:]
    return d_table


def load_conf_file(path_conf, encoding='utf-8') -> dict:
    """音素分類用のファイルを読み取って辞書を返す"""
    # ファイル読み取り
    try:
        with open(path_conf, mode='r', encoding=encoding) as f:
            lines = [line.strip() for line in f.readlines()]
    except UnicodeDecodeError:
        try:
            with open(path_conf, mode='r', encoding='cp932') as f:
                lines = [line.strip() for line in f.readlines()]
        except UnicodeDecodeError:
            with open(path_conf, mode='r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]
    # 辞書にする
    d_conf = {'SILENCES': ['sil'], 'PAUSES': ['pau'], 'BREAKS': ['br']}
    for line in lines:
        key, value = line.split('=', 1)
        phonemes = value.strip('"').split(',')
        d_conf[key] = phonemes
    if 'PHONEME_CL' in d_conf:
        d_conf['BREAKS'] += d_conf['PHONEME_CL']

    return d_conf


if __name__ == '__main__':
    main()

#!python3
# coding: utf-8
"""
SHIRO (https://github.com/Sleepwalking/SHIRO) 関連のファイルを扱う。
"""

import re


def load_index(path, mode='r', encoding='shift-jis'):
    """index fileを読み取ってIndexを返す"""
    # labファイル読み取り
    with open(path, mode=mode, encoding=encoding) as f:
        lines = [re.split(', ') for s in f.readlines()]
    idx = Index()
    idx.values = lines
    return idx


class Index:
    """
    wavに含まれる音素一覧を提示する 'index file' を扱うクラス。
        音声ファイル名1,音素1-1 音素1-2 音素1-3 音素1-4 ...
        音声ファイル名2,音素2-1 音素2-2 音素3-3 音素4-4 ...
        ...
    ってフォーマットのファイル。
    """

    def __init__(self):
        """二次元リスト [[開始時刻, 音素, 音素, 音素, ...], [], ...]"""
        self.__values = []

    def write(self, path, mode='w', encoding='shift-jis', newline='\n'):
        """indexfile(CSV)を保存"""
        l = self.values
        s = ''
        for v in l:
            s += '{},{}\n'.format(v[0], ' '.join(v[1:]))
        # ファイル出力
        with open(path, mode=mode, encoding=encoding, newline=newline) as f:
            f.write(s)
        return s

    @property
    def values(self):
        """値を取得"""
        return self.__values

    @values.setter
    def values(self, lines):
        """値を登録"""
        if not isinstance(lines, list):
            raise TypeError('\"lines\" must be list instance (values.setter in label.py)')
        self.__values = lines

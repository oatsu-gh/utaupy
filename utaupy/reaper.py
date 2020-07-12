#!python3
# coding: utf-8
# Copyright (c) oatsu
"""
REAPERのリージョンCSVを扱うモジュールです。
BOMなしUTF-8じゃないとREAPERは読み込んでくれません。
REAPER v5, v6 で動作確認

各行は "連番タグ,名前,開始時刻,終了時刻,長さ" になってる。
時刻は x.y.zz (小節.拍.割合(4/4拍子の時は8分音符:50, 16分音符:25))

時刻の zz は 4/4, 4/4 拍子の時は  8分音符:50 16分音符:25 の表記
                  6/8 拍子の時は 16分音符:50 32分音符:25 の表記

[例]---------------------------------------
  R1,_ああんいあう,5.1.00,9.1.00,4.0.00
  R2,_いいんういえ,9.1.00,13.1.00,4.0.00
-------------------------------------------

"""

import csv
from pprint import pprint


def main():
    print('---REAPERのリージョンCSVを扱うモジュールです。importして使ってね。---')
    print('CSV読み取りテストをします。')
    path = input('CSVのパスを入力してください。\n>>> ')
    l = load(path)
    print()
    pprint(l)


def load(path, mode='r', encoding='utf-8'):
    """
    REAPERのリージョンCSVを読み取る。
    """
    # 文字コードの候補
    choices = ['utf-8', 'shift-jis']
    if encoding in choices:
        choices.remove(encoding)
    # 指定された文字コードで読み取ろうとする
    try:
        with open(path, mode=mode, encoding=encoding) as f:
            reader = csv.reader(f)
            l = [row for row in reader]
    # 上手くいかなかったらもう片方の文字コードで読み取る
    except UnicodeDecodeError as e:
        print('[WARN]', e)
        print('[INFO] 文字コードを {} に変更して読み取ります。'.format(choices[0]))
        with open(path, mode=mode, encoding=choices[0]) as f:
            reader = csv.reader(f)
            l = [row for row in csv.reader(f)]
    return l[1:]


class Region:
    """REAPERのリージョンCSV用のクラス"""

    def __init__(self):
        self.__values = []

    @property
    def values(self):
        """値を確認"""
        return self.__values

    @values.setter
    def values(self, l_2d):
        """値を登録"""
        if not isinstance(lines, list):
            raise TypeError('argument \'l_2d\' must be 2-dimensional list instance (values.setter in utaupy.reaper.py)')
        self.__values = lines

    @property
    def tags(self):
        """タグ一覧を取得"""
        return [v[0] for v in self.__values]

    @property
    def names(self):
        """リージョン名一覧を取得"""
        return [v[1] for v in self.__values]

    @property
    def starts(self):
        """開始時刻一覧を取得"""
        return [v[2] for v in self.__values]

    @property
    def ends(self):
        """終了時刻一覧を取得"""
        return [v[3] for v in self.__values]

    @property
    def lengths(self):
        """終了時刻一覧を取得"""
        return [v[4] for v in self.__values]


def write_csv(l, path, mode='w'):
    """
    二次元配列を受け取って、REAPERのリージョンに適したCSVを出力する。
    """
    # 見出し行を追加
    l = [['#', 'Name', 'Start', 'End', 'Length']] + l
    # ファイル出力
    with open(path) as f:
        writer = csv.writer(f)
        writer.writerows(l)


if __name__ == '__main__':
    main()
    print('Press enter to exit.')

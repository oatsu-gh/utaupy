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

    tmp = []
    # 行ごとにRegionオブジェクトを生成
    keys = tuple(l[0])
    for v in l[1:]:
        region = Region()
        region.values = dict(zip(keys, v))
        tmp.append(region)

    regioncsv = RegionCsv()
    regioncsv.values = tmp
    return regioncsv


class RegionCsv:
    """
    REAPERのリージョンCSV用のクラス
    """

    def __init__(self):
        # 辞書からなるリスト
        self.__l = []

    @property
    def values(self):
        """
        値を確認
        """
        return self.__l

    @values.setter
    def values(self, l):
        """
        値を代入
        """
        self.__l = l


    def append(self, region):
        """Regionオブジェクトを末尾に追加"""
        self.__l.append(region)


    def write(self, path, mode='w'):
        """
        REAPERのリージョンに適したCSVを出力する。
        """
        rows = [['#', 'Name', 'Start', 'End', 'Length']]
        for i, region in enumerate(self.__l):
            row = [f'R{i}', region.name, region.start, region.end, region.length]
            rows.append(row)
        # ファイル出力
        with open(path, mode=mode, encoding='utf-8', newline='\n') as f:
            writer = csv.writer(f)
            writer.writerows(rows)


class Region:
    """
    REAPERのリージョンひとつ分のクラス
    辞書
    """

    def __init__(self):
        self.__d = {'#': '', 'Name': '', 'Start': '', 'End': '', 'Length': ''}

    @property
    def values(self):
        """
        値を確認
        """
        return self.__d

    @values.setter
    def values(self, d):
        """
        値を代入
        """
        self.__d = d

    @property
    def name(self):
        return self.__d['Name']

    @name.setter
    def name(self, x):
        self.__d['Name'] = x

    @property
    def start(self):
        return self.__d['Start']

    @start.setter
    def start(self, x):
        self.__d['Start'] = x

    @property
    def end(self):
        return self.__d['End']

    @end.setter
    def end(self, x):
        self.__d['End'] = x

    @property
    def length(self):
        return self.__d['Length']

    @length.setter
    def length(self, x):
        self.__d['Length'] = x


if __name__ == '__main__':
    main()
    print('Press enter to exit.')

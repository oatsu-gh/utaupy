#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) oatsu
"""
UTAUのプラグイン用のモジュール
基本的には utaupy.ust の Ust() とか Note() を流用する。

【注意】本スクリプトは開発初期なため仕様変更が激しいです。
"""

from copy import deepcopy
from pprint import pprint
from sys import argv

from . import ust as _ust


def run(your_function):
    """
    UTAUプラグインスクリプトファイルの入出力をする。
    """
    # UTAUから出力されるプラグインスクリプトのパスを取得
    path = argv[1]
    # up.utauplugin.Plugin オブジェクトとしてプラグインスクリプトを読み取る
    plugin = load(path)
    # 目的のノート処理を実行
    your_function(plugin)
    # プラグインスクリプトを上書き
    plugin.write(path)


def load(path, mode='r', encoding='shift-jis'):
    """
    UTAUプラグイン一時ファイルを読み取る
    USTのやつを一部改変
    """
    ust = _ust.load(path, mode=mode, encoding=encoding)
    # UtauPluginオブジェクト化
    plugin = UtauPlugin()
    plugin.data = ust.data

    if ust[2].tag == '[#PREV]':
        plugin.previous_note = ust.pop(2)
    if ust[-1].tag == '[#NEXT]':
        plugin.next_note = ust.pop(-1)
    plugin.version = ust.version
    plugin.setting = ust.setting
    plugin.notes = ust[2:]
    return plugin


class UtauPlugin(_ust.Ust):
    """
    UTAUプラグインの一時ファイル用のクラス
    UST用のクラスを継承
    """

    def __init__(self):
        super().__init__()
        self.version = None  # [#VERSION]
        self.setting = None  # [#SETTING]
        self.previous_note = None  # [#PREV] のNoteオブジェクト
        self.__notes = []  # Noteオブジェクトのリスト
        self.next_note = None  # [#NEXT] のNoteオブジェクト

    def write(self, path, mode='w', encoding='shift-jis'):
        """
        プラグイン用のテキストをファイル出力する。
        UST と違って[#DELETE]でも書き込む。
        """
        duplicated_self = deepcopy(self)
        lines = []
        for note in duplicated_self.notes:
            # ノートを解体して行のリストにする
            d = note.values
            lines.append(d.pop('Tag'))
            for k, v in d.items():
                lines.append('{}={}'.format(str(k), str(v)))
        # 出力用の文字列
        s = '\n'.join(lines)
        # ファイル出力
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s

    @property
    def notes(self):
        """
        ノート部分を返す。Ustのままだと、さらに縮まってしまうため上書き。
        """
        return self.__notes

    @notes.setter
    def notes(self, x):
        """
        ノート部分を上書き。
        """
        self.__notes = list(x)

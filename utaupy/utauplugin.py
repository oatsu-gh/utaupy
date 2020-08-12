#!python3
# coding: utf-8
# Copyright (c) oatsu
"""
UTAUのプラグイン用のモジュール
基本的には utaupy.ust の Ust() とか Note() を流用する。

【注意】本スクリプトは開発初期なため仕様変更が激しいです。
"""

from pprint import pprint
from sys import argv

from utaupy import ust as _ust


def main():
    """
    直接実行されたときのやつ
    """
    print('UTAUプラグイン一時ファイルの読み取りテストをします。')
    path = input('テキストファイルのパスを入力してください。\n>>> ')
    plugin = load(path)
    for note in plugin.values:
        pprint(note.values, width=200)


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
    notes = ust.values
    # UtauPluginオブジェクト化
    plugin = UtauPlugin()
    plugin.version = notes.pop(0)
    plugin.setting = notes.pop(0)
    if notes[0].tag == '[#PREV]':
        plugin.prev = notes.pop(0)
    if notes[-1].tag == '[#NEXT]':
        plugin.next = notes.pop(-1)
    plugin.notes = notes
    return plugin


class UtauPlugin(_ust.Ust):
    """
    UTAUプラグインの一時ファイル用のクラス
    UST用のクラスを継承
    """

    def __init__(self):
        super().__init__()  # self._note = []
        self.version = None  # [#VERSION]
        self.setting = None  # [#SETTING]
        self.prev = None  # [#PREV] のNoteオブジェクト
        self.next = None  # [#NEXT] のNoteオブジェクト

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, l):
        self._notes = l


if __name__ == '__main__':
    main()

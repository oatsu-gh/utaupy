#!python3
# coding: utf-8
# Copyright (c) oatsu
"""
UTAUのプラグイン用のモジュール
基本的には utaupy.ust の Ust() とか Note() を流用する。

【注意】本スクリプトは開発初期なため仕様変更が激しいです。
"""

from pprint import pprint

from . import ust as _ust


def main():
    """
    直接実行されたときのやつ
    """
    print('UTAUプラグイン一時ファイルの読み取りテストをします。')
    path = input('テキストファイルのパスを入力してください。\n>>> ')
    plugin = load(path)
    for note in plugin.values:
        pprint(note.values, width=200)


def load(path, mode='r', encoding='shift-jis'):
    """
    UTAUプラグイン一時ファイルを読み取る
    USTのやつを一部改変
    """
    ust = _ust.load(path, mode='r', encoding='shift-jis')
    notes = ust.values
    plugin = PluginText()
    plugin.version = notes.pop(0)
    plugin.setting = notes.pop(0)
    if notes[0].tag == '[#PREV]':
        plugin.prev = notes.pop(0)
    if notes[-1].tag == '[#NEXT]':
        plugin.next = notes.pop(-1)
    plugin.notes = notes
    return plugin


class PluginText(_ust.Ust):
    """
    UTAUプラグインの一時ファイル用のクラス
    UST用のクラスを継承
    """

    def __init__(self):
        super().__init__()   # self._notes = []
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

    def insert_note(self, i):
        """
        i 番目の区切りに新規ノートを挿入する。
        このときの i は音符のみのインデックス。
        編集するために、挿入したノートを返す。
        """
        note = _ust.Note()
        note.tag = '[#INSERT]'
        self.notes.insert(i, note)
        return note

    def delete_note(self, i):
        """
        i 番目のノートを [#DELETE] する。
        """
        self.notes[i].tag = '[#DELETE]'


if __name__ == '__main__':
    main()

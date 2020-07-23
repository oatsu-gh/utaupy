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
    # ----ここからutaupy.ust.load()と同じ------------------------------------
    # USTを文字列として取得
    try:
        with open(path, mode=mode, encoding=encoding) as f:
            s = f.read()
    except UnicodeDecodeError:
        with open(path, mode=mode, encoding='utf-8_sig') as f:
            s = f.read()
    # USTをノート単位に分割
    l = [r'[#' + v.strip() for v in s.split(r'[#')][1:]
    # さらに行ごとに分割して二次元リストに
    l = [v.split('\n') for v in l]

    # ノートのリストを作る
    notes = []
    for lines in l:
        note = _ust.Note()
        # ノートの種類
        tag = lines[0]
        note.tag = tag
        # print('Making "Note" instance from UST: {}'.format(tag))
        # タグ以外の行の処理
        if tag == '[#VERSION]':
            note.set_by_key('Version', lines[1])
        elif tag == '[#TRACKEND]':
            pass
        else:
            for line in lines[1:]:
                key, value = line.split('=', 1)
                note.set_by_key(key, value)
        notes.append(note)

    # 旧形式の場合にタグの数を合わせる
    if notes[0].tag != r'[#VERSION]':
        version = notes[0].get_by_key('UstVersion')
        note = _ust.Note()
        note.tag = '[#VERSION]'
        note.set_by_key('UstVersion', version)
        notes.insert(0, note)  # リスト先頭に挿入
    # ----ここまでutaupy.ust.load()とほぼ同じ------------------------------------

    plugin = PluginText()
    plugin.version = notes.pop(0)
    plugin.setting = notes.pop(0)
    if notes[0].tag == r'[#PREV]':
        plugin.prev = notes.pop(0)
    if notes[-1].tag == r'[#NEXT]':
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
        ノート情報が無ければまっさらなノートを挿入する。
        このときの i は音符のみのインデックス。
        """
        new_note = _ust.Note()
        new_note.tag = '[#INSERT]'
        self.notes.insert(i, new_note)
        # 挿入したノートを編集できるように返す
        return new_note

    def delete_note(self, i):
        """
        i 番目のノートを [#DELETE] する。
        """
        self.notes[i].tag = r'[#DELETE]'


if __name__ == '__main__':
    main()

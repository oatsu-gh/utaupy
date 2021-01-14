#! /usr/bin/env python3
# coding: utf-8
"""
USTファイルとデータを扱うモジュールです。
"""
import re
from collections import UserDict
from copy import deepcopy
# from functools import lru_cache
# from pprint import pprint
from typing import List


def notenum_as_abc(notenum) -> str:
    """
    音階番号をABC表記に変更する(C1=24, C4=)
    """
    d = {'24': 'C1', '25': 'Db1', '26': 'D1', '27': 'Eb1', '28': 'E1', '29': 'F1',
         '30': 'Gb1', '31': 'G1', '32': 'Ab1', '33': 'A1', '34': 'Bb1', '35': 'B1',
         '36': 'C2', '37': 'Db2', '38': 'D2', '39': 'Eb2', '40': 'E2', '41': 'F2',
         '42': 'Gb2', '43': 'G2', '44': 'Ab2', '45': 'A2', '46': 'Bb2', '47': 'B2',
         '48': 'C3', '49': 'Db3', '50': 'D3', '51': 'Eb3', '52': 'E3', '53': 'F3',
         '54': 'Gb3', '55': 'G3', '56': 'Ab3', '57': 'A3', '58': 'Bb3', '59': 'B3',
         '60': 'C4', '61': 'Db4', '62': 'D4', '63': 'Eb4', '64': 'E4', '65': 'F4',
         '66': 'Gb4', '67': 'G4', '68': 'Ab4', '69': 'A4', '70': 'Bb4', '71': 'B4',
         '72': 'C5', '73': 'Db5', '74': 'D5', '75': 'Eb5', '76': 'E5', '77': 'F5',
         '78': 'Gb5', '79': 'G5', '80': 'Ab5', '81': 'A5', '82': 'Bb5', '83': 'B5',
         '84': 'C6', '85': 'Db6', '86': 'D6', '87': 'Eb6', '88': 'E6', '89': 'F6',
         '90': 'Gb6', '91': 'G6', '92': 'Ab6', '93': 'A6', '94': 'Bb6', '95': 'B6',
         '96': 'C7', '97': 'Db7', '98': 'D7', '99': 'Eb7', '100': 'E7', '101': 'F7',
         '102': 'Gb7', '103': 'G7', '104': 'Ab7', '105': 'A7', '106': 'Bb7', '107': 'B7',
         '108': 'C8', '109': 'Db8', '110': 'D8', '111': 'Eb8', '112': 'E8', '113': 'F8',
         '114': 'Gb8', '115': 'G8', '116': 'Ab8', '117': 'A8', '118': 'Bb8', '119': 'B8'}
    return d[str(notenum)]


def load(path: str, encoding: str = 'shift-jis'):
    """
    USTを読み取り
    """
    new_ust = Ust()
    new_ust.load(path, encoding=encoding)
    return new_ust


class Ust:
    """
    UST (UTAU Sequence Text) ファイルを扱うためのクラス
    """

    def __init__(self):
        super().__init__()
        # ノート(クラスオブジェクト)からなるリスト
        self.version = None   # [#VERSION]
        self.setting = None   # [#SETTING]
        self.notes: List[Note] = []       # [#1234], [#INSERT], [#DELETE]
        self.trackend = None  # [#TRACKEND]
        self.next_note = None      # [#NEXT]
        self.previous_note = None      # [#PREV]

    def __str__(self):
        # self.notesが増減するので複製したものを扱う
        duplicated_self = deepcopy(self)
        # 特殊ノートを処理
        if self.setting is not None:
            duplicated_self.notes.insert(0, self.setting)
        if self.previous_note is not None:
            duplicated_self.notes.insert(0, self.previous_note)
        if self.next_note is not None:
            duplicated_self.notes.append(self.next_note)
        if self.trackend is not None:
            duplicated_self.notes.append(self.trackend)
        # 通常ノートを文字列にする
        s = '\n'.join(str(note) for note in duplicated_self.notes)
        # バージョン情報があれば先頭に追記
        if self.version is not None:
            str_version = f'[#VERSION]\nUST Version {str(duplicated_self.version)}'
            s = '\n'.join((str_version, s))
        return s

    def load(self, path: str, encoding='shift-jis'):
        """
        ファイルからインスタンス生成
        """
        # USTを文字列として取得
        try:
            with open(path, mode='r', encoding=encoding) as f:
                s = f.read().strip()
        except UnicodeDecodeError:
            try:
                with open(path, mode='r', encoding='utf-8') as f:
                    s = f.read().strip()
            except UnicodeDecodeError:
                with open(path, mode='r', encoding='utf-8_sig') as f:
                    s = f.read().strip()

        # USTの文字列をノート単位に分割
        l: List[str] = [f'[#{v.strip()}' for v in s.split('[#')][1:]
        l_2d = [s.split('\n') for s in l]

        # ノートのリストを作る
        for lines in l_2d:
            # 1行目: ノートの種類
            tag = lines[0]
            # print('reading entry:', tag)  # デバッグ用出力
            note = Note(tag=tag)
            # どこに登録するか決める
            if tag not in ('[#VERSION]', '[#SETTING]', '[#TRACKEND]', '[#PREV]', '[#NEXT]'):
                self.notes.append(note)
            elif tag == '[#VERSION]':
                self.version = lines[1].replace('UST Version ', '')
                continue
            elif tag == '[#SETTING]':
                self.setting = note
            elif tag == '[#PREV]':
                self.previous_note = note
            elif tag == '[#NEXT]':
                self.next_note = note
            elif tag == '[#TRACKEND]':
                self.trackend = note
            else:
                raise Exception('想定外のエラーです。開発者に連絡してください。:', tag, str(note))
            # 2行目移行: タグ以外の情報
            for line in lines[1:]:
                key, value = line.split('=', maxsplit=1)
                note[key] = value

        # 隠しパラメータ alternative_tempo を全ノートに設定
        self.reload_tempo()
        return self

    @ property
    def tempo(self) -> float:
        """
        USTのグローバルテンポ
        """
        # 2020-12-19以前の実装------------
        # global_tempo = self.setting.get('Tempo', self.notes[0].tempo)
        # --------------------------------
        if 'Tempo' not in self.setting:
            self.setting['Tempo'] = self.notes[0].tempo
        return self.setting['Tempo']

    @ tempo.setter
    def tempo(self, tempo):
        self.setting.tempo = tempo
        # self.notes[0].tempo = tempo
        self.reload_tempo()

    def clean_tempo(self):
        """
        ローカルテンポが不要な部分を削除する。
        """
        # まずはグローバルテンポを取得
        current_tempo = self.tempo
        # 不要なデータを削除
        for note in self.notes:
            if 'Tempo' in note:
                if note['Tempo'] == current_tempo:
                    del note['Tempo']
            else:
                current_tempo = note.tempo

    def reload_tempo(self):
        """
        1. グローバルテンポを1ノート目のテンポで上書きする。
        2. 各ノートでBPMが取得できるように note.alternative_tempo を全ノートに仕込む。
        """
        if 'Tempo' in self.notes[0]:
            self.setting['Tempo'] = self.notes[0]['Tempo']
        current_tempo = self.setting['Tempo']
        for note in self.notes:
            if 'Tempo' in note:
                if float(note['Tempo']) == current_tempo:
                    del note['Tempo']
                else:
                    current_tempo = note['Tempo']
            # current_tempo = note.get('Tempo', current_tempo)
            note.alternative_tempo = float(current_tempo)
        self.clean_tempo()

    def reload_tag_number(self, start: int = 0):
        """
        start: 開始番号 (0なら[#0000]から)
        各ノートのノート番号を振りなおす。
        ファイル出力時に実行することを想定。
        """
        for i, note in enumerate(self.notes, start):
            note.tag = f'[#{str(i).zfill(4)}]'

    # ノート一括編集系関数ここから----------------------------------------------
    def replace_lyrics(self, before: str, after: str):
        """歌詞を一括置換（文字列指定・破壊的処理）"""
        for note in self.notes:
            note.lyric = note.lyric.replace(before, after)

    def translate_lyrics(self, before, after):
        """歌詞を一括置換（複数文字指定・破壊的処理）"""
        for note in self.notes:
            note.lyric = note.lyric.translate(before, after)

    def vcv2cv(self):
        """歌詞を平仮名連続音から単独音にする"""
        for note in self.notes:
            note.lyric = note.lyric.split()[-1]
    # ノート一括編集系関数ここまで----------------------------------------------

    def insert_note(self, i: int):
        """
        i 番目の区切りに新規ノートを挿入する。
        このときの i は音符のみのインデックス。
        編集するために、挿入したノートを返す。
        """
        note = Note()
        note.tag = '[#INSERT]'
        self.notes.insert(i, note)
        return note

    def delete_note(self, i: int):
        """
        i 番目のノートを [#DELETE] する。
        """
        self.notes[i].tag = '[#DELETE]'

    def make_finalnote_R(self):
        """Ustの最後のノートが休符 になるようにする"""
        last_note = self.notes[-1]
        # Ust内の最後はTRACKENDなので後ろから2番目のノートで判定
        if last_note.lyric not in ('pau', 'sil', 'R'):
            print('  末尾に休符を自動追加します。')
            rest_note = deepcopy(last_note)
            rest_note.lyric = 'R'
            self.notes.append(rest_note)
        self.reload_tempo()

    def write(self, path: str, mode: str = 'w', encoding: str = 'shift-jis') -> str:
        """
        USTをファイル出力
        """
        duplicated_self = deepcopy(self)
        # [#DELETE] なノートをファイル出力しないために削除
        duplicated_self.notes = [
            note for note in duplicated_self.notes if note.tag != '[#DELETE]'
        ]
        # ノート番号を振りなおす
        duplicated_self.reload_tag_number()
        # 文字列にする
        s = str(duplicated_self) + '\n'
        # ファイル出力
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s


class Note(UserDict):
    """UST内のノート"""

    def __init__(self, tag: str = '[#UNDEFINED]'):
        super().__init__()
        self['Tag'] = tag
        self.alternative_tempo = None

    def __str__(self):
        lines = [self['Tag']] + [f'{k}={v}' for (k, v) in self.items() if k != 'Tag']
        return '\n'.join(lines)

    @property
    def tag(self):
        """タグを確認"""
        return self['Tag']

    @tag.setter
    def tag(self, s):
        """タグを上書き"""
        self['Tag'] = s

    @property
    def length(self):
        """ノート長を確認[Ticks]"""
        return int(self['Length'])

    @length.setter
    def length(self, x):
        """ノート長を上書き[Ticks]"""
        self['Length'] = str(x)

    @property
    def length_ms(self) -> float:
        """ノート長を確認[ms]"""
        return 125 * float(self['Length']) / self.tempo

    @length_ms.setter
    def length_ms(self, x):
        """ノート長を上書き[ms]"""
        self['Length'] = str(round(x * self.tempo / 125))

    @property
    def lyric(self):
        """
        歌詞
        """
        return self['Lyric']

    @lyric.setter
    def lyric(self, x):
        self['Lyric'] = x

    @property
    def notenum(self):
        """
        音階番号
        """
        return int(self['NoteNum'])

    @notenum.setter
    def notenum(self, x):
        self['NoteNum'] = str(x)

    @property
    def tempo(self) -> float:
        """
        ローカルBPM
        """
        return float(self.get('Tempo', self.alternative_tempo))

    @tempo.setter
    def tempo(self, x):
        self['Tempo'] = str(x)

    @property
    def pbs(self):
        """
        PBS (mode2ピッチ開始位置[ms]) を取得
        例) PBS=-104;20.0
        """
        # 辞書には文字列で登録してある
        str_pbs = self['PBS']
        # 浮動小数のリストに変換
        list_pbs = list(map(float, re.split('[;,]', str_pbs)))
        # PBSの値をリストで返す
        return list_pbs

    @pbs.setter
    def pbs(self, list_pbs):
        """
        PBS (mode2ピッチ開始位置[ms]) を登録
        例) PBS=-104;20.0
        """
        s1 = f'{int(list_pbs[0])};'
        s2 = ','.join(map(str, list_pbs[1:]))

        str_pbs = s1 + s2
        self['PBS'] = str_pbs

    @property
    def pbw(self):
        """
        PBW (mode2ピッチ点の間隔[ms]) を取得
        例) PBW=77,163
        """
        # 辞書には文字列で登録してある
        s_pbw = self['PBW']
        # 整数のリストに変換
        l_pbw = list(map(int, s_pbw.split(',')))
        # PBWの値をリストで返す
        return l_pbw

    @pbw.setter
    def pbw(self, list_pbw):
        """
        PBW (mode2ピッチ点の間隔[ms]) を登録
        例) PBW=77,163
        """
        # リストを整数の文字列に変換
        str_pbw = ','.join(list(map(str, map(int, list_pbw))))
        self['PBW'] = str_pbw

    @property
    def pby(self):
        """
        PBY (mode2ピッチ点の高さ) を取得
        例) PBY=-10.6,0.0
        """
        # 辞書には文字列で登録してある
        s_pby = self['PBY']
        # 整数のリストに変換
        l_pby = list(map(float, s_pby.split(',')))
        # PBYの値をリストで返す
        return l_pby

    @pby.setter
    def pby(self, list_pby):
        """
        PBY (mode2ピッチ点の高さ) を登録
        例) PBY=-10.6,0.0
        """
        # リストを小数の文字列に変換
        str_pby = ','.join(list(map(str, map(float, list_pby))))
        self['PBY'] = str_pby

    @property
    def pbm(self):
        """
        PBM (mode2ピッチ点の形状) を取得
        例) PBY=-10.6,0.0
        """
        # 辞書には文字列で登録してある
        s_pby = self['PBM']
        # 整数のリストに変換
        l_pbm = s_pby.split(',')
        # PBYの値をリストで返す
        return l_pbm

    @pbm.setter
    def pbm(self, list_pbm):
        """
        PBM (mode2ピッチ点の形状) を登録
        例) PBM=,r,j,s
        """
        # リストを文字列に変換
        str_pbm = ','.join(list_pbm)
        self['PBM'] = str_pbm

    @property
    def velocity(self):
        """
        子音速度
        """
        return int(self.get('Velocity', 100))

    @velocity.setter
    def velocity(self, x: int):
        self['Velocity'] = int(x)

    @property
    def flags(self) -> str:
        """
        フラグ
        """
        return self.get('Flags', '')

    @flags.setter
    def flags(self, flags: str):
        self['Flags'] = str(flags)

    # ここからデータ操作系-----------------------------------------------------
    def get_by_key(self, key):
        """
        ノートの特定の情報を取得
        UserDictになったのでいずれ消す
        """
        return self[key]

    def set_by_key(self, key, x):
        """ノートの特定の情報を上書きまたは登録
        UserDictになったのでいずれ消す
        """
        self[key] = x
    # ここまでデータ操作系-----------------------------------------------------

    # ここからノート操作系-----------------------------------------------------
    def delete(self):
        """選択ノートを削除"""
        self.tag = '[#DELETE]'
        return self

    # def insert(self):
    #     """ノートを挿入(したい)"""
    #     self.tag = '[#INSERT]'
    #     return self

    def refresh(self):
        """
        ノートの情報を引き継ぎつつ、自由にいじれるようにする
        UTAUプラグインは値の上書きはできるが削除はできない。
        一旦ノートを削除して新規ノートとして扱う必要がある。
        """
        self.tag = '[#DELETE]\n[#INSERT]'

    def suppin(self):
        """ノートの情報を最小限にする"""
        new_data = {}
        new_data['Tag'] = '[#DELETE]\n[#INSERT]'
        new_data['Lyric'] = self.lyric
        new_data['Length'] = self.length
        new_data['NoteNum'] = self.notenum
        self.data = new_data
    # ここまでノート操作系-----------------------------------------------------


def main():
    """実行されたときの挙動"""
    print('デフォ子かわいいよデフォ子\n')

    print('ust読み取りテストをします。')
    path = input('ustのパスを入力してください。\n>>> ')
    ust = load(path)
    print(ust)

    input('\nPress Enter to exit.')


if __name__ == '__main__':
    main()

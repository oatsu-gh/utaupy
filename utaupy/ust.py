#! /usr/bin/env python3
"""
USTファイルとデータを扱うモジュールです。
"""

import re
from collections import UserDict
from copy import deepcopy
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from typing import Optional, Union
from warnings import warn

from utaupy.utau import (  # pylint: disable=relative-beyond-top-level
    utau_appdata_root,
    utau_root,
)

NOTENUM_TO_NOTENAME_DICT = {
    12: 'C0',
    13: 'Db0',
    14: 'D0',
    15: 'Eb0',
    16: 'E0',
    17: 'F0',
    18: 'Gb0',
    19: 'G0',
    20: 'Ab0',
    21: 'A0',
    22: 'Bb0',
    23: 'B0',
    24: 'C1',
    25: 'Db1',
    26: 'D1',
    27: 'Eb1',
    28: 'E1',
    29: 'F1',
    30: 'Gb1',
    31: 'G1',
    32: 'Ab1',
    33: 'A1',
    34: 'Bb1',
    35: 'B1',
    36: 'C2',
    37: 'Db2',
    38: 'D2',
    39: 'Eb2',
    40: 'E2',
    41: 'F2',
    42: 'Gb2',
    43: 'G2',
    44: 'Ab2',
    45: 'A2',
    46: 'Bb2',
    47: 'B2',
    48: 'C3',
    49: 'Db3',
    50: 'D3',
    51: 'Eb3',
    52: 'E3',
    53: 'F3',
    54: 'Gb3',
    55: 'G3',
    56: 'Ab3',
    57: 'A3',
    58: 'Bb3',
    59: 'B3',
    60: 'C4',
    61: 'Db4',
    62: 'D4',
    63: 'Eb4',
    64: 'E4',
    65: 'F4',
    66: 'Gb4',
    67: 'G4',
    68: 'Ab4',
    69: 'A4',
    70: 'Bb4',
    71: 'B4',
    72: 'C5',
    73: 'Db5',
    74: 'D5',
    75: 'Eb5',
    76: 'E5',
    77: 'F5',
    78: 'Gb5',
    79: 'G5',
    80: 'Ab5',
    81: 'A5',
    82: 'Bb5',
    83: 'B5',
    84: 'C6',
    85: 'Db6',
    86: 'D6',
    87: 'Eb6',
    88: 'E6',
    89: 'F6',
    90: 'Gb6',
    91: 'G6',
    92: 'Ab6',
    93: 'A6',
    94: 'Bb6',
    95: 'B6',
    96: 'C7',
    97: 'Db7',
    98: 'D7',
    99: 'Eb7',
    100: 'E7',
    101: 'F7',
    102: 'Gb7',
    103: 'G7',
    104: 'Ab7',
    105: 'A7',
    106: 'Bb7',
    107: 'B7',
    108: 'C8',
    109: 'Db8',
    110: 'D8',
    111: 'Eb8',
    112: 'E8',
    113: 'F8',
    114: 'Gb8',
    115: 'G8',
    116: 'Ab8',
    117: 'A8',
    118: 'Bb8',
    119: 'B8',
    120: 'C9',
    121: 'Db9',
    122: 'D9',
    123: 'Eb9',
    124: 'E9',
    125: 'F9',
    126: 'Gb9',
    127: 'G9',
    '12': 'C0',
    '13': 'Db0',
    '14': 'D0',
    '15': 'Eb0',
    '16': 'E0',
    '17': 'F0',
    '18': 'Gb0',
    '19': 'G0',
    '20': 'Ab0',
    '21': 'A0',
    '22': 'Bb0',
    '23': 'B0',
    '24': 'C1',
    '25': 'Db1',
    '26': 'D1',
    '27': 'Eb1',
    '28': 'E1',
    '29': 'F1',
    '30': 'Gb1',
    '31': 'G1',
    '32': 'Ab1',
    '33': 'A1',
    '34': 'Bb1',
    '35': 'B1',
    '36': 'C2',
    '37': 'Db2',
    '38': 'D2',
    '39': 'Eb2',
    '40': 'E2',
    '41': 'F2',
    '42': 'Gb2',
    '43': 'G2',
    '44': 'Ab2',
    '45': 'A2',
    '46': 'Bb2',
    '47': 'B2',
    '48': 'C3',
    '49': 'Db3',
    '50': 'D3',
    '51': 'Eb3',
    '52': 'E3',
    '53': 'F3',
    '54': 'Gb3',
    '55': 'G3',
    '56': 'Ab3',
    '57': 'A3',
    '58': 'Bb3',
    '59': 'B3',
    '60': 'C4',
    '61': 'Db4',
    '62': 'D4',
    '63': 'Eb4',
    '64': 'E4',
    '65': 'F4',
    '66': 'Gb4',
    '67': 'G4',
    '68': 'Ab4',
    '69': 'A4',
    '70': 'Bb4',
    '71': 'B4',
    '72': 'C5',
    '73': 'Db5',
    '74': 'D5',
    '75': 'Eb5',
    '76': 'E5',
    '77': 'F5',
    '78': 'Gb5',
    '79': 'G5',
    '80': 'Ab5',
    '81': 'A5',
    '82': 'Bb5',
    '83': 'B5',
    '84': 'C6',
    '85': 'Db6',
    '86': 'D6',
    '87': 'Eb6',
    '88': 'E6',
    '89': 'F6',
    '90': 'Gb6',
    '91': 'G6',
    '92': 'Ab6',
    '93': 'A6',
    '94': 'Bb6',
    '95': 'B6',
    '96': 'C7',
    '97': 'Db7',
    '98': 'D7',
    '99': 'Eb7',
    '100': 'E7',
    '101': 'F7',
    '102': 'Gb7',
    '103': 'G7',
    '104': 'Ab7',
    '105': 'A7',
    '106': 'Bb7',
    '107': 'B7',
    '108': 'C8',
    '109': 'Db8',
    '110': 'D8',
    '111': 'Eb8',
    '112': 'E8',
    '113': 'F8',
    '114': 'Gb8',
    '115': 'G8',
    '116': 'Ab8',
    '117': 'A8',
    '118': 'Bb8',
    '119': 'B8',
    '120': 'C9',
    '121': 'Db9',
    '122': 'D9',
    '123': 'Eb9',
    '124': 'E9',
    '125': 'F9',
    '126': 'Gb9',
    '127': 'G9',
}

NOTENAME_TO_NOTENUM_DICT = {
    'Cb0': 11,
    'C0': 12,
    'C#0': 13,
    'Db0': 13,
    'D0': 14,
    'D#0': 15,
    'Eb0': 15,
    'E0': 16,
    'E#0': 17,
    'Fb0': 16,
    'F0': 17,
    'F#0': 18,
    'Gb0': 18,
    'G0': 19,
    'G#0': 20,
    'Ab0': 20,
    'A0': 21,
    'A#0': 22,
    'Bb0': 22,
    'B0': 23,
    'B#0': 24,
    'Cb1': 23,
    'C1': 24,
    'C#1': 25,
    'Db1': 25,
    'D1': 26,
    'D#1': 27,
    'Eb1': 27,
    'E1': 28,
    'E#1': 29,
    'Fb1': 28,
    'F1': 29,
    'F#1': 30,
    'Gb1': 30,
    'G1': 31,
    'G#1': 32,
    'Ab1': 32,
    'A1': 33,
    'A#1': 34,
    'Bb1': 34,
    'B1': 35,
    'B#1': 36,
    'Cb2': 35,
    'C2': 36,
    'C#2': 37,
    'Db2': 37,
    'D2': 38,
    'D#2': 39,
    'Eb2': 39,
    'E2': 40,
    'E#2': 41,
    'Fb2': 40,
    'F2': 41,
    'F#2': 42,
    'Gb2': 42,
    'G2': 43,
    'G#2': 44,
    'Ab2': 44,
    'A2': 45,
    'A#2': 46,
    'Bb2': 46,
    'B2': 47,
    'B#2': 38,
    'Cb3': 47,
    'C3': 48,
    'C#3': 49,
    'Db3': 49,
    'D3': 50,
    'D#3': 51,
    'Eb3': 51,
    'E3': 52,
    'E#3': 53,
    'Fb3': 52,
    'F3': 53,
    'F#3': 54,
    'Gb3': 54,
    'G3': 55,
    'G#3': 56,
    'Ab3': 56,
    'A3': 57,
    'A#3': 58,
    'Bb3': 58,
    'B3': 59,
    'B#3': 60,
    'Cb4': 59,
    'C4': 60,
    'C#4': 61,
    'Db4': 61,
    'D4': 62,
    'D#4': 63,
    'Eb4': 63,
    'E4': 64,
    'E#4': 65,
    'Fb4': 64,
    'F4': 65,
    'F#4': 66,
    'Gb4': 66,
    'G4': 67,
    'G#4': 68,
    'Ab4': 68,
    'A4': 69,
    'A#4': 70,
    'Bb4': 70,
    'B4': 71,
    'B#4': 72,
    'Cb5': 71,
    'C5': 72,
    'C#5': 73,
    'Db5': 73,
    'D5': 74,
    'D#5': 75,
    'Eb5': 75,
    'E5': 76,
    'E#5': 77,
    'Fb5': 76,
    'F5': 77,
    'F#5': 78,
    'Gb5': 78,
    'G5': 79,
    'G#5': 79,
    'Ab5': 80,
    'A5': 81,
    'A#5': 82,
    'Bb5': 82,
    'B5': 83,
    'B#5': 84,
    'Cb6': 83,
    'C6': 84,
    'C#6': 85,
    'Db6': 85,
    'D6': 86,
    'D#6': 87,
    'Eb6': 87,
    'E6': 88,
    'E#6': 89,
    'Fb6': 88,
    'F6': 89,
    'F#6': 90,
    'Gb6': 90,
    'G6': 91,
    'G#6': 92,
    'Ab6': 92,
    'A6': 93,
    'A#6': 94,
    'Bb6': 94,
    'B6': 95,
    'B#6': 96,
    'Cb7': 95,
    'C7': 96,
    'C#7': 97,
    'Db7': 97,
    'D7': 98,
    'D#7': 99,
    'Eb7': 99,
    'E7': 100,
    'E#7': 101,
    'Fb7': 100,
    'F7': 101,
    'F#7': 102,
    'Gb7': 102,
    'G7': 103,
    'G#7': 104,
    'Ab7': 104,
    'A7': 105,
    'A#7': 106,
    'Bb7': 106,
    'B7': 107,
    'B#7': 108,
    'Cb8': 107,
    'C8': 108,
    'C#8': 109,
    'Db8': 109,
    'D8': 110,
    'D#8': 111,
    'Eb8': 111,
    'E8': 112,
    'E#8': 113,
    'Fb8': 112,
    'F8': 113,
    'F#8': 114,
    'Gb8': 114,
    'G8': 115,
    'G#8': 116,
    'Ab8': 116,
    'A8': 117,
    'A#8': 118,
    'Bb8': 118,
    'B8': 119,
    'B#8': 120,
    'Cb9': 119,
    'C9': 120,
    'C#9': 121,
    'Db9': 121,
    'D9': 122,
    'D#9': 123,
    'Eb9': 123,
    'E9': 124,
    'E#9': 125,
    'Fb9': 124,
    'F9': 125,
    'F#9': 126,
    'Gb9': 126,
    'G9': 127,
}

TIMESIGNATURES_PATTERN = re.compile(r'\(\d+/\d+/\d+\)')


def notenum_as_abc(notenum) -> str:
    """
    音階番号をABC表記に変更する(C1=24, C4=60)
    """
    return NOTENUM_TO_NOTENAME_DICT[int(notenum)]


def load(path: str, encoding: str = 'cp932'):
    """
    USTを読み取り
    """
    new_ust = Ust()
    new_ust.load(path.strip('"'), encoding=encoding)
    return new_ust


class Ust:
    """
    UST (UTAU Sequence Text) ファイルを扱うためのクラス
    """

    def __init__(self):
        self.version = None  # [#VERSION]
        self.notes: list[Note] = []  # [#1234], [#INSERT], [#DELETE]
        self.setting = Note(tag='[#SETTING]')  # [#SETTING]
        self.trackend = Note(tag='[#TRACKEND]')  # [#TRACKEND]
        self.next_note = None  # [#NEXT]
        self.previous_note = None  # [#PREV]
        # 初期値を設定したり消したりする
        self.setting['Tempo'] = 120
        self.setting['$TimeSignatures'] = '(4/4/0)'
        del self.setting['Length']
        del self.setting['NoteNum']
        del self.trackend['Length']
        del self.trackend['NoteNum']

    def __str__(self):
        l: list[str] = []
        # [#VERSION]
        if self.version is not None:
            l.append(f'[#VERSION]\nUST Version {str(self.version)}')
        # [#SETTING]
        if len(self.setting) >= 2:
            l.append(str(self.setting))
        # [#PREV]
        if self.previous_note is not None:
            l.append(str(self.previous_note))
        # 歌詞とかが入ってるメインのノート群を追加
        l.append('\n'.join(str(note) for note in self.notes))
        # [#NEXT]
        if self.next_note is not None:
            l.append(str(self.next_note))
        # [#TRACKEND]
        if self.trackend is not None:
            l.append(str(self.trackend))
        # 改行文字で結合した文字列を返す
        return '\n'.join(l)

    def load(self, path: str, encoding='cp932'):
        """
        ファイルからインスタンス生成
        """
        # USTを文字列として取得
        try:
            with open(path, encoding=encoding) as f:
                s = f.read().strip()
        except UnicodeDecodeError:
            try:
                with open(path, encoding='utf-8') as f:
                    s = f.read().strip()
            except UnicodeDecodeError:
                with open(path, encoding='utf-8_sig') as f:
                    s = f.read().strip()

        # USTの文字列をノート単位に分割
        l: list[str] = [f'[#{v.strip()}' for v in s.split('[#')][1:]
        l_2d = [s.split('\n') for s in l]

        # ノートのリストを作る
        for lines in l_2d:
            # 1行目: ノートの種類
            tag = lines[0]
            note = Note(tag=tag)
            # どこに登録するか決める
            if tag not in {
                '[#VERSION]',
                '[#SETTING]',
                '[#TRACKEND]',
                '[#PREV]',
                '[#NEXT]',
            }:
                self.notes.append(note)
            elif tag == '[#VERSION]':
                self.version = (
                    lines[1].replace(' ', '').lower().replace('ustversion', '')
                )
                del note
                continue
            elif tag == '[#SETTING]':
                del note['Length']
                del note['NoteNum']
                note.update(self.setting)  # __init__で定義した初期設定を保持
                self.setting = note
            elif tag == '[#PREV]':
                self.previous_note = note
            elif tag == '[#NEXT]':
                self.next_note = note
            elif tag == '[#TRACKEND]':
                del note['Length']
                del note['NoteNum']
                self.trackend = note
            else:
                raise Exception(
                    '想定外のエラーです。開発者に連絡してください。:', tag, str(note)
                )
            # 2行目移行: タグ以外の情報
            for line in lines[1:]:
                key, value = line.split('=', maxsplit=1)
                note[key] = value

        # ノート長を整数にする
        self.round_length()
        # 音階番号を整数にする
        self.round_notenum()
        # 隠しパラメータ _hidden_dict['Tempo'] を全ノートに設定
        self.reload_tempo()
        # 隠しパラメータ _hidden_dict['$TimeSignatures] を全ノートに設定
        self.reload_timesignatures()
        return self

    @property
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

    @tempo.setter
    def tempo(self, tempo):
        self.setting.tempo = tempo
        # self.notes[0].tempo = tempo
        self.reload_tempo()

    @property
    def timesignatures(self) -> str:
        """
        USTのグローバルな拍子情報
        独自エントリを使用するため、[#SETTING] ではなく最初のノートから取得する。
        UST Ver.2.0 以降では (4/4/0) のような表記をするらしい。
        """
        if '$TimeSignatures' not in self.setting:
            self.setting['$TimeSignatures'] = self.notes[0].timesignatures
        return self.setting['$TimeSignatures']

    @timesignatures.setter
    def timesignatures(self, x):
        if not TIMESIGNATURES_PATTERN.match(x):
            raise ValueError(
                '拍子情報の表記が不適切です。"(4/4/0)" のように表記してください。'
            )
        self.setting['$TimeSignatures'] = str(x)
        self.reload_timesignatures()

    @property
    def voicedir(self):
        """
        UTAU音源のフォルダのパスを返す
        """
        voicedir = self.setting['VoiceDir']
        voicedir = voicedir.replace('%VOICE%', f'{utau_root()}\\voice\\')
        voicedir = voicedir.replace('%DATA%', utau_appdata_root())
        return voicedir  # noqa: RET504

    @voicedir.setter
    def voicedir(self, path):
        self.setting['VoiceDir'] = path.strip('\'"')

    def round_length(self, rounding=ROUND_HALF_EVEN):
        """
        SynthVなどで生成したUSTファイルだとLengthが小数になっていることがあるので、整数に丸める。
        UST全体の長さがずれないように銀行丸めを用いる。
        """
        for note in self.notes:
            note['Length'] = int(
                Decimal(note['Length']).quantize(Decimal(0), rounding=rounding)
            )

    def round_notenum(self, rounding=ROUND_HALF_UP):
        """
        SynthVなどで生成したUSTファイルだとNoteNumが小数になっていることがあるので、整数に丸める。
        銀行丸めではなく四捨五入を用いる。
        """
        for note in self.notes:
            note['NoteNum'] = int(
                Decimal(note['NoteNum']).quantize(Decimal(0), rounding=rounding)
            )

    def clean_tempo(self):
        """
        ローカルテンポが不要な部分を削除する。
        """
        # # まずはグローバルテンポを取得
        # current_tempo = self.tempo
        # # 不要なデータを削除
        # for note in self.notes:
        #     if 'Tempo' in note:
        #         if note['Tempo'] == current_tempo:
        #             del note['Tempo']
        #     else:
        #         current_tempo = note.tempo
        self._clean_local_value('Tempo')

    def _clean_local_value(self, key: str):
        """
        テンポや拍子情報のように、グローバル値とローカル値を
        持ちうるパラメータの余分なものを削除する。
        """
        # pylint: disable=protected-access
        # まずはグローバルテンポを取得
        first_note = self.notes[0]
        first_local_value = first_note.get(key, first_note._hidden_dict[key])
        current_value = self.setting.get(key, first_local_value)
        # 不要なデータを削除
        for note in self.notes:
            if key in note:
                if note[key] == current_value:
                    del note[key]
            else:
                current_value = note.get(key, note._hidden_dict[key])

    def reload_local_value(self, key: str):
        """
        テンポや拍子情報など、グローバルな値とローカルな値を持ちうる変数の
        ローカル情報を一時的に格納するためのパラメーターを、
        最新の状態に更新する。

        グローバルな値か、1ノート目のローカルな値のどちらかが存在する前提で処理をすることに注意。

        ## テンポの場合の例
        1. グローバルテンポを1ノート目のテンポで上書きする。
        2. 各ノートでBPMが取得できるように
           note._hidden_dict['Tempo'] を全ノートに仕込む。
        """
        # pylint: disable=protected-access

        # ノートがないときは何もしない
        if len(self.notes) == 0:
            return
        # ここからはノートが1つ以上あるとき
        if key in self.notes[0]:
            self.setting[key] = self.notes[0][key]
        current_value = self.setting[key]

        # [#PREV]に_hidden_dict['Tempo']を登録
        previous_note = self.previous_note
        if previous_note is not None:
            previous_note._hidden_dict[key] = previous_note.get(key, current_value)

        # 通常のノートに_hidden_dict['Tempo']を登録
        for note in self.notes:
            if key in note:
                if note[key] == current_value:
                    del note[key]
                else:
                    current_value = note[key]
            # current_value = note.get(key, current_value)
            note._hidden_dict[key] = current_value

        # [#NEXT]に_hidden_dict['Tempo']を登録
        next_note = self.next_note
        if next_note is not None:
            next_note._hidden_dict[key] = next_note.get(key, current_value)

        # 全ノートに登録する必要はないので、不要なものを削除
        self._clean_local_value(key)

    def reload_tempo(self):
        """
        1. グローバルテンポを1ノート目のテンポで上書きする。
        2. 各ノートでBPMが取得できるように
           note._hidden_dict['Tempo'] を全ノートに仕込む。
        """
        self.reload_local_value('Tempo')

    def reload_timesignatures(self):
        """
        拍子情報を各ノートに登録する
        """
        self.reload_local_value('$TimeSignatures')

    # NOTE: メジャーアップデートの時に変更する
    def reload_index(self, start: int = 0):
        """
        start: 開始番号 (0なら[#0000]から)
        各ノートのノート番号を振りなおす。
        ファイル出力時に実行することを想定。
        """
        for i, note in enumerate(self.notes, start):
            note.tag = f'[#{str(i).zfill(4)}]'

    def reload_tag_number(self, start: int = 0):
        """
        start: 開始番号 (0なら[#0000]から)
        各ノートのノート番号を振りなおす。
        ファイル出力時に実行することを想定。
        """
        warn(
            'Use utaupy.Ust.reload_index() instead of utaupy.Ust.reload_tag_number()',
            DeprecationWarning,
            stacklevel=2,
        )
        self.reload_index(start=start)

    # ノート一括編集系関数ここから----------------------------------------------
    def replace_lyrics(self, before: str, after: str):
        """
        歌詞を一括置換（文字列指定・破壊的処理）
        """
        for note in self.notes:
            note.lyric = note.lyric.replace(before, after)

    def translate_lyrics(self, before, after):
        """
        歌詞を一括置換（複数文字指定・破壊的処理）
        """
        for note in self.notes:
            note.lyric = note.lyric.translate(before, after)

    def vcv2cv(self):
        """
        歌詞を平仮名連続音から単独音にする
        """
        for note in self.notes:
            note.lyric = note.lyric.split(' ', 1)[-1]

    # ノート一括編集系関数ここまで----------------------------------------------

    def insert_note(self, i: int):
        """
        i 番目の区切りに新規ノートを挿入する。
        このときの i は音符のみのインデックス。
        編集するために、挿入したノートを返す。
        """
        note = Note()
        # note.tag = '[#INSERT]'
        self.notes.insert(i, note)
        return note

    def delete_note(self, i: int):
        """
        i 番目のノートを [#DELETE] する。
        """
        self.notes[i].tag = '[#DELETE]'

    def make_final_note_R(self):
        """
        Ustの最後のノートが休符 になるようにする
        """
        last_note = self.notes[-1]
        # Ust内の最後はTRACKENDなので後ろから2番目のノートで判定
        if last_note.lyric not in ('pau', 'sil', 'R'):
            rest_note = deepcopy(last_note)
            rest_note.lyric = 'R'
            rest_note.length = 480
            self.notes.append(rest_note)
        self.reload_tempo()

    def make_finalnote_R(self):
        """
        旧バージョンに対する互換性維持
        """
        self.make_final_note_R()

    def write(self, path: str, mode: str = 'w', encoding: str = 'cp932') -> str:
        """
        USTをファイル出力
        """
        duplicated_self = deepcopy(self)
        # [#DELETE] なノートをファイル出力しないために削除
        duplicated_self.notes = [
            note for note in duplicated_self.notes if note.tag != '[#DELETE]'
        ]
        # テンポを整理する
        duplicated_self.reload_tempo()
        # ノート番号を振りなおす
        duplicated_self.reload_index()
        # 文字列にする
        s = str(duplicated_self) + '\n'
        # ファイル出力
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s


class Note(UserDict):
    """
    UST内のノート
    """

    def __init__(self, tag: str = '[#INSERT]'):
        super().__init__()
        self['Tag'] = tag
        self.length = 480
        self.notenum = 60
        # 計算用のローカルBPMなどを管理する。
        self._hidden_dict: dict = {'Tempo': None}

    def __str__(self):
        lines = [self['Tag']] + [f'{k}={v}' for (k, v) in self.items() if k != 'Tag']
        return '\n'.join(lines)

    @property
    def tag(self) -> str:
        """
        ノート識別用のタグ
        """
        return self['Tag']

    @tag.setter
    def tag(self, s):
        self['Tag'] = s

    @property
    def intensity(self) -> int:
        """
        音量
        """
        return round(float(self.get('Intensity', 100)))

    @intensity.setter
    def intensity(self, x):
        self['Intensity'] = str(x)

    @property
    def length(self) -> int:
        """
        ノート長[Ticks]
        """
        return int(self['Length'])

    @length.setter
    def length(self, x):
        self['Length'] = str(x)

    @property
    def length_ms(self) -> float:
        """
        ノート長[ms]
        """
        return 125 * float(self['Length']) / self.tempo

    @length_ms.setter
    def length_ms(self, x):
        self['Length'] = str(round(x * self.tempo / 125))

    @property
    def lyric(self) -> str:
        """
        歌詞
        """
        return self['Lyric']

    @lyric.setter
    def lyric(self, x):
        self['Lyric'] = x

    @property
    def notenum(self) -> int:
        """
        音階番号
        """
        return int(self['NoteNum'])

    @notenum.setter
    def notenum(self, x):
        self['NoteNum'] = str(x)

    @property
    def notename(self) -> str:
        """
        音名（C4などの表記）
        """
        return NOTENUM_TO_NOTENAME_DICT[self.notenum]

    @notename.setter
    def notename(self, notename: str):
        self.notenum = NOTENAME_TO_NOTENUM_DICT[str(notename)]

    @property
    def tempo(self) -> float:
        """
        ローカルBPM
        """
        return float(self.get('Tempo', self._hidden_dict['Tempo']))

    @tempo.setter
    def tempo(self, x):
        self['Tempo'] = str(x)

    @property
    def timesignatures(self):
        """
        拍子記号
        """
        return str(self.get('$TimeSignatures', self._hidden_dict['$TimeSignatures']))

    @timesignatures.setter
    def timesignatures(self, x):
        if not TIMESIGNATURES_PATTERN.match(x):
            raise ValueError(
                '拍子情報の表記が不適切です。"(4/4/0)" のように表記してください。'
            )
        self['$TimeSignatures'] = str(x)

    @property
    def pbs(self) -> Optional[Union[list[int], list[float]]]:
        """
        PBS (mode2ピッチ開始位置[ms];ピッチの高さ[cent])

        例) PBS=-104;20.0
        前半だけだったり後半だけだったりする
        """
        # 辞書には文字列で登録してある
        str_pbs = self.get('PBS')
        # PBSがないときはNoneを返す
        if str_pbs is None:
            return None
        if str_pbs == '':
            return None
        # リストに変換
        list_pbs = re.split('[;,]', str_pbs)
        # 2項目目がない場合は0を追加して
        if len(list_pbs) == 1:
            return [float(list_pbs[0]), 0]
        # 2項目め(ピッチ点の高さ)が空欄の場合も0を追加して返す
        if list_pbs[1] == '':
            return [float(list_pbs[0]), 0]
        # 浮動小数のリストに変換して返す
        return list(map(float, list_pbs))

    @pbs.setter
    def pbs(self, list_pbs: Optional[Union[list[int], list[float]]]):
        if list_pbs is None:
            return
        if not 1 <= len(list_pbs) <= 2:
            raise ValueError('pbs must be a list of length 1 or 2.')
        s1 = f'{int(list_pbs[0])};'
        s2 = ','.join(map(str, list_pbs[1:]))
        str_pbs = s1 + s2
        self['PBS'] = str_pbs

    @property
    def pbw(self) -> Optional[Union[list[int], list[float]]]:
        """
        PBW (mode2ピッチ点の間隔[ms]) を取得
        例) PBW=77,163
        """
        # 辞書には文字列で登録してある
        s_pbw = self.get('PBW')
        # PBWがないときはNoneを返す
        if s_pbw is None:
            return None
        if s_pbw == '':
            return None
        # PBW を整数のリストに変換し (空白文字の場合でも対応できるようにしている)
        return [float(x or 0) for x in s_pbw.split(',')]

    @pbw.setter
    def pbw(self, list_pbw: Optional[Union[list[int], list[float]]]):
        if list_pbw is None:
            return
        # リストを整数の文字列に変換
        str_pbw = ','.join(list(map(str, map(float, list_pbw))))
        self['PBW'] = str_pbw

    @property
    def pby(self) -> Optional[list[float]]:
        """
        PBY (mode2ピッチ点の高さ) を取得
        例) PBY=-10.6,0.0
        """
        # 辞書には文字列で登録してある
        s_pby = self.get('PBY')
        # PBYがないとき
        if s_pby is None:
            return None
        if s_pby == '':
            return None
        # PBYの値をリストで返す
        return [float(x or 0) for x in s_pby.split(',')]

    @pby.setter
    def pby(self, list_pby: Optional[Union[list[int], list[float]]]):
        if list_pby is None:
            return
        # リストを小数の文字列に変換
        str_pby = ','.join(list(map(str, map(float, list_pby))))
        self['PBY'] = str_pby

    @property
    def pbm(self, default='') -> Optional[list[str]]:
        """
        PBM (mode2ピッチ点の形状) を取得
        例) PBM=,,,,
        """
        # 辞書には文字列で登録してある
        s_pbm = self.get('PBM')
        # PBMがないとき
        if s_pbm is None:
            return None
        if s_pbm == '':
            return None
        # PBYの値をリストで返す
        return [x or default for x in s_pbm.split(',')]

    @pbm.setter
    def pbm(self, list_pbm: Optional[list[str]]):
        if list_pbm is None:
            return
        # リストを文字列に変換
        str_pbm = ','.join(list_pbm)
        self['PBM'] = str_pbm

    @property
    def velocity(self) -> int:
        """
        子音速度
        """
        return int(self.get('Velocity', 100))

    @velocity.setter
    def velocity(self, x: int):
        self['Velocity'] = int(x)

    @property
    def flag(self) -> str:
        """
        フラグ
        """
        return self.get('Flags', '')

    @flag.setter
    def flag(self, flags: str):
        self['Flags'] = str(flags)

    @property
    def flags(self) -> str:
        """
        フラグ
        """
        return self.get('Flags', '')

    @flags.setter
    def flags(self, flags: str):
        self['Flags'] = str(flags)

    @property
    def label(self) -> str:
        """
        ノートのラベル
        UTAUエディタのピアノロール画面で、ローカルテンポの上に表示されるやつ
        """
        return self.get('Label', '')

    @label.setter
    def label(self, label: str):
        self['Label'] = str(label)

    @property
    def vbr(self) -> str:
        """
        ノートのビブラート情報

        ## 例
        VBR=65,180,35,20,20,0,0
        ## 詳細(8項目)
            - 長さ[%]
            - 周期[ms]
            - 深さ[cent]
            - 入(フェードイン)[%]
            - 出(フェードアウト)[%]
            - 位相[%]
            - 高さ[%]
            - 未使用[-]
        """
        # 辞書には文字列で登録してある
        s_vbr = self.get('VBR')
        # VBRがないとき
        if s_vbr is None:
            return None
        if s_vbr == '':
            return None
        # VBRの値をリストで返す
        return [float(x or 0) for x in s_vbr.split(',')]

    @vbr.setter
    def vbr(self, list_vbr: Optional[Union[list[int], list[float]]]):
        if list_vbr is None:
            return
        if len(list_vbr) != 7 and len(list_vbr) != 8:
            raise ValueError('VBR must be a list of length 7 or 8.')
        # 7項目なら8項目目を0にする
        if len(list_vbr) == 7:
            list_vbr.append(0)
        # リストを小数の文字列に変換
        str_vbr = ','.join(list(map(str, map(float, list_vbr))))
        self['VBR'] = str_vbr

    @property
    def vibrato(self) -> Optional[Union[list[int], list[float]]]:
        """
        ノートのビブラート情報 (vbr のエイリアス)
        """
        return self.vbr

    @vibrato.setter
    def vibrato(self, value: Optional[Union[list[int], list[float]]]):
        self.vbr = value

    # ここからノート操作系-----------------------------------------------------

    def delete(self):
        """選択ノートを削除"""
        self.tag = '[#DELETE]'
        return self

    def insert(self):
        """ノートを挿入(したい)"""
        self.tag = '[#INSERT]'
        return self

    def refresh(self):
        """
        ノートの情報を引き継ぎつつ、自由にいじれるようにする
        UTAUプラグインは値の上書きはできるが削除はできない。
        一旦ノートを削除して新規ノートとして扱う必要がある。
        """
        self.tag = '[#DELETE]\n[#INSERT]'

    def suppin(self):
        """
        ノートの情報を最小限にする
        """
        new_data = {}
        new_data['Tag'] = '[#DELETE]\n[#INSERT]'
        new_data['Lyric'] = self.lyric
        new_data['Length'] = self.length
        new_data['NoteNum'] = self.notenum
        self.data = new_data

    # ここまでノート操作系-----------------------------------------------------


if __name__ == '__main__':
    # 直接実行されたときは ust を読み取って表示する
    print('デフォ子かわいいよデフォ子\n')
    print('ust読み取りテストをします。')
    path = input('ustのパスを入力してください。\n>>> ')
    ust = load(path)
    print(ust)
    input('\nPress Enter to exit.')

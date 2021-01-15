#!/usr/bin/env python3
# Copyright (c) 2020 oatsu
"""
Python3 module for HTS-full-label.
Sinsy仕様のHTSフルコンテキストラベルを扱うモジュール

forループが多いのでpypy3を使っても良いかも。(とくにdeepcopyが重い)
"""
# import json
import re
from collections import UserList
from copy import deepcopy
from decimal import ROUND_HALF_UP, Decimal
from itertools import chain

# from pprint import pprint

# p1を埋めるのに使う。
VOWELS = ('a', 'i', 'u', 'e', 'o', 'A', 'I', 'U', 'E', 'O', 'N', 'ae', 'AE')
BREAKS = ('br', 'cl')
PAUSES = ('pau', 'sil')

# e1を埋めるのに使う
NOTENUM_TO_ABSPITCH_DICT = {
    'xx': 'xx',
    '12': 'C0', '13': 'Db0', '14': 'D0', '15': 'Eb0', '16': 'E0', '17': 'F0',
    '18': 'Gb0', '19': 'G0', '20': 'Ab0', '21': 'A0', '22': 'Bb0', '23': 'B0',
    '24': 'C1', '25': 'Db1', '26': 'D1', '27': 'Eb1', '28': 'E1', '29': 'F1',
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
    '114': 'Gb8', '115': 'G8', '116': 'Ab8', '117': 'A8', '118': 'Bb8', '119': 'B8',
    '120': 'C9', '121': 'Db9', '122': 'D9', '123': 'Eb9', '124': 'E9', '125': 'F9',
    '126': 'Gb9', '127': 'G9',
}
# e57, e58 を埋めるのに使う
ABSPITCH_TO_NOTENUM_DICT = {
    'xx': 'xx',
    'C0': 12, 'Db0': 13, 'D0': 14, 'Eb0': 15, 'E0': 16, 'F0': 17,
    'Gb0': 18, 'G0': 19, 'Ab0': 20, 'A0': 21, 'Bb0': 22, 'B0': 23,
    'C1': 24, 'Db1': 25, 'D1': 26, 'Eb1': 27, 'E1': 28, 'F1': 29,
    'Gb1': 30, 'G1': 31, 'Ab1': 32, 'A1': 33, 'Bb1': 34, 'B1': 35,
    'C2': 36, 'Db2': 37, 'D2': 38, 'Eb2': 39, 'E2': 40, 'F2': 41,
    'Gb2': 42, 'G2': 43, 'Ab2': 44, 'A2': 45, 'Bb2': 46, 'B2': 47,
    'C3': 48, 'Db3': 49, 'D3': 50, 'Eb3': 51, 'E3': 52, 'F3': 53,
    'Gb3': 54, 'G3': 55, 'Ab3': 56, 'A3': 57, 'Bb3': 58, 'B3': 59,
    'C4': 60, 'Db4': 61, 'D4': 62, 'Eb4': 63, 'E4': 64, 'F4': 65,
    'Gb4': 66, 'G4': 67, 'Ab4': 68, 'A4': 69, 'Bb4': 70, 'B4': 71,
    'C5': 72, 'Db5': 73, 'D5': 74, 'Eb5': 75, 'E5': 76, 'F5': 77,
    'Gb5': 78, 'G5': 79, 'Ab5': 80, 'A5': 81, 'Bb5': 82, 'B5': 83,
    'C6': 84, 'Db6': 85, 'D6': 86, 'Eb6': 87, 'E6': 88, 'F6': 89,
    'Gb6': 90, 'G6': 91, 'Ab6': 92, 'A6': 93, 'Bb6': 94, 'B6': 95,
    'C7': 96, 'Db7': 97, 'D7': 98, 'Eb7': 99, 'E7': 100, 'F7': 101,
    'Gb7': 102, 'G7': 103, 'Ab7': 104, 'A7': 105, 'Bb7': 106, 'B7': 107,
    'C8': 108, 'Db8': 109, 'D8': 110, 'Eb8': 111, 'E8': 112, 'F8': 113,
    'Gb8': 114, 'G8': 115, 'Ab8': 116, 'A8': 117, 'Bb8': 118, 'B8': 119,
    'C9': 120, 'Db9': 121, 'D9': 122, 'Eb9': 123, 'E9': 124, 'F9': 125,
    'Gb9': 126, 'G9': 127
}


def load(source):
    """
    HTSフルコンテキストラベル(Sinsy用)を読み取る

    source: path, lines
    """
    song = HTSFullLabel()
    return song.load(source)


def notenum_to_abspitch(notenum) -> str:
    """
    音高をC4のような記法に変換する
    """
    return NOTENUM_TO_ABSPITCH_DICT[str(notenum)]


def abspitch_to_notenum(abspitch: str):
    """
    音高をノート番号に変換する
    """
    return ABSPITCH_TO_NOTENUM_DICT[abspitch]


class HTSFullLabel(UserList):
    """
    HTSのフルコンテキストラベルの1行を扱うクラス
    OneLine からなる list
    [OneLine, OneLine, ..., OneLine]
    """

    def __init__(self, init=None):
        super().__init__(init)
        self.song = Song()

    def write(self, path, mode='w', encoding='utf-8', strict_sinsy_style: bool = True) -> str:
        """
        ファイル出力する
        strict_sinsy_style: bool:
            「休符の長さ」が前後の発声に影響するかどうかを左右する。
            Trueのときは d, f における休符の長さ情報が削除されて 'xx' になる。
            Falseのときは d, f における休符の長さ情報が維持される。
        """
        # 休符周辺の仕様をSinsyに近づける。
        new_label = adjust_pau_contexts(self, strict=strict_sinsy_style)
        # 文字列にする
        s = '\n'.join(list(map(str, new_label)))
        # ファイル出力
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s

    def load(self, source, encoding='utf-8'):
        """
        ファイル、文字列、文字列のリスト、Songオブジェクトのいずれかより値を取得して登録する。
        """
        if isinstance(source, str):
            self._load_from_path(source, encoding=encoding)
            self.generate_songobj()
        elif isinstance(source, Song):
            self._load_from_songobj(source)
            self.fill_contexts_from_songobj()
        elif isinstance(source, list):
            self._load_from_lines(source)
            self.generate_songobj()
        else:
            raise TypeError(f'Type of the argument "source" must be str, list or {Song}.')
        return self

    def _load_from_path(self, path, encoding: str = 'utf-8'):
        """
        ファイルをもとに値を登録する。
        """
        # パスに半角スペースが入っている場合に出現する引用符を除去
        path = path.strip('"')
        # ファイルを読み取って行のリストにする
        try:
            with open(path, mode='r', encoding=encoding) as f:
                lines = [line.rstrip('\r\n') for line in f.readlines()]
        except UnicodeDecodeError:
            with open(path, mode='r', encoding='sjis') as f:
                lines = [line.rstrip('\r\n') for line in f.readlines()]
        # 行ごとに分割したリストをもとに情報を登録する。
        self._load_from_lines(lines)
        return self

    def _load_from_lines(self, lines: list):
        """
        文字列のリスト(行のリスト)をもとに値を登録する。
        """
        # 各行を解析してHTSFullLabelに追加する。
        for line in lines:
            # 1行分の情報用のオブジェクトを生成
            ol = OneLine()
            # 正規表現で上手く区切れない文字を置換する
            # 空白で分割して、時刻情報とそれ以外のコンテキストに分ける
            line_split = line.split(maxsplit=2)
            ol.start = int(line_split[0])
            ol.end = int(line_split[1])
            str_contexts = line_split[2]
            # コンテキスト文字列を /A: などの文字列で区切って一次元リストにする
            l_contexts = re.split('/.:', str_contexts)
            # 特定の文字でさらに区切って二次元リストにする
            sep = re.escape('=+-~∼!@#$%^ˆ&;_|[]')
            l_contexts_2d = [re.split((f'[{sep}]'), s) for s in l_contexts]
            # 1行分の情報用のオブジェクトに、各種コンテキストを登録する
            ol.p, ol.a, ol.b, ol.c, ol.d, ol.e, ol.f, ol.g, ol.h, ol.i, ol.j = l_contexts_2d
            # 1行分の情報用のオブジェクトを HTSFullLabel オブジェクトに追加する。
            self.append(ol)
        return self

    def _load_from_songobj(self, songobj: list):
        """
        hts.Song オブジェクトをもとにコンテキストを登録する。
        """
        self.song = songobj
        return self

    def fill_contexts_from_songobj(self):
        """
        自身が持つSongオブジェクトをもとにコンテキスト情報を埋める。
        """
        song = self.song
        dummy_note = Note()
        dummy_syllable = Syllable()
        dummy_syllable.append(Phoneme())
        dummy_note.append(dummy_syllable)

        notes = [dummy_note] + song + [deepcopy(dummy_note)]

        onelines = []
        for i_n, note in enumerate(notes[1:-1], 1):
            syllables = notes[i_n - 1] + note + notes[i_n + 1]
            for i_s, syllable in enumerate(syllables[1:-1], 1):
                for phoneme in syllable:
                    ol = OneLine()
                    # ノート情報を登録
                    ol.previous_note = notes[i_n - 1]
                    ol.note = note
                    ol.next_note = notes[i_n + 1]
                    # 音節情報を登録
                    ol.previous_syllable = syllables[i_s - 1]
                    ol.syllable = syllable
                    ol.next_syllable = syllables[i_s + 1]
                    # 音素情報を登録(現在の音素のみ)
                    ol.phoneme = phoneme
                    # 楽曲情報を登録
                    ol.song = song
                    # print(list(map(id, [song, note, syllable, phoneme])))
                    onelines.append(ol)
        self.data = onelines
        self.fill_phonemes()
        return self

    def fill_phonemes(self):
        """
        phoneme をもとに、前後の音素に関する項を埋める。
        """
        extended_self = [OneLine(), OneLine()] + self.data + [OneLine(), OneLine()]
        # ol is OneLine objec
        for i, ol in enumerate(extended_self[2:-2], 2):
            ol.before_previous_phoneme = extended_self[i - 2].phoneme
            ol.previous_phoneme = extended_self[i - 1].phoneme
            ol.next_phoneme = extended_self[i + 1].phoneme
            ol.after_next_phoneme = extended_self[i + 2].phoneme
        return self

    def generate_songobj(self):
        """
        フルコンテキストラベルの情報をもとにSongオブジェクトをつくる。
        self.song に格納する。
        """
        # Song は1つの HTSFullLabel につき1つだけなので、ループする必要がない。
        # Song は一番最初の行の情報がすべての行に通用すると考える。
        song = self[0].song
        song.data = []
        note = Note()
        syllable = Syllable()
        for ol in self:
            phoneme = ol.phoneme
            # すでに入っている音節や音素を取り除く。取り除かないと数が倍になる。
            ol.note.data = []
            ol.syllable.data = []
            # 処理する行が「ノート内で1番最初の音節」かつ
            # 「音節内でいちばん最初の音素」のとき、ノートを切り替える。
            if str(ol.syllable.position) == '1' and str(phoneme.position) == '1':
                note = ol.note
                song.append(note)
            # 処理する行が「音節内で1番最初の音素」なとき、音節を切り替える。
            if str(phoneme.position) == '1':
                syllable = ol.syllable
                note.append(syllable)
            syllable.append(phoneme)

        song.autofill()
        self.song = song
        self.fill_contexts_from_songobj()


class OneLine:
    """
    HTSのフルコンテキストラベルの1行を扱うクラス
    ファイルを読み取って HTSFullLabel を生成するときと、
    HTSFullLabel をファイル入出力するときに使う。
    """

    def __init__(self):
        self.before_previous_phoneme = Phoneme()
        self.previous_phoneme = Phoneme()
        self.phoneme = Phoneme()
        self.next_phoneme = Phoneme()
        self.after_next_phoneme = Phoneme()
        self.previous_syllable = Syllable()
        self.syllable = Syllable()
        self.next_syllable = Syllable()
        self.previous_note = Note()
        self.note = Note()
        self.next_note = Note()
        self.previous_phrase = Phrase()
        self.phrase = Phrase()
        self.next_phrase = Phrase()
        self.song = Song()

    def __str__(self):
        str_self = ''.join((
            f'{self.start} {self.end} ',
            # Phoneme 関連
            '{}@{}^{}-{}+{}={}_{}%{}^{}_{}~{}-{}!{}[{}${}]{}'
            .format(*self.p),
            # Syllable 関連
            '/A:{}-{}-{}@{}~{}'.format(*self.a),
            '/B:{}_{}_{}@{}|{}'.format(*self.b),
            '/C:{}+{}+{}@{}&{}'.format(*self.c),
            # Note 関連
            '/D:{}!{}#{}${}%{}|{}&{};{}-{}'.format(*self.d),
            '/E:{}]{}^{}={}~{}!{}@{}#{}+{}]{}${}|{}[{}&{}]{}={}^{}~{}#{}_{};{}${}&{}%{}[{}|{}]{}-{}^{}+{}~{}={}@{}${}!{}%{}#{}|{}|{}-{}&{}&{}+{}[{};{}]{};{}~{}~{}^{}^{}@{}[{}#{}={}!{}~{}+{}!{}^{}' \
            .format(*self.e),
            '/F:{}#{}#{}-{}${}${}+{}%{};{}'.format(*self.f),
            # Phrase 関連
            '/G:{}_{}'.format(*self.g),
            '/H:{}_{}'.format(*self.h),
            '/I:{}_{}'.format(*self.i),
            # Song 関連
            '/J:{}~{}@{}'.format(*self.j)
        ))
        return str_self

    @property
    def start(self) -> int:
        """
        発声開始時刻
        """
        return int(self.phoneme.start)

    @start.setter
    def start(self, start_time: int):
        self.phoneme.start = start_time

    @property
    def end(self) -> int:
        """
        発声終了時刻
        """
        return int(self.phoneme.end)

    @end.setter
    def end(self, end_time: int):
        self.phoneme.end = end_time

    @property
    def p(self) -> list:
        """
        音素に関するコンテキスト
        """
        p = [
            self.phoneme.language_independent_identity,
            self.before_previous_phoneme.identity,
            self.previous_phoneme.identity,
            self.phoneme.identity,
            self.next_phoneme.identity,
            self.after_next_phoneme.identity,
            self.before_previous_phoneme.flag,
            self.previous_phoneme.flag,
            self.phoneme.flag,
            self.next_phoneme.flag,
            self.after_next_phoneme.flag,
            self.phoneme.position,
            self.phoneme.position_backward,
            self.phoneme.distance_from_previous_vowel,
            self.phoneme.distance_to_next_vowel,
            self.phoneme.undefined_context
        ]
        return p

    @p.setter
    def p(self, phoneme_contexts: list):
        (self.phoneme.language_independent_identity,
         self.before_previous_phoneme.identity,
         self.previous_phoneme.identity,
         self.phoneme.identity,
         self.next_phoneme.identity,
         self.after_next_phoneme.identity,
         self.before_previous_phoneme.flag,
         self.previous_phoneme.flag,
         self.phoneme.flag,
         self.next_phoneme.flag,
         self.after_next_phoneme.flag,
         self.phoneme.position,
         self.phoneme.position_backward,
         self.phoneme.distance_from_previous_vowel,
         self.phoneme.distance_to_next_vowel,
         self.phoneme.undefined_context
         ) = phoneme_contexts[0:16]

    @property
    def a(self) -> list:
        """
        直前の音節のコンテキスト
        """
        return self.previous_syllable.contexts

    @a.setter
    def a(self, syllable_contexts: list):
        self.previous_syllable.contexts = syllable_contexts

    @property
    def b(self) -> list:
        """
        現在の音節のコンテキスト
        """
        return self.syllable.contexts

    @b.setter
    def b(self, syllable_contexts: list):
        self.syllable.contexts = syllable_contexts

    @property
    def c(self) -> list:
        """
        直後の音節のコンテキスト
        """
        return self.next_syllable.contexts

    @c.setter
    def c(self, syllable_contexts: list):
        self.next_syllable.contexts = syllable_contexts

    @property
    def d(self) -> list:
        """
        直前のノートのコンテキスト
        """
        return self.previous_note.contexts

    @d.setter
    def d(self, note_contexts: list):
        self.previous_note.contexts = note_contexts

    @property
    def e(self) -> list:
        """
        現在のノートのコンテキスト
        """
        return self.note.contexts

    @e.setter
    def e(self, note_contexts: list):
        self.note.contexts = note_contexts

    @property
    def f(self) -> list:
        """
        直後のノートのコンテキスト
        """
        return self.next_note.contexts

    @f.setter
    def f(self, note_contexts: list):
        self.next_note.contexts = note_contexts

    @property
    def g(self) -> list:
        """
        直前のフレーズのコンテキスト
        """
        return self.previous_phrase.contexts

    @g.setter
    def g(self, phrase_contexts: list):
        self.previous_phrase.contexts = phrase_contexts

    @property
    def h(self) -> list:
        """
        現在のフレーズのコンテキスト
        """
        return self.phrase.contexts

    @h.setter
    def h(self, phrase_contexts: list):
        self.phrase.contexts = phrase_contexts

    @property
    def i(self) -> list:
        """
        直後のフレーズのコンテキスト
        """
        return self.next_phrase.contexts

    @i.setter
    def i(self, phrase_contexts: list):
        self.next_phrase.contexts = phrase_contexts

    @property
    def j(self) -> list:
        """
        (現在の)楽曲のコンテキスト
        1ファイル1曲。
        """
        return self.song.contexts

    @j.setter
    def j(self, song_contexts: list):
        self.song.contexts = song_contexts


class Song(UserList):
    """
    曲を扱うクラス
    今日の曲(j1-j3)
    [Phrase, Phrase, ..., Phrase]
    [Note, Note, ..., Note]
    """

    def __init__(self, init=None):
        super().__init__(init)
        self.contexts = ['xx'] * 3
        self.number_of_measures = 'xx'

    # @property
    # def all_phrases(self):
    #     """
    #     Phraseをすべて並べたリストを返す。
    #     """
    #     return self

    @property
    def all_notes(self):
        """
        Noteをすべて並べたリストを返す。
        """
        return self.data

    @property
    def all_syllables(self):
        """
        Syllableをすべて並べたリストを返す。
        """
        return list(chain.from_iterable(self.all_notes))

    @property
    def all_phonemes(self):
        """
        Phonemeをすべて並べたリストを返す。
        """
        return list(chain.from_iterable(self.all_syllables))

    @property
    def number_of_phrases(self):
        """
        楽曲内のフレーズ数。(j3)
        """
        return self.contexts[2]

    @number_of_phrases.setter
    def number_of_phrases(self, number: int):
        self.contexts[2] = number

    def write(self, path, mode='w', encoding='utf-8', strict_sinsy_style: bool = True
              ) -> HTSFullLabel:
        """
        ファイル出力する。
        HTSFullLabelからではなく、USTなどからSongが直接生成されている場合に対応する。
        """
        full_label = HTSFullLabel()
        full_label.song = self
        full_label.fill_contexts_from_songobj()
        full_label.write(
            path, mode=mode, encoding=encoding, strict_sinsy_style=strict_sinsy_style
        )
        return full_label

    def reset_time(self):
        """
        ノート長をもとに、Sinsyの出力と同じになるように、
        Phonemeオブジェクトのstartとendを計算して登録する。

        単位は100ns
        100ns単位での長さがすでに計算されているものとする。(note.length_100ns)
        """
        t_start = 0
        t_end = 0
        for note in self.all_notes:
            phonemes_in_note = tuple(chain.from_iterable(note))
            t_end += note.length_100ns
            for phoneme in phonemes_in_note:
                phoneme.start = Decimal(t_start).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                phoneme.end = Decimal(t_end).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
            t_start = t_end

    def autofill(self):
        """
        自動補完可能なものをすべて自動補完する。
        """
        # この順でやらないと、p1が未設定の状態で Note.is_pau() をやってしまう
        self._fill_phoneme_contexts()
        self._fill_syllable_contexts()
        self._fill_note_contexts()
        self._fill_song_contexts()

    def _fill_phoneme_contexts(self, vowels=VOWELS, pauses=PAUSES, breaks=BREAKS):
        """
        p1, p12, p13, p14, p15 を補完する。
        """
        # p1 を埋める
        for phoneme in self.all_phonemes:
            phoneme_identity = phoneme.identity
            if phoneme_identity == 'xx':
                phoneme.language_independent_identity = 'xx'
            elif phoneme_identity in vowels:
                phoneme.language_independent_identity = 'v'
            elif phoneme_identity in pauses:
                phoneme.language_independent_identity = 'p'
            elif phoneme_identity in breaks:
                phoneme.language_independent_identity = 'b'
            else:
                phoneme.language_independent_identity = 'c'
        # p12, p13, p14, p15を埋める
        self._fill_p12_p13()
        self._fill_p14_p15()

    def _fill_p12_p13(self):
        """
        p12 と p13 (音節内での位置) を補完する。
        """
        for syllable in self.all_syllables:
            len_syllable = len(syllable)
            for i, phoneme in enumerate(syllable):
                # p12
                phoneme.position = i + 1
                # p13
                phoneme.position_backward = len_syllable - i

    def _fill_p14_p15(self):
        """
        p14 と p15 (母音からの距離) を補完する。
        """
        # p14
        for syllable in self.all_syllables:
            distance = None
            for phoneme in syllable:
                if phoneme.is_vowel():
                    phoneme.distance_from_previous_vowel = 'xx'
                    distance = 1
                elif distance is None:
                    continue
                elif phoneme.is_consonant():
                    phoneme.distance_from_previous_vowel = distance
                    distance += 1
                # 母音でも子音でもない場合(clとか)
                else:
                    distance += 1
        # p15
        for syllable in self.all_syllables:
            distance = None
            for phoneme in reversed(syllable):
                if phoneme.is_vowel():
                    phoneme.distance_to_next_vowel = 'xx'
                    distance = 1
                elif distance is None:
                    continue
                elif phoneme.is_consonant():
                    phoneme.distance_to_next_vowel = distance
                    distance += 1
                # 母音でも子音でもない場合(clとか)
                else:
                    distance += 1

    def _fill_syllable_contexts(self):
        """
        b1, b2, b3 を補完する。
        """
        for note in self.all_notes:
            len_note = len(note)
            for i, syllable in enumerate(note):
                # b1
                syllable.number_of_phonemes = len(syllable)
                # b2
                syllable.position = i + 1
                # b3
                syllable.position_backward = len_note - i

    def _fill_note_contexts(self):
        """
        e を補完する。

        必要なデータ:
            - e1: 絶対音高
            - e5: テンポ
            - e8: ノート長(96分音符)
        補完するデータ:
            - e6: ノート内音節数
            - e7: ノート長(10ms)
            - e18-e25: フレーズ内での位置
                - e20, e21: フレーズ内での位置(100ms)
                - e22, e23: フレーズ内での位置(96分音符)
                - e24, e25: フレーズ内での位置(パーセント)
            - Note.position_100ns
            - Note.position_100ns_backward
            - e57-e58: 前後のノートとの音高差
        """
        # e6, e7 を埋める。
        for note in self.all_notes:
            # e6 (ノート内音節数) を埋める
            note.number_of_syllables = len(note)
            # e8 の情報をもとに e7 を埋める。テンポ情報(e5)がないと困る。
            # 100ns単位での長さも登録する。
            if note.tempo != 'xx' and note.length != 'xx':
                note.length_10ms = Decimal(note.length_100ns / 100000
                                           ).quantize(Decimal('0'), rounding=ROUND_HALF_UP)

        # フレーズ内で何番目のノートかを埋める
        self._fill_e18_e19()
        # フレーズ内での 96分音符単位での位置を埋める。e18,e19が必要。
        self._fill_e22_e23()
        # フレーズ内での 100ms単位での位置を埋める。e18,e19が必要。
        # フレーズ内での 100ns単位での位置も埋める(utaupy独自コンテキスト)。
        self._fill_e20_e21_100ns()
        # フレーズ内での パーセント表記での位置を埋める。e18, e19, 100ns位置が必要
        self._fill_e24_e25()
        # 音高の前後変化を埋める
        self._fill_e57_e58()

    def _fill_e18_e19(self):
        """
        「Phrase内で何番目か(e18, e19)」の項を埋める。
        Phraseの扱いは難しいので、「休符からの距離」を代わりに用いる。
        """
        counter = 'xx'
        # 直前の休符からの距離を数える
        for note in self.all_notes:
            # 休符のときは距離をリセット
            if note.is_pau():
                note.position = 'xx'
                counter = 0
            # 休符ではないけれど休符位置が分からないときは未登録のまま
            elif counter == 'xx':
                continue
            # 休符ではなく、休符位置が分かっているときは登録
            else:
                counter += 1
                note.position = counter
        # 次の休符までの距離を登録する。
        for note in reversed(self.all_notes):
            if note.is_pau():
                note.position_backward = 'xx'
                counter = 0
            elif counter == 'xx':
                continue
            else:
                counter += 1
                note.position_backward = counter

    def _fill_e20_e21_100ns(self):
        """
        「フレーズ内での位置(100ms単位での表記) (e20, e21)」の項を埋める。

        e18とe19のデータがある前提で実行する。
        10msでの累計だとずれるので100nsで計算してから10msに直して登録する。
        """

        counter_100ns = 0

        # 前の休符から数えた時間を登録する。
        for note in self.all_notes:
            # 休符のときは 'xx'
            if note.position == 'xx':
                note.position_100ms = 'xx'
                note.position_100ns = None
                counter_100ns = 0
            # フレーズ中で最初のノートのときは時間をリセットして、累積時間を増やす。
            elif note.position == 1:
                note.position_100ms = 0
                note.position_100ns = 0
                counter_100ns += note.length_100ns
            # 休符でもなくて最初のノートでもないとき
            else:
                note.position_100ms = \
                    Decimal(counter_100ns / 1000000).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                note.position_100ns = counter_100ns
                counter_100ns += note.length_100ns

        counter_100ns = 0
        # 次の休符から数えた時間を登録する。
        for note in reversed(self.all_notes):
            # 休符のときは 'xx'
            if note.position_backward == 'xx':
                counter_100ns = 0
                note.position_100ms_backward = 'xx'
                note.position_100ns_backward = None
            # フレーズ中で最後のノートのときは時間をリセットして、累積時間を増やす。
            elif note.position_backward == 1:
                counter_100ns = note.length_100ns
                note.position_100ms_backward = \
                    Decimal(counter_100ns / 1000000).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                note.position_100ns_backward = counter_100ns
            # 休符でもなくて最後のノートでもないとき
            else:
                counter_100ns += note.length_100ns
                note.position_100ms_backward = \
                    Decimal(counter_100ns / 1000000).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                note.position_100ns_backward = counter_100ns

    def _fill_e22_e23(self):
        """
        「フレーズ内での位置(96分音符単位) (e22, e23)」の項を埋める。
        e18とe19のデータがある前提で実行する。
        """
        counter = 0
        # 前の休符から数えた時間を登録する。
        for note in self.all_notes:
            # 休符のときは 'xx'
            if note.position == 'xx':
                note.contexts[21] = 'xx'
                counter = 0
            # フレーズ中で最初のノートのときは時間をリセットして、累積時間を増やす。
            elif note.position == 1:
                note.contexts[21] = 0
                counter += int(note.length)
            # 休符でもなくて最初のノートでもないとき
            else:
                note.contexts[21] = counter
                counter += int(note.length)

        counter = 0
        # 次の休符から数えた時間を登録する。
        for note in reversed(self.all_notes):
            # 休符のときは 'xx'
            if note.position_backward == 'xx':
                counter = 0
                note.contexts[22] = 'xx'
            # フレーズ中で最後のノートのときは時間をリセットして、累積時間を増やす。
            elif note.position_backward == 1:
                counter = int(note.length)
                note.contexts[22] = counter
            # 休符でもなくて最後のノートでもないときは普通に登録して、累積時間を増やす。
            else:
                counter += int(note.length)
                note.contexts[22] = counter

    def _fill_e24_e25(self):
        """
        「フレーズ内での位置(パーセント表記) (e24, e25)」の項を埋める。
        e18, e19, length_100ns のデータがある前提で実行する。
        """
        # フレーズの全体の長さ
        phrase_length_100ns = 0
        counter_100ns = 0
        for note in self.all_notes:
            if note.position == 'xx':
                phrase_length_100ns = 0
                counter_100ns = 0
                note.contexts[23] = 'xx'
            elif note.position == 1:
                phrase_length_100ns = note.position_100ns_backward
                note.contexts[23] = Decimal(100 * counter_100ns / phrase_length_100ns
                                            ).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                counter_100ns += note.length_100ns
            else:
                note.contexts[23] = Decimal(100 * counter_100ns / phrase_length_100ns
                                            ).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                counter_100ns += note.length_100ns

        # フレーズの全体の長さ
        phrase_length_100ns = 0
        counter_100ns = 0
        for note in reversed(self.all_notes):
            # 休符のときは 'xx'
            if note.position_backward == 'xx':
                phrase_length = 0
                counter_100ns = 0
                note.contexts[24] = 'xx'
            # フレーズ中で最後のノートのときは時間をリセットして、累積時間を増やす。
            elif note.position_backward == 1:
                phrase_length = note.position_100ns + note.length_100ns
                counter_100ns = note.length_100ns
                note.contexts[24] = Decimal(100 * counter_100ns / phrase_length
                                            ).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
            # 休符でもなくて最後のノートでもないときは普通に登録して、累積時間を増やす。
            else:
                counter_100ns += note.length_100ns
                note.contexts[24] = Decimal(100 * counter_100ns / phrase_length
                                            ).quantize(Decimal('0'), rounding=ROUND_HALF_UP)

    def _fill_e57_e58(self):
        """
        「前後のノートとの音高差 (e57, e58)」の項を埋める。
        e1がある前提で実行する。
        休符が入ると死ぬw
        """
        notes = self.all_notes
        # e57を埋める
        for i, note in enumerate(notes[1:], 1):
            previous_note = notes[i - 1]
            previous_abspitch = previous_note.absolute_pitch
            current_abspitch = note.absolute_pitch
            # 直前のノートまたは今のノートが休符のときはスキップ
            if (previous_note.is_pau() or note.is_pau()):
                note.contexts[56] = 'xx'
                continue
            # 直前のノートも今のノートも音符のとき
            previous_notenum = abspitch_to_notenum(previous_abspitch)
            current_notenum = abspitch_to_notenum(current_abspitch)
            pitch_difference = previous_notenum - current_notenum
            note.contexts[56] = f'{"p" if pitch_difference >= 0 else "m"}{abs(pitch_difference)}'

        # e58 を埋める
        # 処理内容を比較しやすいようにprevious_noteにしているが、実際はnext_note
        for i, note in enumerate(reversed(notes[:-1]), 1):
            previous_note = notes[-i]
            previous_abspitch = previous_note.absolute_pitch
            current_abspitch = note.absolute_pitch
            # 直後のノートまたは今のノートが休符のときはスキップ
            if (previous_note.is_pau() or note.is_pau()):
                note.contexts[57] = 'xx'
                continue
            # 直前のノートも今のノートも音符のとき
            previous_notenum = abspitch_to_notenum(previous_abspitch)
            current_notenum = abspitch_to_notenum(current_abspitch)
            pitch_difference = previous_notenum - current_notenum
            note.contexts[57] = f'{"p" if pitch_difference >= 0 else "m"}{abs(pitch_difference)}'

    def _fill_song_contexts(self):
        """
        Songオブジェクトのコンテキストを自動補完する。
        """
        self.fill_j3()

    def fill_j3(self):
        """
        Songオブジェクト内のフレーズ数(j3) の項を埋める。
        """
        notes = self.all_notes
        previous_note_is_pau = notes[0].is_pau()

        counter = 0
        # 最初が音符だった時はフレーズ数1からスタート
        if not previous_note_is_pau:
            counter = +1
        # 休符→音符 の並びの回数を検出する。
        for note in notes[1:]:
            current_note_is_pau = note.is_pau()
            if previous_note_is_pau and not current_note_is_pau:
                counter += 1
            previous_note_is_pau = current_note_is_pau
        self.number_of_phrases = counter


class Phrase(UserList):
    """
    フレーズを扱うクラス
    昨日のフレーズ G (g1~g2)
    今日のフレーズ H (h1~h2)
    明日のフレーズ I (i1~i2)
    基本的にはHのみを操作する。
    [Note, Note, Note, ..., Note]
    """

    def __init__(self, init=None):
        super().__init__(init)
        self.contexts = ['xx'] * 2

    @property
    def number_of_syllables(self):
        """
        フレーズ内の音節数。

        OneLine からSongを生成するときに使うかも。
        フレーズの切り替わり判定をするときに使うかも。
        多分使わない。
        """
        return self.contexts[0]

    @number_of_syllables.setter
    def number_of_syllables(self, number):
        self.contexts[0] = number

    @property
    def number_of_phonemes(self):
        """
        フレーズ内の音素数。
        OneLine からSongを生成するときに使う。
        """
        return self.contexts[1]

    @number_of_phonemes.setter
    def number_of_phonemes(self, number):
        self.contexts[1] = number


class Note(UserList):
    """
    ノートまたは休符を扱うクラス
    1ノート（ノートと休符）を扱うクラス
    昨日のノート D (d1~d5)
    今日のノート E (e1~e60)
    明日のノート F (f1~f5)
    基本的にはEのみを操作する。
    [Syllable, Syllable, ..., Syllable]
    """

    def __init__(self, init=None):
        super().__init__(init)
        self.contexts = ['xx'] * 60
        self.position_100ns: int = None
        self.position_100ns_backward: int = None

    @property
    def absolute_pitch(self):
        """
        ノートの絶対音高 (C0-G9) (e1)
        # TODO: 番号でもsetできるようにする。
        """
        return self.contexts[0]

    @absolute_pitch.setter
    def absolute_pitch(
            self, absolute_pitch: str = None, notenum: int = None):
        """
        absolute_pitch: C0-G9 のような表記
        notenum: MIDIなどの note number による表記(C-1:0 ~ G9:127)
        """
        # どちらか片方は必須だし、
        # 片方しか利用できませんよというやつ
        assert not (absolute_pitch is None) == (notenum is None)
        if absolute_pitch is not None:
            self.contexts[0] = absolute_pitch
        else:
            self.contexts[0] = notenum_to_abspitch(notenum)

    @property
    def relative_pitch(self) -> int:
        """
        ノートの相対音高(p2)
        """
        return self.contexts[1]

    @relative_pitch.setter
    def relative_pitch(self, relative_pitch: int):
        self.contexts[1] = relative_pitch

    @property
    def key(self):
        """
        ノートのキー(p3)
        """
        return self.contexts[2]

    @key.setter
    def key(self, key: int):
        self.contexts[2] = key

    @property
    def beat(self):
        """
        拍子情報(p4)
        3/4 とか 4/4 とか 6/8 とか
        """
        return self.contexts[3]

    @beat.setter
    def beat(self, beat: str):
        self.contexts[3] = str(beat)

    @property
    def notenum(self):
        """
        音高をノート番号で取得する
        ラベルファイルには記録されないが、
        C4のような表記でe1に記録される。
        """
        return abspitch_to_notenum(self.absolute_pitch)

    @notenum.setter
    def notenum(self, notenum):
        self.absolute_pitch = notenum_to_abspitch(notenum)

    @property
    def tempo(self):
        """
        テンポ(e5)
        """
        return self.contexts[4]

    @tempo.setter
    def tempo(self, tempo: int):
        self.contexts[4] = tempo

    @property
    def number_of_syllables(self):
        """
        ノート内音節数(e6)
        """
        return self.contexts[5]

    @number_of_syllables.setter
    def number_of_syllables(self, number: int):
        self.contexts[5] = number

    @property
    def length_10ms(self):
        """
        ノート長(e7)
        10ms単位の整数で計算
        """
        return self.contexts[6]

    @length_10ms.setter
    def length_10ms(self, length: int):
        self.contexts[6] = length

    @property
    def length(self):
        """
        ノート長(e8)
        96分音符いくつ分かで計算
        """
        return self.contexts[7]

    @length.setter
    def length(self, length: int):
        self.contexts[7] = length

    @property
    def length_100ns(self):
        """
        ノート長(ラベル出力なし)
        100ns単位の整数で計算
        """
        if 'xx' in (self.tempo, self.length):
            return 'xx'
        return float(25000000 * int(self.length) / int(self.tempo))

    @property
    def position(self):
        """
        フレーズ内での位置(e18)
        """
        return self.contexts[17]

    @position.setter
    def position(self, position: int):
        self.contexts[17] = position

    @property
    def position_backward(self):
        """
        フレーズ内での後ろから数えた位置(e19)
        1-indexed
        """
        return self.contexts[18]

    @position_backward.setter
    def position_backward(self, position_backward: int):
        self.contexts[18] = position_backward

    @property
    def position_100ms(self):
        """
        フレーズ内での位置(e20)
        100ms単位
        """
        return self.contexts[19]

    @position_100ms.setter
    def position_100ms(self, position: int):
        self.contexts[19] = position

    @property
    def position_100ms_backward(self):
        """
        フレーズ内での後ろから数えた位置(e21)
        100ms単位
        """
        return self.contexts[20]

    @position_100ms_backward.setter
    def position_100ms_backward(self, position_backward: int):
        self.contexts[20] = position_backward

    def is_pau(self):
        """
        休符かどうかを返す
        ノート内の最初の音素が休符かどうかで判断する
        """
        return self[0][0].is_pau()


class Syllable(UserList):
    """
    1音節を扱うクラス
    昨日の音節 A (a1~a5)
    今日の音節 B (b1~b5)
    明日の音節 C (c1~c5)
    [Phoneme, Phoneme, ..., Phoneme]
    """

    def __init__(self, init=None):
        super().__init__(init)
        self.contexts = ['xx'] * 5

    @property
    def number_of_phonemes(self):
        """
        音節内の音素数(b1)
        """
        return self.contexts[0]

    @number_of_phonemes.setter
    def number_of_phonemes(self, number: int):
        self.contexts[0] = number

    @property
    def position(self):
        """
        ノート内での位置(b2)
        1-indexed
        """
        return self.contexts[1]

    @position.setter
    def position(self, position: int):
        self.contexts[1] = position

    @property
    def position_backward(self):
        """

        ノート内での後ろから数えた位置(b3)
        1-indexed
        """
        return self.contexts[2]

    @position_backward.setter
    def position_backward(self, position_backward: int):
        self.contexts[2] = position_backward


class Phoneme:
    """
    音素を扱うクラス
    p1~p16
    """

    def __init__(self):
        # 発声開始時刻
        self.start: int = 0
        # 発声終了時刻
        self.end: int = 0
        # p1: 言語非依存の音素記号(p, c, v など)
        self.language_independent_identity: str = 'xx'
        # p4: 音素記号
        self.identity: str = 'xx'
        # p9: フラグ
        self.flag: str = 'xx'
        # p12: 音節(Syllable)内の、先頭から数えた位置
        self.position: int = 'xx'
        # p13: 音節(Syllable)内の、末尾から数えた位置
        self.position_backward: int = 'xx'
        # p14: 今が子音のときのみに定義される、直前の母音からの距離
        self.distance_from_previous_vowel: int = 'xx'
        # p15: 今が子音のときのみに定義される、直後の母音までの距離
        self.distance_to_next_vowel: int = 'xx'
        # 未定義のコンテキスト
        self.undefined_context = 'xx'

    def __str__(self):
        return f'{self.start} {self.end} {self.identity}'

    def is_vowel(self):
        """
        母音かどうか
        """
        return self.language_independent_identity == 'v'

    def is_consonant(self):
        """
        子音かどうか
        """
        return self.language_independent_identity == 'c'

    def is_pau(self):
        """
        休符かどうか
        """
        return self.language_independent_identity == 'p'

    def is_break(self):
        """
        息継ぎかどうか
        """
        return self.language_independent_identity == 'b'


def adjust_pau_contexts(full_label: HTSFullLabel, strict: bool = True) -> HTSFullLabel:
    """
    出力用に休符まわりの音節コンテキストを調整する。
    """
    # deepcopyが深く、できるだけSinsyの出力に近づける。でも遅い。
    if strict:
        new_label = HTSFullLabel()
        # NOTE: ここのdeepcopyめっちゃ遅い
        new_label.data = [deepcopy(ol) for ol in full_label]
        # 前の音節とノートに関する処理
        for ol in new_label[1:]:
            if ol.previous_syllable[0].identity in ('pau', 'sil'):
                ol.a[0:3] = ['xx'] * 3
            if ol.previous_note.is_pau():
                ol.d[0:3] = ['xx'] * 3
                ol.d[3:8] = ['xx'] * 5
        # 現在の音節とノートに関する処理
        for ol in new_label:
            if ol.note.is_pau():
                ol.e[0:2] = ['xx'] * 2
        # 次の音節とノートに関する処理
        for ol in new_label[:-1]:
            if ol.next_syllable[0].identity in ('pau', 'sil'):
                ol.c[0:3] = ['xx'] * 3
            if ol.next_note.is_pau():
                ol.f[0:3] = ['xx'] * 3
                ol.f[3:8] = ['xx'] * 5

    # deepcopyが浅く処理が速い。ただし、Sinsyの出力と差異が生じてしまう。
    else:
        new_label = deepcopy(full_label)
        for ol in new_label:
            if ol.note.is_pau():
                ol.b[0:3] = ['xx'] * 3
                ol.e[0:3] = ['xx'] * 3

    return new_label


def main():
    """
    直接実行された時にやるやつ
    """
    path_hts_in = input('path_hts_in: ')
    label = load(path_hts_in)
    label.song.autofill()
    label.song.reset_time()
    path_hts_out = path_hts_in.replace('.lab', '_utaupy.lab')
    label.write(path_hts_out)


if __name__ == '__main__':
    main()

#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
Python3 module for HTS-full-label.
Sinsy仕様のHTSフルコンテキストラベルを扱うモジュール
"""

# import json
import re
from collections import UserList
from copy import deepcopy
from itertools import chain

# from pprint import pprint


def load(source):
    """
    HTSフルコンテキストラベル(Sinsy用)を読み取る

    source: path, lines
    """
    song = HTSFullLabel()
    return song.load(source)


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
        new_label = adjust_syllables_to_sinsy(self)
        new_label = adjust_notes_to_sinsy(new_label, strict=strict_sinsy_style)
        # 文字列にする
        s = '\n'.join([str(oneline) for oneline in new_label])
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
        elif isinstance(source, Song):
            self._load_from_songobj(source)
        elif isinstance(source, list):
            self._load_from_lines(source)
        else:
            raise TypeError(f'Type of the argument "source" must be str, list or {Song}.')
        self.generate_songobj()
        self.fill_contexts_from_songobj()
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
            oneline = OneLine()
            # 正規表現で上手く区切れない文字を置換する
            # 空白で分割して、時刻情報とそれ以外のコンテキストに分ける
            line_split = line.split(maxsplit=2)
            oneline.start = int(line_split[0])
            oneline.end = int(line_split[1])
            str_contexts = line_split[2]
            # コンテキスト文字列を /A: などの文字列で区切って一次元リストにする
            l_contexts = re.split('/.:', str_contexts)
            # 特定の文字でさらに区切って二次元リストにする
            sep = re.escape('=+-~∼!@#$%^ˆ&;_|[]')
            l_contexts_2d = [re.split((f'[{sep}]'), s) for s in l_contexts]
            # 1行分の情報用のオブジェクトに、各種コンテキストを登録する
            oneline.p = l_contexts_2d[0]
            oneline.a = l_contexts_2d[1]
            oneline.b = l_contexts_2d[2]
            oneline.c = l_contexts_2d[3]
            oneline.d = l_contexts_2d[4]
            oneline.e = l_contexts_2d[5]
            oneline.f = l_contexts_2d[6]
            oneline.g = l_contexts_2d[7]
            oneline.h = l_contexts_2d[8]
            oneline.i = l_contexts_2d[9]
            oneline.j = l_contexts_2d[10]
            # 1行分の情報用のオブジェクトを HTSFullLabel オブジェクトに追加する。
            self.append(oneline)
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
                    # 音素情報を登録(現在の音素のみ)
                    ol.phoneme = phoneme
                    # 音節情報を登録
                    ol.syllable = syllable
                    ol.previous_syllable = syllables[i_s - 1]
                    ol.next_syllable = syllables[i_s + 1]
                    # ノート情報を登録
                    ol.note = note
                    ol.previous_note = notes[i_n - 1]
                    ol.next_note = notes[i_n + 1]
                    # 楽曲情報を登録
                    ol.song = song
                    # print(list(map(id, [song, note, syllable, phoneme])))
                    onelines.append(ol)
        self.data = onelines
        self._fill_phonemes()
        return self

    def _fill_phonemes(self):
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
        self.song = song


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
        str_time = f'{self.start} {self.end} '
        # Phoneme 関連
        str_p = \
            '{0}@{1}ˆ{2}-{3}+{4}={5}_{6}%{7}ˆ{8}_{9}∼{10}-{11}!{12}[{13}${14}]{15}' \
            .format(*self.p)
        # Syllable 関連
        str_a = '/A:{0}-{1}-{2}@{3}~{4}'.format(*self.a)
        str_b = '/B:{0}_{1}_{2}@{3}|{4}'.format(*self.b)
        str_c = '/C:{0}+{1}+{2}@{3}&{4}'.format(*self.c)
        # Note 関連
        str_d = '/D:{0}!{1}#{2}${3}%{4}|{5}&{6};{7}-{8}'.format(*self.d)
        str_e = \
            '/E:{0}]{1}ˆ{2}={3}∼{4}!{5}@{6}#{7}+{8}]{9}${10}|{11}[{12}&{13}]{14}={15}ˆ{16}∼{17}#{18}_{19};{20}${21}&{22}%{23}[{24}|{25}]{26}-{27}ˆ{28}+{29}∼{30}={31}@{32}${33}!{34}%{35}#{36}|{37}|{38}-{39}&{40}&{41}+{42}[{43};{44}]{45};{46}∼{47}∼{48}ˆ{49}ˆ{50}@{51}[{52}#{53}={54}!{55}∼{56}+{57}!{58}ˆ{59}' \
            .format(*self.e)
        str_f = '/F:{0}#{1}#{2}-{3}${4}${5}+{6}%{7};{8}'.format(*self.f)
        # Phrase 関連
        str_g = '/G:{0}_{1}'.format(*self.g)
        str_h = '/H:{0}_{1}'.format(*self.h)
        str_i = '/I:{0}_{1}'.format(*self.i)
        # Song 関連
        str_j = '/J:{0}~{1}@{2}'.format(*self.j)
        # 各パラメータの文字列を結合
        str_self = ''.join((str_time, str_p, str_a, str_b, str_c, str_d,
                            str_e, str_f, str_g, str_h, str_i, str_j))
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
        return self

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

    def check(self):
        """
        まとめてチェックする。
        """
        self.check_number_of_values()
        self.check_position()

    def check_number_of_values(self):
        """
        リストとしての要素数と、コンテキストに記載されている要素数が一致するか点検する。
        Noteに記載されている
        """
        # 各音節内音素数が、ラベルに記載されている値と一致するか確認する。
        for i, syllable in enumerate(self.all_syllables):
            assert str(len(syllable)) == str(syllable.number_of_phonemes), \
                f'音節内音素数に不整合があります。i:{i} len(syllable):{len(syllable)} syllable.number_of_phonemes:{syllable.number_of_phonemes}'
        for i, note in enumerate(self):
            assert str(len(note)) == str(note.number_of_syllables), \
                f'ノート内音節数に不整合があります。i:{i} len(note):{len(note)} note.number_of_syllables:{note.number_of_syllables}'

    def check_position(self):
        """
        各position がちゃんとしているか確認する。
        """
        for syllable in self.all_syllables:
            assert all(str(phoneme.position) == str(idx + 1) for (idx, phoneme) in enumerate(syllable)), \
                '音節内音素位置に不整合があります。'
        for note in self.all_notes:
            assert all(str(syllable.position) == str(idx + 1) for (idx, syllable) in enumerate(note)), \
                'ノート内音節位置に不整合があります。'


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
        return int(self.contexts[18])

    @position_backward.setter
    def position_backward(self, position_backward: int):
        self.contexts[18] = position_backward

    @property
    def number_of_syllables(self):
        """
        ノート内音節数(e6)
        """
        return self.contexts[5]

    @number_of_syllables.setter
    def number_of_syllables(self, number: int):
        self.contexts[5] = number

    def is_pau(self):
        """
        休符かどうかを返す
        """
        return self[0][0].identity in ('pau', 'sil')


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
    def position(self):
        """
        ノート内での位置(b2)
        1-indexed
        """
        return int(self.contexts[1])

    @position.setter
    def position(self, position: int):
        self.contexts[1] = position

    @property
    def position_backward(self):
        """
        ノート内での後ろから数えた位置(b3)
        1-indexed
        """
        return int(self.contexts[2])

    @position_backward.setter
    def position_backward(self, position_backward: int):
        self.contexts[2] = position_backward

    @property
    def number_of_phonemes(self):
        """
        音節内の音素数(b1)
        """
        return self.contexts[0]

    @number_of_phonemes.setter
    def number_of_phonemes(self, number: int):
        self.contexts[0] = number


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

def adjust_syllables_to_sinsy(full_label: HTSFullLabel) -> HTSFullLabel:
    """
    出力用に休符まわりの音節コンテキストを調整する。
    """
    new_label = deepcopy(full_label)
    for ol in new_label[1:]:
        if ol.previous_syllable[0].identity in ('pau', 'sil'):
            ol.a[0:2] = ['xx'] * 3
    for ol in new_label[:-1]:
        if ol.next_syllable[0].identity in ('pau', 'sil'):
            ol.c[0:2] = ['xx'] * 3

    return new_label

def adjust_notes_to_sinsy(full_label: HTSFullLabel, strict=True) -> HTSFullLabel:
    """
    休符の前後のノート情報を調整したい。
    Sinsy仕様の d, f では休符を飛ばした音符を検出して処理している。

    音程関連は必ずやる。
    休符の長さに関する前後情報は持っておきたい。
    """
    new_label = deepcopy(full_label)
    if strict:
        # 前のノートに関する処理
        for ol in new_label[1:]:
            if ol.previous_note.is_pau():
                ol.d[0:3] = ['xx'] * 3
                ol.d[3:8] = ['xx'] * 5
        # 次のノートに関する処理
        for ol in new_label[:-1]:
            if ol.next_note.is_pau():
                ol.f[0:3] = ['xx'] * 3
                ol.f[3:8] = ['xx'] * 5
    else:
        # 前のノートに関する処理
        for ol in new_label[1:]:
            if ol.previous_note.is_pau():
                ol.d[0:3] = ['xx'] * 3
        # 次のノートに関する処理
        for ol in new_label[:-1]:
            if ol.next_note.is_pau():
                ol.f[0:3] = ['xx'] * 3
    # 現在のノートに関する処理
    for ol in new_label:
        if ol.note.is_pau():
            ol.e[0:2] = ['xx'] * 2

    return new_label

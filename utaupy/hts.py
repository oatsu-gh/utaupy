#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
Python3 module for HTS-full-label.
"""

import re
from collections import UserList
from itertools import chain

# import itertools


class HTSFullLabel(list):
    """
    HTSのフルコンテキストラベルの1行を扱うクラス
    OneLine からなる list
    [OneLine, OneLine, ..., OneLine]
    """

    def __init__(self):
        super().__init__()
        self.song = Song()

    def write(self, path, mode='w', encoding='utf-8') -> str:
        """
        ファイル出力する
        """
        s = '\n'.join([str(oneline) for oneline in self])
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s

    def load(self, path=None, strings=None, lines=None, songobj=None, encoding='utf-8') -> list:
        """
        ファイル、文字列、文字列のリスト、Songオブジェクトのいずれかより値を取得して登録する。
        """
        arguments = (path, strings, lines, songobj)
        assert not all(arg is None for arg in arguments
                       ), 'One arguments in "path", "lines" or "songobj" is needed to load.'
        assert not all(arg is None for arg in arguments
                       ), 'Only one arguments in "path", "lines" or "songobj" can be loaded.'
        if path is not None:
            self._load_from_path(path)
        elif lines is not None:
            self._load_from_lines(lines)
        elif songobj is not None:
            self._load_from_songobj(songobj)
        else:
            raise Exception('An unexpected error occurred.')
        return self

    def _load_from_path(self, path, encoding='utf-8') -> list:
        """
        ファイルをもとに値を登録する。
        """
        # パスに半角スペースが入っている場合に出現する引用符を除去
        path = path.strip('"')
        # ファイルを読み取って行のリストにする
        try:
            with open(path, mode='r', encoding=encoding) as f:
                lines = [line.rstrip('\n') for line in f.readlines()]
        except UnicodeDecodeError:
            with open(path, mode='r', encoding='sjis') as f:
                lines = [line.rstrip('\n') for line in f.readlines()]
        # 行ごとに分割したリストをもとに情報を登録する。
        self._load_from_lines(lines)
        return self

    def _load_from_lines(self, lines: list) -> list:
        """
        文字列のリスト(行のリスト)をもとに値を登録する。
        """
        # 各行を解析してHTSFullLabelに追加する。
        for line in lines:
            # 1行分の情報用のオブジェクトを生成
            oneline = _OneLine()
            # 空白で分割して、時刻情報とそれ以外のコンテキストに分ける
            line_split = line.split(maxsplit=2)
            oneline.start = int(line_split[0])
            oneline.end = int(line_split[1])
            str_contexts = line_split[2]
            # コンテキスト文字列を /A: などの文字列で区切って一次元リストにする
            l_contexts = re.split('/.:', str_contexts)
            # 特定の文字でさらに区切って二次元リストにする
            l_contexts_2d = \
                [
                    re.split('[{}]'.format(re.escape('=+-~!@#$%^&;_|[]')), s)
                    for s in l_contexts
                ]
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

    def _load_from_songobj(self, songobj: list) -> list:
        """
        hts.Song オブジェクトをもとにコンテキストを登録する。
        """
        self.song = songobj
        self.fill_contexts_from_songobj()
        return self

    def fill_contexts_from_songobj(self) -> list:
        """
        自身が持つSongオブジェクトをもとにコンテキスト情報を埋める。
        """
        song = self.song
        phrases = [Phrase()] + song + [Phrase()]
        for i_p, phrase in enumerate(phrases[1:-1], 1):
            notes = [Note()] + phrase + [Note()]
            for i_n, note in enumerate(notes[1:-1], 1):
                syllables = [Note()] + phrase + [Note()]
                for i_s, syllable in enumerate(syllables[1:-1], 1):
                    for phoneme in syllable:
                        print(list(map(id, [phoneme, note, syllable, phoneme])))
                        ol = _OneLine()
                        # 音素情報を登録(現在の音素のみ)
                        ol.phoneme_current = phoneme
                        # 音節情報を登録
                        ol.syllable_current = syllable
                        ol.syllable_previous = syllables[i_s - 1]
                        ol.syllable_next = syllables[i_s - 1]
                        # 音符情報を登録
                        ol.note_current = note
                        ol.note_previous = notes[i_n - 1]
                        ol.note_next = notes[i_n + 1]
                        # 楽節情報を登録
                        ol.phrase_current = phrase
                        ol.phrase_previous = phrases[i_p - 1]
                        ol.phrase_next = phrases[i_p + 1]
                        # 楽曲情報を登録
                        ol.song = song
        self._fill_phoneme_contexts()
        return self

    def _fill_phoneme_contexts(self) -> list:
        """
        phoneme_current をもとに、前後の音素に関する項を埋める。
        """
        # fill previous phoneme
        extended_self = [_OneLine(), _OneLine()] + self + [_OneLine(), _OneLine()]
        # ol is OneLine object
        for i, ol in enumerate(extended_self[2:-2], 2):
            ol.phoneme_before_previous = extended_self[i - 2].phoneme_current
            ol.phoneme_previous = extended_self[i - 1].phoneme_current
            ol.phoneme_next = extended_self[i + 1].phoneme_current
            ol.phoneme_after_next = extended_self[i + 2].phoneme_current
        return self


class _OneLine:
    """
    HTSのフルコンテキストラベルの1行を扱うクラス
    ファイルを読み取って HTSFullLabel を生成するときと、
    HTSFullLabel をファイル出力するときに使う。
    """

    def __init__(self):
        self.phoneme_before_previous = Phoneme()
        self.phoneme_previous = Phoneme()
        self.phoneme_current = Phoneme()
        self.phoneme_next = Phoneme()
        self.phoneme_after_next = Phoneme()
        self.syllable_previous = Syllable()
        self.syllable_current = Syllable()
        self.syllable_next = Syllable()
        self.note_previous = Note()
        self.note_current = Note()
        self.note_next = Note()
        self.phrase_previous = Phrase()
        self.phrase_current = Phrase()
        self.phrase_next = Phrase()
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
        #
        str_g = '/G:{0}_{1}'.format(*self.g)
        str_h = '/H:{0}_{1}'.format(*self.h)
        str_i = '/I:{0}_{1}'.format(*self.i)
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
        return int(self.phoneme_current.start)

    @start.setter
    def start(self, start_time: int):
        self.phoneme_current.start = int(start_time)

    @property
    def end(self) -> int:
        """
        発声終了時刻
        """
        return int(self.phoneme_current.end)

    @end.setter
    def end(self, end_time: int):
        self.phoneme_current.end = int(end_time)

    @property
    def p(self) -> list:
        """
        音素に関するコンテキスト
        """
        p = [
            self.phoneme_current.language_independent_identity,
            self.phoneme_before_previous.identity,
            self.phoneme_previous.identity,
            self.phoneme_current.identity,
            self.phoneme_next.identity,
            self.phoneme_after_next.identity,
            self.phoneme_before_previous.flag,
            self.phoneme_previous.flag,
            self.phoneme_current.flag,
            self.phoneme_next.flag,
            self.phoneme_after_next.flag,
            self.phoneme_current.position_forward,
            self.phoneme_current.position_backward,
            self.phoneme_current.distance_from_previous_vowel,
            self.phoneme_current.distance_to_next_vowel,
            self.phoneme_current.undefined_context
        ]
        return p

    @p.setter
    def p(self, phoneme_contexts: list):
        self.phoneme_current.language_independent_identity = phoneme_contexts[0]
        self.phoneme_before_previous.identity = phoneme_contexts[1]
        self.phoneme_previous.identity = phoneme_contexts[2]
        self.phoneme_current.identity = phoneme_contexts[3]
        self.phoneme_next.identity = phoneme_contexts[4]
        self.phoneme_after_next.identity = phoneme_contexts[5]
        self.phoneme_before_previous.flag = phoneme_contexts[6]
        self.phoneme_previous.flag = phoneme_contexts[7]
        self.phoneme_current.flag = phoneme_contexts[8]
        self.phoneme_next.flag = phoneme_contexts[9]
        self.phoneme_after_next.flag = phoneme_contexts[10]
        self.phoneme_current.position_forward = phoneme_contexts[11]
        self.phoneme_current.position_backward = phoneme_contexts[12]
        self.phoneme_current.distance_from_previous_vowel = phoneme_contexts[13]
        self.phoneme_current.distance_to_next_vowel = phoneme_contexts[14]
        self.phoneme_current.undefined_context = phoneme_contexts[15]

    @property
    def a(self) -> list:
        """
        直前の音節のコンテキスト
        """
        return self.syllable_previous.contexts

    @a.setter
    def a(self, syllable_contexts: list):
        self.syllable_previous.contexts = syllable_contexts

    @property
    def b(self) -> list:
        """
        現在の音節のコンテキスト
        """
        return self.syllable_current.contexts

    @b.setter
    def b(self, syllable_contexts: list):
        self.syllable_current.contexts = syllable_contexts

    @property
    def c(self) -> list:
        """
        直後の音節のコンテキスト
        """
        return self.syllable_next.contexts

    @c.setter
    def c(self, syllable_contexts: list):
        self.syllable_next.contexts = syllable_contexts

    @property
    def d(self) -> list:
        """
        直前の音符のコンテキスト
        """
        return self.note_previous.contexts

    @d.setter
    def d(self, note_contexts: list):
        self.note_previous.contexts = note_contexts

    @property
    def e(self) -> list:
        """
        現在の音符のコンテキスト
        """
        return self.note_current.contexts

    @e.setter
    def e(self, note_contexts: list):
        self.note_current.contexts = note_contexts

    @property
    def f(self) -> list:
        """
        直後の音符のコンテキスト
        """
        return self.note_next.contexts

    @f.setter
    def f(self, note_contexts: list):
        self.note_next.contexts = note_contexts

    @property
    def g(self) -> list:
        """
        直前の楽節のコンテキスト
        """
        return self.phrase_previous.contexts

    @g.setter
    def g(self, phrase_contexts: list):
        self.phrase_previous.contexts = phrase_contexts

    @property
    def h(self) -> list:
        """
        現在の楽節のコンテキスト
        """
        return self.phrase_current.contexts

    @h.setter
    def h(self, phrase_contexts: list):
        self.phrase_current.contexts = phrase_contexts

    @property
    def i(self) -> list:
        """
        直後の楽節のコンテキスト
        """
        return self.phrase_next.contexts

    @i.setter
    def i(self, phrase_contexts: list):
        self.phrase_next.contexts = phrase_contexts

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


class Song(list):
    """
    曲を扱うクラス
    今日の曲(j1-j3)
    [Phrase, Phrase, ..., Phrase]
    """

    def __init__(self):
        super().__init__()
        self.contexts = ['xx'] * 3

    @property
    def all_phrases(self):
        """
        Phraseをすべて並べたリストを返す。
        """
        return list(chain.from_iterable(self))

    @property
    def all_notes(self):
        """
        Noteをすべて並べたリストを返す。
        """
        notes_2d = [phrase.notes for phrase in self.all_phrases]
        return list(chain.from_iterable(notes_2d))

    @property
    def all_syllables(self):
        """
        Syllableをすべて並べたリストを返す。
        """
        syllables_2d = [note.syllables for note in self.all_notes]
        return list(chain.from_iterable(syllables_2d))

    @property
    def all_phonemes(self):
        """
        Phonemeをすべて並べたリストを返す。
        """
        phonemes_2d = [syllable.phonemes for syllable in self.all_syllables]
        return list(chain.from_iterable(phonemes_2d))


class Phrase(list):
    """
    フレーズを扱うクラス
    昨日のフレーズ G (g1~g2)
    今日のフレーズ H (h1~h2)
    明日のフレーズ I (i1~i2)
    基本的にはHのみを操作する。
    [Note, Note, Note, ..., Note]
    """

    def __init__(self):
        super().__init__()
        self.contexts = ['xx'] * 2


class Note(list):
    """
    音符または休符を扱うクラス
    1ノート（音符と休符）を扱うクラス
    昨日のノート D (d1~d5)
    今日のノート E (e1~e60)
    明日のノート F (f1~f5)
    基本的にはEのみを操作する。
    [Syllable, Syllable, ..., Syllable]
    """

    def __init__(self):
        super().__init__()
        self.contexts = ['xx'] * 60


class Syllable(list):
    """
    1音節を扱うクラス
    昨日の音節 A (a1~a5)
    今日の音節 B (b1~b5)
    明日の音節 C (c1~c5)
    [Phoneme, Phoneme, ..., Phoneme]
    """

    def __init__(self):
        super().__init__()
        self.contexts = ['xx'] * 5


class Phoneme:
    """
    音素を扱うクラス
    p1~p16
    """

    def __init__(self):
        # 発声開始時刻
        self.start = 0
        # 発声終了時刻
        self.end = 0
        # p1: 言語非依存の音素記号(p, c, v など)
        self.language_independent_identity = 'xx'
        # p4: 音素記号
        self.identity = 'xx'
        # p9: フラグ
        self.flag = 'xx'
        # p12: 音節(Syllable)内の、先頭から数えた位置
        self.position_forward = 'xx'
        # p13: 音節(Syllable)内の、末尾から数えた位置
        self.position_backward = 'xx'
        # p14: 今が子音のときのみに定義される、直前の母音からの距離
        self.distance_from_previous_vowel = 'xx'
        # p15: 今が子音のときのみに定義される、直後の母音までの距離
        self.distance_to_next_vowel = 'xx'
        # 未定義のコンテキスト
        self.undefined_context = 'xx'

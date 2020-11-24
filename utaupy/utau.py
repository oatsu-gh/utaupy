#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
UTAU音源を扱うモジュール
"""
from collections import UserDict
from glob import glob

from . import otoini as _otoini


class PrefixMap(UserDict):
    """
    UTAUの多音階音源用の prefixmap ファイルを扱うクラス。
    prefixmap_obj[音階名] または prefixmap_obj[音階番号] で
    サフィックス文字列を取得できるようにしたい。
    """

    def __init__(self, path):
        super().__init__()
        self.comment_lines = []
        with open(path, 'r') as prefixmap_file:
            lines = prefixmap_file.readlines()
        # 改行文字を削除、コメント行を無視
        lines = [line.rstrip('\r\n') for line in lines if not line.startswith('//')]
        # 空白で区切って {音程: suffix文字列} の辞書にする
        lines_2d = [line.split(maxsplit=1) for line in lines]
        # 音程表記をUSTでの音階番号に変換
        abc_to_notenum = {
            'C1': '24', 'C#1': '25', 'D1': '26', 'D#1': '27', 'E1': '28', 'F1': '29',
            'F#1': '30', 'G1': '31', 'G#1': '32', 'A1': '33', 'A#1': '34', 'B1': '35',
            'C2': '36', 'C#2': '37', 'D2': '38', 'D#2': '39', 'E2': '40', 'F2': '41',
            'F#2': '42', 'G2': '43', 'G#2': '44', 'A2': '45', 'A#2': '46', 'B2': '47',
            'C3': '48', 'C#3': '49', 'D3': '50', 'D#3': '51', 'E3': '52', 'F3': '53',
            'F#3': '54', 'G3': '55', 'G#3': '56', 'A3': '57', 'A#3': '58', 'B3': '59',
            'C4': '60', 'C#4': '61', 'D4': '62', 'D#4': '63', 'E4': '64', 'F4': '65',
            'F#4': '66', 'G4': '67', 'G#4': '68', 'A4': '69', 'A#4': '70', 'B4': '71',
            'C5': '72', 'C#5': '73', 'D5': '74', 'D#5': '75', 'E5': '76', 'F5': '77',
            'F#5': '78', 'G5': '79', 'G#5': '80', 'A5': '81', 'A#5': '82', 'B5': '83',
            'C6': '84', 'C#6': '85', 'D6': '86', 'D#6': '87', 'E6': '88', 'F6': '89',
            'F#6': '90', 'G6': '91', 'G#6': '92', 'A6': '93', 'A#6': '94', 'B6': '95',
            'C7': '96', 'C#7': '97', 'D7': '98', 'D#7': '99', 'E7': '100', 'F7': '101',
            'F#7': '102', 'G7': '103', 'G#7': '104', 'A7': '105', 'A#7': '106', 'B7': '107',
            'C8': '108', 'C#8': '109', 'D8': '110', 'D#8': '111', 'E8': '112', 'F8': '113',
            'F#8': '114', 'G8': '115', 'G#8': '116', 'A8': '117', 'A#8': '118', 'B8': '119'
        }
        # {音階番号: suffix文字列} の辞書になる
        for line in lines_2d:
            if len(line) == 1:
                self.data.update({abc_to_notenum[line[0]]: ''})
            else:
                self.data.update({abc_to_notenum[line[0]]: line[1]})


class UtauVoiceBank():
    """
    UTAU音源の原音設定を扱うクラス。
    音階と歌詞（連続音）を指定したら、原音設定を返すようにしたい。
    """

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.prefixmap = PrefixMap(f'{self.path}/prefix.map')
        self.otoini = {}
        # 原音設定ファイルを取得
        all_otoini_paths = glob(f'{path}/**/oto.ini', recursive=True)
        for path_otoini in all_otoini_paths:
            each_otoini = _otoini.load(path_otoini)
            self.otoini.update(each_otoini.as_dict())


def autoselect_alias(voicebank, utaupy_ust_note):
    """
    voicebank       : utaupy.utau.UtauVoiceBank オブジェクト
    utaupy_ust_note : utaupy.Ust.Note オブジェクト
    use_atalias     : Noteオブジェクトの '@alias' を使用するかどうか。
                      voicebankで指定しているUTAU音源が 対象USTのUTAU音源とは違う場合、
                      Falseにするほうがよい。

    Noteオブジェクトの歌詞と音程から、使用する原音に対応するエイリアスを決定する。
    ノート情報に @alias があればそのエイリアスを使用し、
    無い場合は prefix.map を使って決定する。
    """
    lyric = utaupy_ust_note.lyric
    if lyric == 'R':
        return 'R'
    # USTでエイリアスを強制指定している場合
    if lyric.startswith('?'):
        return lyric.lstrip('?')
    # 普通の歌詞の場合はprefixmapを参照してサフィックス追加
    alias = lyric + voicebank.prefixmap[str(utaupy_ust_note.notenum)]
    return alias


def get_oto(voicebank, utaupy_ust_note, suffix_exists=False):
    """
    voicebank       : utaupy.utau.UtauVoiceBank オブジェクト
    utaupy_ust_note : utaupy.Ust.Note オブジェクト
    use_atparam     : Noteオブジェクトの '@alias' などを使用するかどうか。
                      voicebankで指定しているUTAU音源が 対象USTのUTAU音源とは違う場合、
                      Falseにするほうがよい。
    Noteオブジェクトに対応する原音設定の値を取得する。
    """
    if suffix_exists is False:
        alias = autoselect_alias(voicebank, utaupy_ust_note)
    else:
        alias = utaupy_ust_note.lyric
    # 原音にちゃんとあるかどうか
    try:
        oto_for_the_alias = voicebank.otoini[alias]
    # なければ全部の数値がゼロの原音設定値を返す
    except KeyError as e:
        print(f'[WARN] KeyError: {e}')
        oto_for_the_alias = _otoini.Oto()
        oto_for_the_alias.Alias = alias
    return oto_for_the_alias


def autoadjust_parameters(voicebank, utaupy_ust_ust):
    """
    voicebank       : utaupy.utau.UtauVoiceBank オブジェクト
    utaupy_ust_ust  : utaupy.Ust.Ust オブジェクト

    # TODO: プラグイン用に'@'パラメータに対応させる。
    UTAUの「パラメータ自動調整」機能に相当するメソッド。
    ・エイリアス(@alias)
    ・STP(StartPoint)
    ・オーバーラップ(VoiceOverlap)
    ・先行発声(PreUtterance)
    の4つの値を調整する。

    # TODO: 子音速度100以外に対応させる。
    仕様
    前のノートが休符な時は、原音値をそのまま入力する。
    前のノートが休符でない場合
        前のノートの長さの半分が、oto.overlapからoto.preutteranceまでの長さよりも短い場合
            差分をSTPで削る
    """
    notes = utaupy_ust_ust.notes
    for i, note in enumerate(notes[1:], 1):
        halflen = notes[i - 1].length_ms / 2
        oto = get_oto(voicebank, note, suffix_exists=True)
        if halflen < oto.preutterance - oto.overlap:
            at_preuttr = halflen * oto.preutterance / (oto.preutterance - oto.overlap)
            at_overlap = halflen * oto.overlap / (oto.preutterance - oto.overlap)
            note.set_by_key('StartPoint', oto.preutterance - at_preuttr)
            note.set_by_key('PreUtterance', at_preuttr)
            note.set_by_key('VoiceOverlap', at_overlap)
            print('adjust')
        else:
            note.set_by_key('StartPoint', 0)
            note.set_by_key('PreUtterance', oto.preutterance)
            note.set_by_key('VoiceOverlap', oto.overlap)

#!/usr/bin/env python3
# Copyright (c) 2020 oatsu
"""
HTSフルラベルをUSTファイルに変換する。
"""
import utaupy as up


def htsnote2ustnote(hts_note: up.hts.Note, d_table: dict = None, joint: str = '') -> up.ust.Note:
    """
    utaupy.hts.Note を utaupy.ust.Note に変換する。

    joint: 音素記号を結合するときにはさむ文字
    """
    ust_note = up.ust.Note()
    # ノート長
    ust_note.length = int(hts_note.length) * 20
    # 音高情報が無かったらC4にする。
    ust_note.notenum = int(str(hts_note.notenum).replace('xx', '60'))
    # テンポ
    ust_note.tempo = hts_note.tempo
    # 拍子情報をラベル部分に書き込む
    ust_note.label = hts_note.beat
    # 歌詞を登録する
    phonemes = [phoneme.identity for phoneme in hts_note.phonemes]
    lyric = joint.join(phonemes).replace('pau', 'R')
    if lyric.endswith('cl') and lyric != 'cl':
        lyric = lyric.replace('cl', ' cl')
    ust_note.lyric = lyric

    return ust_note


def clean_beat(ust):
    """
    不要な拍子情報を削除する
    """
    # 拍子情報を一時的に記憶する変数
    beat = None
    # 拍子情報が変化する部分だけラベルを残す
    for note in ust.notes:
        if note.label == beat:
            del note['Label']
        else:
            beat = note.label


def songobj2ustobj(hts_song: up.hts.Song, d_table: dict = None, joint: str = '') -> up.ust.Ust:
    """
    Song オブジェクトを Ust オブジェクトに変換する。
    joint: 音素記号を結合するときにはさむ文字
    """
    ust = up.ust.Ust()
    # 各ノートを変換する
    for hts_note in hts_song:
        ust_note = htsnote2ustnote(hts_note, d_table, joint=joint)
        ust.notes.append(ust_note)
    # 重複するテンポ情報を削除
    ust.reload_tempo()
    # 重複する拍子情報を削除
    clean_beat(ust)
    return ust


def hts2ust(path_hts, path_ust, path_table=None, joint: str = ''):
    """
    HTSフルコンテキストラベルファイルをUSTファイルに変換する。
    """
    d_table = up.table.load(path_table) if path_table is not None else None
    full_label = up.hts.load(path_hts)
    ust = songobj2ustobj(full_label.song, d_table, joint=joint)
    ust.write(path_ust)


def main():
    """
    ファイル変換をする。
    """
    path_hts = input('path_hts: ')
    path_ust = path_hts.replace('.lab', '_hts2ust.ust')
    path_table = input('path_table: ')
    hts2ust(path_hts, path_ust, path_table)


if __name__ == '__main__':
    main()

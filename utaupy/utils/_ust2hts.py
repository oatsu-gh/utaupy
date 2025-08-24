#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
USTファイルをHTSフルラベルに変換する。
Songオブジェクトを使って生成する。
いまのところ日本語にしか対応していないので注意。

対象
    CQS:
        p11, p12, p13, p14
        a1, a2, a3,
        b1, b2, b3,
        c1, c2, c3,
        d1, d2, d3, (d5), d6, d7, d8,
        e1, e2, e3, (e5), e6, e7, e8, e57, e58,
        f1, f2, f3, (f5), f6, f7, f8
    QS:
        p1, p3, p4, p5

d2, d3, e2, e3, f2, f3 はスケール判定が必要なため、実行時にキー(スケール)を指定する必要がある。
キーを指定しない場合は上記の値は'xx'のままにする。
d3, e3, f3 には 'xx' を代入する。歌うときに休符の学習データ引っ張ってきそうな気はする。
"""

from decimal import Decimal

import utaupy as up


def ustnote2htsnote(
    ust_note: up.ust.Note, d_table: dict, key_of_the_note: int = None
) -> up.hts.Note:
    """
    utaupy.ust.Note を utaupy.hts.Note に変換する。
    """
    # ノート全体の情報を登録
    hts_note = up.hts.Note()
    # e1
    hts_note.notenum = ust_note.notenum
    # e2-e3
    if key_of_the_note is not None:
        # e2
        hts_note.relative_pitch = (ust_note.notenum - key_of_the_note) % 12
        # e3
        hts_note.key = key_of_the_note
    # e4----------------------------------------
    # NOTE: 拍子情報を扱うTimeSignaturesエントリがUSTに実装されたら有効化する。
    # if ust_note.timesignatures is not None:
    #     hts_note.beat = '/'.join(
    #         ust_note.timesignatures.strip('()').split('/')[:2]
    #     )
    # ------------------------------------------
    # e5
    hts_note.tempo = Decimal(ust_note.tempo)
    # e8
    hts_note.length = round(ust_note.length / 20)

    # UST内のノートの歌詞を空白で区切る
    kana_lyrics = ust_note.lyric.replace('っ', ' っ ').split()

    # TODO: 音節数を2以上にできるようにする
    hts_syllable = up.hts.Syllable()
    # かな→ローマ字 で音素変換する
    phonemes = []
    for lyric in kana_lyrics:
        phonemes += d_table.get(lyric, [lyric])
    # 音素を追加していく
    for phoneme in phonemes:
        hts_phoneme = up.hts.Phoneme()
        # p4
        hts_phoneme.identity = phoneme
        # p9
        # ustのローカルフラグが設定されている時だけp9に記入
        if ust_note.flags != '':
            hts_phoneme.flag = ust_note.flags
        # 音節に追加
        hts_syllable.append(hts_phoneme)
    hts_note.append(hts_syllable)

    return hts_note


def ustobj2songobj(ust: up.ust.Ust, d_table: dict, key_of_the_note: int = None) -> up.hts.Song:
    """
    Ustオブジェクトをノートごとに処理して、HTS用に変換する。
    日本語歌詞を想定するため、音節数は1とする。促音に注意。

    ust: Ustオブジェクト
    d_table: 日本語→ローマ字変換テーブル

    key_of_the_note:
        曲のキーだが、USTからは判定できない。
        Sinsyでは 0 ~ 11 または 'xx' である。
    """
    song = up.hts.Song()
    ust_notes = ust.notes
    # Noteオブジェクトの種類を変換
    for ust_note in ust_notes:
        hts_note = ustnote2htsnote(ust_note, d_table, key_of_the_note=key_of_the_note)
        song.append(hts_note)

    # ノート長や位置などを自動補完
    song.autofill()
    # 発声開始時刻と終了時刻をノート長に応じて設定
    song.reset_time()
    return song


def ust2hts(
    path_ust: str,
    path_hts: str,
    path_table: str,
    strict_sinsy_style: bool = True,
    as_mono: bool = False,
):
    """
    USTファイルをLABファイルに変換する。
    """
    ust = up.ust.load(path_ust)
    d_table = up.table.load(path_table, encoding='utf-8')
    # Ust → HTSFullLabel
    hts_song = ustobj2songobj(ust, d_table)
    # HTSFullLabel中の重複データを削除して整理
    # ファイル出力
    hts_song.write(path_hts, strict_sinsy_style=strict_sinsy_style, as_mono=as_mono)


# def __ust2hts_with_precise_time(
#         path_ust: str, path_hts: str, path_table: str,
#         strict_sinsy_style: bool = True, as_mono: bool = False):
#     """
#     USTファイルをLABファイルに変換する。時刻の詳細を保った状態で保存する。
#     1tick = 1,470,000
#     4分音符 = 480tick = 705,600,000
#     """
#     ust = up.ust.load(path_ust)
#     d_table = up.table.load(path_table, encoding='utf-8')
#     # Ust → HTSFullLabel
#     hts_song = ustobj2songobj(ust, d_table)

#     # ノート数が一致することを確認する
#     assert len(ust.notes) == len(hts_song.all_notes)
#     # 時刻を再計算する。SynthVと同じ仕様
#     ust_note_length_x1470000 = [note.length * 1470000 for note in ust.notes]
#     # HTSFullLabel中の重複データを削除して整理
#     # ファイル出力
#     hts_song.write(
#         path_hts, strict_sinsy_style=strict_sinsy_style, as_mono=as_mono)


def main():
    """
    USTファイルをLABファイルおよびJSONファイルに変換する。
    """
    from glob import glob
    from os.path import isfile, join, splitext

    # 各種パスを指定
    ust_dir = input('Select a directory or a UST file: ').strip('"')
    ust_files = [ust_dir] if isfile(ust_dir) else glob(join(ust_dir, '*.ust'))
    path_table = input('path_table: ')

    for path_in in ust_files:
        try:
            path_out = f'{splitext(path_in)[0]}.lab'
            # 変換
            ust2hts(path_in, path_out, path_table, strict_sinsy_style=False)
        except Exception as e:
            raise Exception(f'Some exception was raised while processing {path_in}') from e


if __name__ == '__main__':
    main()

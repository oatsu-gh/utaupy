#!/usr/bin/env python3
# coding: utf-8
"""
UTAU関連ファイルの相互変換
"""
# from pysnooper import snoop
# from pprint import pprint
from copy import deepcopy

from . import label as _label
from . import otoini as _otoini
from . import table as _table
from . import ust as _ust


def main():
    """ここ書く必要なくない？"""
    print('AtomとReaperが好き')


def ust2otoini(ust, name_wav, path_tablefile, mode='romaji_cv', dt=100, debug=False):
    """
    UstクラスオブジェクトからOtoIniクラスオブジェクトを生成
    機能選択部分
    """
    allowed_modes = ['mono', 'romaji_cv']
    if mode == 'romaji_cv':
        print('  変換モード : ひらがな歌詞 → ローマ字CV')
        otoini = ust2otoini_romaji_cv(ust, name_wav, path_tablefile, dt, debug=debug)
    elif mode == 'mono':
        print('  変換モード : ひらがな歌詞 → ローマ字モノフォン')
        otoini = ust2otoini_mono(ust, name_wav, path_tablefile, debug=debug)
    else:
        raise ValueError('argument \'mode\' must be in {}'.format(allowed_modes))
    return otoini


def make_finalnote_R(ust):
    """Ustの最後のノートが必ず休符 になるようにする"""
    notes = ust.values
    note = notes[-2]
    # Ust内の最後はTRACKENDなので後ろから2番目のノートで判定
    # DEBUG: NoteのIDが引き継がれるっぽくて最後から2番目のノートもRになってしまう。
    if note.lyric not in ('pau', 'sil', 'R'):
        print('  末尾に休符を自動追加しました。')
        extra_note = deepcopy(note)
        extra_note.lyric = 'R'
        notes.insert(-1, extra_note)
    processed_ust = _ust.Ust()
    processed_ust.values = notes
    return processed_ust


def ust2otoini_mono(ust, name_wav, path_tablefile, dt=100, debug=False):
    """
    UstクラスオブジェクトからOtoIniクラスオブジェクトを生成
    vowel_otoの対称は母音以外に 'N', 'cl' なども含まれる。
    mode : otoiniのエイリアス種別選択
    【パラメータ設定図】
    simple_oto---------------------------------------------------------------
      |||左ブランク・オーバーラップ・先行発声 ||固定範囲・右ブランク
      |||       ノート長 + 2dt (ms)           ||
    -------------------------------------------------------------------------
    子音・半母音用のoto------------------------------------------------------
      ||左ブランク・オーバーラップ |先行発声 ||固定範囲・右ブランク
      ||          dt(ms)           | dt(ms)  ||
    -------------------------------------------------------------------------
    母音用のoto--------------------------------------------------------------
      ||左ブランク・オーバーラップ |先行発声 |固定範囲            |右ブランク
      ||          dt(ms)           | dt(ms)  | ノート長 - dt (ms) |
    -------------------------------------------------------------------------
    """
    d = _table.load(path_tablefile)  # ひらがなローマ字対応表の辞書
    d.update({'R': ['pau'], 'pau': ['pau'], 'sil': ['sil'], 'br': ['br'], '息': ['br']})
    ust = make_finalnote_R(ust)  # 最終ノートが休符じゃない場合を対策
    notes = ust.values
    tempo = ust.tempo

    # UstのNoteオブジェクトごとにOtoオブジェクトを生成
    l = []  # simple_otoを入れるリスト
    t = 0  # ノート開始時刻を記録
    for note in notes[2:-1]:
        length = note.get_length_ms(tempo)
        simple_oto = _otoini.Oto()  # 各パラメータ位置を両端に集めたOto
        simple_oto.filename = name_wav
        simple_oto.alias = note.lyric
        simple_oto.offset = t
        simple_oto.overlap = 0
        simple_oto.preutterance = 0
        simple_oto.consonant = length
        simple_oto.cutoff = -length  # 負で左ブランク相対時刻, 正で絶対時刻
        l.append(simple_oto)
        t += length  # 今のノート終了位置が次のノート開始位置

    # Otoを音素ごとに分割
    new = []  # mono_otoを入れるリスト
    for simple_oto in l:
        if debug:
            print(f'    {simple_oto.values}')
        try:
            phonemes = d[simple_oto.alias]
        except KeyError as e:
            print('\nKeyError in utaupy.convert.ust2otoini_mono---------')
            print('ひらがなローマ字変換に失敗しました。半角スペースで音素として分割してぶち込みます。')
            print('エラー詳細:', e)
            print('--------------------------------------\n')
            phonemes = simple_oto.alias.split()
            print(phonemes)
        # 子音+母音 「か(k a)」
        if len(phonemes) == 2:
            # 子音部分
            first_oto = _otoini.Oto()
            first_oto.filename = name_wav
            first_oto.alias = phonemes[0]
            first_oto.offset = simple_oto.offset - (2 * dt)
            first_oto.overlap = 0
            first_oto.preutterance = dt
            first_oto.consonant = 2 * dt
            first_oto.cutoff = - 2 * dt
            new.append(first_oto)
            # 母音部分
            second_oto = _otoini.Oto()
            second_oto.filename = name_wav
            second_oto.alias = phonemes[1]
            second_oto.offset = simple_oto.offset - dt
            second_oto.overlap = 0
            second_oto.preutterance = dt
            second_oto.consonant = 2 * dt
            second_oto.cutoff = simple_oto.cutoff - dt
            new.append(second_oto)
        # 母音など 「あ(a)」「ん(cl)」「っ(cl)」「(pau)」「(br)」「(sil)」
        elif len(phonemes) == 1:
            first_oto = _otoini.Oto()
            first_oto.filename = name_wav
            first_oto.alias = phonemes[0]
            first_oto.offset = simple_oto.offset - dt
            first_oto.overlap = 0
            first_oto.preutterance = dt
            first_oto.consonant = 2 * dt
            first_oto.cutoff = simple_oto.cutoff - dt
            new.append(first_oto)
        # 子音+半母音+母音 「ぐぁ(g w a)」
        elif len(phonemes) == 3:
            # 子音部分
            first_oto = _otoini.Oto()
            first_oto.filename = name_wav
            first_oto.alias = phonemes[0]
            first_oto.offset = simple_oto.offset - (2 * dt)
            first_oto.overlap = 0
            first_oto.preutterance = dt
            first_oto.consonant = 2 * dt
            first_oto.cutoff = - 2 * dt
            new.append(first_oto)
            # 半母音部分
            second_oto = _otoini.Oto()
            second_oto.filename = name_wav
            second_oto.alias = phonemes[1]
            second_oto.offset = simple_oto.offset - dt
            second_oto.overlap = 0
            second_oto.preutterance = dt
            second_oto.consonant = 2 * dt
            second_oto.cutoff = - 2 * dt
            new.append(second_oto)
            # 母音部分
            third_oto = _otoini.Oto()
            third_oto.filename = name_wav
            third_oto.alias = phonemes[2]
            third_oto.offset = simple_oto.offset
            third_oto.overlap = 0
            third_oto.preutterance = dt
            third_oto.consonant = 2 * dt
            third_oto.cutoff = simple_oto.cutoff - (2 * dt)
            new.append(third_oto)
        else:
            raise ValueError('len(alias) must be in [1, 2, 3]')

    new[0].offset = 0
    new[0].preutterance = 0
    mono_otoini = _otoini.OtoIni()
    mono_otoini.values = new
    return mono_otoini


def ust2otoini_romaji_cv(ust, name_wav, path_tablefile, dt=100, debug=False):
    """
    UstクラスオブジェクトからOtoIniクラスオブジェクトを生成
    dt   : 左ブランク - オーバーラップ - 先行発声 - 固定範囲と右ブランク の距離
    mode : otoiniのエイリアス種別選択
    【パラメータ設定図】
      | 左ブランク |オーバーラップ| 先行発声 | 固定範囲 |   右ブランク   |
      |   (dt)ms   |    (dt)ms    |  (dt)ms  |  (dt)ms  | (length-2dt)ms |
    """
    d = _table.load(path_tablefile)  # ひらがなローマ字対応表の辞書
    d.update({'R': ['pau'], 'pau': ['pau'], 'sil': ['sil'], 'br': ['br'], '息': ['br']})
    ust = make_finalnote_R(ust)  # 最終ノートが休符じゃない場合を対策
    notes = ust.values
    tempo = ust.tempo
    l = []  # otoini生成元にするリスト
    t = 0  # ノート開始時刻を記録

    # NOTE: ここnotes[2:-1]とust.values[2:1]で処理時間に差は出る？
    for note in notes[2:-1]:
        if debug:
            print(f'    {note.values}')
        try:
            phonemes = d[note.lyric]
        except KeyError as e:
            print('\nKeyError in utaupy.convert.ust2otoini_romaji_cv----')
            print('ひらがなローマ字変換に失敗しました。そのままぶち込みます。')
            print('変換前の歌詞(note.lyric):', note.lyric)
            print('エラー詳細(e)           :', e)
            phonemes = note.lyric.split()
            print('---------------------------------------------------\n')

        length = note.get_length_ms(tempo)
        oto = _otoini.Oto()
        oto.filename = name_wav     # wavファイル名
        oto.alias = ' '.join(phonemes)  # エイリアスは音素ごとに空白区切り
        oto.offset = t - (2 * dt)   # 左ブランクはノート開始位置より2段手前
        oto.preutterance = 2 * dt   # 先行発声はノート開始位置
        oto.consonant = min(3 * dt, length + 2 * dt)  # 子音部固定範囲は先行発声より1段後ろか終端
        oto.cutoff = -(length + 2 * dt)  # 右ブランクはノート終端、負で左ブランク相対時刻、正で絶対時刻

        # 1音素のときはノート開始位置に先行発声を配置
        if len(phonemes) == 1:
            oto.overlap = 0

        # 2,3音素の時はノート開始位置に先行発声、その手前にオーバーラップ
        elif len(phonemes) in (2, 3):
            oto.overlap = dt

        # 4音素以上には未対応。特殊音素と判断して1音素として処理
        else:
            print('\nERROR when setting alias : phonemes = {}-------------'.format(phonemes))
            print('1エイリアスあたり 1, 2, 3 音素しか対応していません。')
            oto.alias = ''.join(phonemes)
            oto.overlap = 0

        l.append(oto)
        t += length  # 今のノート終了位置が次のノート開始位置

    # 最初が休符なことを想定して、
    l[0].offset = 0  # 最初の左ブランクを0にする
    l[0].preutterance = 0  # 最初の先行発声を0にする
    l[0].overlap = 0  # 最初のオーバーラップを0にする
    otoini = _otoini.OtoIni()
    otoini.values = l
    return otoini


def otoini2label(otoini, mode='auto',
                 otoini_time_order=10**(-3), label_time_order=10**(-7), debug=False):
    """
    OtoIniクラスオブジェクトからLabelクラスオブジェクトを生成
    発声開始: オーバーラップ
    発声終了: 次のノートのオーバーラップ
    発音記号: エイリアス流用
    otoini_time_order: otoiniの時間単位の桁。
    label_time_order : ラベルの時間単位の桁。
    """
    time_order_ratio = otoini_time_order / label_time_order
    print('  time_order_ratio:', time_order_ratio)

    allowed_modes = ['auto', 'mono', 'romaji_cv']
    # エイリアスのタイプ自動判別
    if mode == 'auto':
        if otoini.is_mono():
            mode = 'mono'
        else:
            mode = 'romaji_cv'

    if mode == 'mono':
        print('  mode: OtoIni(mono) -> Label(mono)')
        # [[発音開始時刻, 発音記号], ...] の仮リストにする
        tmp = []
        otoini_values = otoini.values
        for oto in otoini_values:
            if debug:
                print(f'    {oto.values}')
            t_start = (oto.offset + oto.preutterance) * time_order_ratio
            tmp.append([int(t_start), oto.alias])
        # [[発音開始時刻, 発音終了時刻, 発音記号], ...]
        lines = [[v[0], tmp[i + 1][0], v[1]] for i, v in enumerate(tmp[:-1])]
        # ↓内包表記を展開した場合↓-----
        # lines = []
        # for i, v in enumerate(tmp[:-1]):
        #     lines.append([v[0], tmp[i+1][0], v[1]])
        # -------------------------------

        # 最終ノートだけ特別な処理
        oto = otoini_values[-1]
        # 発声開始位置
        t_start = int(time_order_ratio * (oto.offset + oto.preutterance))
        # 発声終了位置(右ブランクの符号ごとの挙動違いに対応)
        t_end = int(time_order_ratio * oto.cutoff2)
        # 最終ノートをリストに追加
        lines.append([t_start, t_end, oto.alias])

    elif mode == 'romaji_cv':
        print('  mode: OtoIni(romaji_cv) -> Label(mono)')
        # モノフォン化
        otoini.monophonize()
        # [[発音開始時刻, 発音記号], ...] の仮リストにする
        tmp = []
        otoini_values = otoini.values
        for oto in otoini_values:
            if debug:
                print(f'    {oto.values}')

            t_start = time_order_ratio * (oto.offset + oto.preutterance)
            tmp.append([int(t_start), oto.alias])

        # [[発音開始時刻, 発音終了時刻, 発音記号], ...]
        lines = [[v[0], tmp[i + 1][0], v[1]] for i, v in enumerate(tmp[:-1])]
        # ↓内包表記を展開した場合↓-----
        # lines = []
        # for i, v in enumerate(tmp[:-1]):
        #     lines.append([v[0], tmp[i+1][0], v[1]])
        # -------------------------------

        # 最終ノートだけ特別な処理
        oto = otoini_values[-1]
        # 発声開始位置
        t_start = int(time_order_ratio * (oto.offset + oto.preutterance))
        # 発声終了位置(右ブランクの符号ごとの挙動違いに対応)
        t_end = int(time_order_ratio * oto.cutoff2)
        # 最終ノートをリストに追加
        lines.append([t_start, t_end, oto.alias])

    else:
        raise ValueError('argument \'mode\' must be in {}'.format(allowed_modes))

    # Labelクラスオブジェクト化
    label = _label.Label()
    label.values = lines
    return label


def label2otoini(label, name_wav,
                 otoini_time_order=10**(-3), label_time_order=10**(-7)):
    """
    LabelオブジェクトをOtoIniオブジェクトに変換
    モノフォン、CV、VCV とかの選択肢が必要そう
    otoini_time_order: otoiniの時間オーダー。
    label_time_order : ラベルの時間オーダー。
    """
    time_order_ratio = label_time_order / otoini_time_order

    l = []  # Otoオブジェクトを格納するリスト
    lines = label.values

    # ラベルの各行をOtoオブジェクトに変換して、リストにまとめる。
    for line in lines:
        line = [v * time_order_ratio for v in line[:2]] + line[2:]
        duration = line[1] - line[0]  # 発声の長さ
        oto = _otoini.Oto()
        oto.filename = name_wav
        oto.alias = line[2]
        oto.offset = line[0]
        oto.overlap = 0.0
        oto.preutterance = 0.0
        oto.consonant = duration
        oto.cutoff = - duration
        l.append(oto)

    # Otoiniオブジェクト化
    o = _otoini.OtoIni()
    o.values = l
    return o


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass

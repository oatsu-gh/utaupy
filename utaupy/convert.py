#! /usr/bin/env python3
# coding: utf-8
"""
UTAU関連ファイルの相互変換
"""
# from pysnooper import snoop
# from pprint import pprint


# from . import reaper as _reaper
# from . import reclist as _reclist
# from . import table as _table
from . import label as _label
from . import otoini as _otoini
from . import ust as _ust


def main():
    """ここ書く必要なくない？"""
    print('AtomとReaperが好き')


def svp2ust(svp, debug=False):
    """
    svpファイルを受け取って、簡易的なustオブジェクトにする。
    """
    svnotes = svp['tracks'][0]['mainGroup']['notes']

    # ust.Noteを入れておくリスト
    ust = _ust.Ust()
    # バージョン情報の空ノートを追加
    utaunote = _ust.Note()
    ust.append(utaunote)
    # プロジェクト設定のノートを追加
    utaunote = _ust.Note()
    utaunote.set_by_key('Tempo', svp['time']['tempo'][0]['bpm'])
    ust.append(utaunote)

    # 前奏の休符を追加
    utaunote = _ust.Note()
    utaunote.lyric = 'R'
    utaunote.length = svnotes[0]['onset'] // 1470000
    ust.append(utaunote)

    # DEBUG: 休符が挟まってるかどうかを判定して、休符を追加する処理を実装する必要がある。
    for svnote in svnotes:
        utaunote = _ust.Note()
        utaunote.lyric = svnote['lyrics']
        utaunote.length = svnote['duration'] // 1470000
        ust.append(utaunote)
        if debug:
            print(utaunote.values)
    return ust


def ust2otoini(ust, name_wav, d_table, mode='romaji_cv', dt=100, replace=True, debug=False):
    """
    UstクラスオブジェクトからOtoIniクラスオブジェクトを生成
    機能選択部分
    """
    allowed_modes = ['mono', 'romaji_cv']
    if mode == 'romaji_cv':
        print('  変換モード : ひらがな歌詞 → ローマ字CV')
        otoini = ust2otoini_romaji_cv(ust, name_wav, d_table, dt, replace=replace, debug=debug)
    elif mode == 'mono':
        print('  変換モード : ひらがな歌詞 → ローマ字モノフォン')
        otoini = ust2otoini_mono(ust, name_wav, d_table, debug=debug)
    else:
        raise ValueError('argument \'mode\' must be in {}'.format(allowed_modes))
    return otoini


def ust2otoini_mono(ust, name_wav, d_table, dt=100, debug=False):
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
    ust.make_finalnote_R()  # 最終ノートが休符じゃない場合を対策

    # UstのNoteオブジェクトごとにOtoオブジェクトを生成
    kana_otoini = _otoini.OtoIni()  # simple_otoを入れるリスト
    t = 0  # ノート開始時刻を記録
    for note in ust[2:-1]:
        length = note.length_ms
        simple_oto = _otoini.Oto()  # 各パラメータ位置を両端に集めたOto
        simple_oto.filename = name_wav
        simple_oto.alias = note.lyric
        simple_oto.offset = t
        simple_oto.overlap = 0
        simple_oto.preutterance = 0
        simple_oto.consonant = length
        simple_oto.cutoff = -length  # 負で左ブランク相対時刻, 正で絶対時刻
        kana_otoini.append(simple_oto)
        t += length  # 今のノート終了位置が次のノート開始位置

    # Otoを音素ごとに分割
    mono_otoini = _otoini.OtoIni()  # mono_otoを入れるリスト
    for simple_oto in kana_otoini:
        if debug:
            print(f'    {simple_oto.values}')
        try:
            phonemes = d_table[simple_oto.alias]
        except KeyError as e:
            print('KeyError in utaupy.convert.ust2otoini_mono---------')
            print('ひらがなローマ字変換に失敗しました。半角スペースで音素分割してぶち込みます。')
            print('エラー詳細:', e)
            print('--------------------------------------\n')
            phonemes = simple_oto.alias.split()
            print(phonemes)
        # 子音+母音 「か(k a)」
        if len(phonemes) == 2:
            # 子音部分
            oto = _otoini.Oto()
            oto.filename = name_wav
            oto.alias = phonemes[0]
            oto.offset = simple_oto.offset - (2 * dt)
            oto.overlap = 0
            oto.preutterance = dt
            oto.consonant = 2 * dt
            oto.cutoff = - 2 * dt
            mono_otoini.append(oto)
            # 母音部分
            oto = _otoini.Oto()
            oto.filename = name_wav
            oto.alias = phonemes[1]
            oto.offset = simple_oto.offset - dt
            oto.overlap = 0
            oto.preutterance = dt
            oto.consonant = 2 * dt
            oto.cutoff = simple_oto.cutoff - dt
            mono_otoini.append(oto)
        # 母音など 「あ(a)」「ん(cl)」「っ(cl)」「(pau)」「(br)」「(sil)」
        elif len(phonemes) == 1:
            oto = _otoini.Oto()
            oto.filename = name_wav
            oto.alias = phonemes[0]
            oto.offset = simple_oto.offset - dt
            oto.overlap = 0
            oto.preutterance = dt
            oto.consonant = 2 * dt
            oto.cutoff = simple_oto.cutoff - dt
            mono_otoini.append(oto)
        # 子音+半母音+母音 「ぐぁ(g w a)」
        elif len(phonemes) == 3:
            # 子音部分
            oto = _otoini.Oto()
            oto.filename = name_wav
            oto.alias = phonemes[0]
            oto.offset = simple_oto.offset - (2 * dt)
            oto.overlap = 0
            oto.preutterance = dt
            oto.consonant = 2 * dt
            oto.cutoff = - 2 * dt
            mono_otoini.append(oto)
            # 半母音部分
            oto = _otoini.Oto()
            oto.filename = name_wav
            oto.alias = phonemes[1]
            oto.offset = simple_oto.offset - dt
            oto.overlap = 0
            oto.preutterance = dt
            oto.consonant = 2 * dt
            oto.cutoff = - 2 * dt
            mono_otoini.append(oto)
            # 母音部分
            oto = _otoini.Oto()
            oto.filename = name_wav
            oto.alias = phonemes[2]
            oto.offset = simple_oto.offset
            oto.overlap = 0
            oto.preutterance = dt
            oto.consonant = 2 * dt
            oto.cutoff = simple_oto.cutoff - (2 * dt)
            mono_otoini.append(oto)
        else:
            raise ValueError('len(alias) must be in [1, 2, 3]')

    mono_otoini[0].offset = 0
    mono_otoini[0].preutterance = 0
    return mono_otoini


def ust2otoini_romaji_cv(ust, name_wav, d_table, dt=100, replace=True, debug=False):
    """
    UstクラスオブジェクトからOtoIniクラスオブジェクトを生成
    dt   : 左ブランク - オーバーラップ - 先行発声 - 固定範囲と右ブランク の距離
    mode : otoiniのエイリアス種別選択
    【パラメータ設定図】
      | 左ブランク |オーバーラップ| 先行発声 | 固定範囲 |   右ブランク   |
      |   (dt)ms   |    (dt)ms    |  (dt)ms  |  (dt)ms  | (length-2dt)ms |
    """
    ust.make_finalnote_R()  # 最終ノートが休符じゃない場合を対策
    otoini = _otoini.OtoIni()
    t = 0  # ノート開始時刻を記録

    # NOTE: ここnotes[2:-1]とust.values[2:-1]で処理時間に差は出る？
    for note in ust[2:-1]:
        if debug:
            print(f'    {ust}')
        try:
            phonemes = d_table[note.lyric]
        except KeyError as e:
            print(f'    [WARN] KeyError in utaupy.convert.ust2otoini_romaji_cv : {e}')
            phonemes = note.lyric.split()

        length = note.length_ms
        oto = _otoini.Oto()
        oto.filename = name_wav     # wavファイル名
        if replace:
            oto.alias = ' '.join(phonemes)  # エイリアスは音素ごとに空白区切り
        else:
            oto.alias = note.lyric
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
            print('\n[WARN] when setting alias : phonemes = {}-------------'.format(phonemes))
            print('1エイリアスあたり 1, 2, 3 音素しか対応していません。')
            oto.alias = ''.join(phonemes)
            oto.overlap = 0

        otoini.append(oto)
        t += length  # 今のノート終了位置が次のノート開始位置

    # 最初が休符なことを想定して、
    otoini[0].offset = 0  # 最初の左ブランクを0にする
    otoini[0].overlap = 0  # 最初のオーバーラップを0にする
    otoini[0].preutterance = 0  # 最初の先行発声を0にする
    otoini[0].cutoff2 -= 2 * dt
    return otoini


def otoini2label(otoini, mode='auto', debug=False):
    """
    OtoIniクラスオブジェクトからLabelクラスオブジェクトを生成
    発声開始: オーバーラップ
    発声終了: 次のノートのオーバーラップ
    発音記号: エイリアス流用
    otoini_time_order: otoiniの時間単位の桁。
    label_time_order : ラベルの時間単位の桁。
    """
    time_order_ratio = 10000
    # time_order_ratio = otoini_time_order / label_time_order
    # print('  time_order_ratio:', time_order_ratio)

    allowed_modes = ['auto', 'mono', 'romaji_cv']
    # エイリアスのタイプ自動判別
    if mode == 'auto':
        if otoini.is_mono():
            mode = 'mono'
        else:
            mode = 'romaji_cv'
    if mode == 'romaji_cv':
        print('  mode: OtoIni(romaji_cv) -> Label(mono)')
        # モノフォン化
        otoini = otoini.monophonize()
    elif mode == 'mono':
        print('  mode: OtoIni(mono) -> Label(mono)')
    else:
        raise ValueError('argument \'mode\' must be in {}'.format(allowed_modes))

    # 計算の重複を避けるために [[発音開始時刻, 発音記号], ...] の仮リストにする
    tmp = []
    for oto in otoini:
        if debug:
            print(f'    {oto.values}')
        t_start = int(time_order_ratio * (oto.offset + oto.preutterance))
        tmp.append([t_start, oto.alias])

    # OtoオブジェクトをPhonemeオブジェクトに変換する
    label = _label.Label()
    for i, v in enumerate(tmp[:-1]):
        phoneme = _label.Phoneme()
        phoneme.start = v[0]
        phoneme.end = tmp[i + 1][0]
        phoneme.symbol = v[1]
        label.append(phoneme)

    # 最終Otoだけ終了位置が必要なので 特別な処理
    oto = otoini[-1]
    phoneme = _label.Phoneme()
    phoneme.start = int(time_order_ratio * (oto.offset + oto.preutterance))
    phoneme.end = int(time_order_ratio * oto.cutoff2)  # 発声終了位置は右ブランク
    phoneme.symbol = tmp[-1][1]
    label.append(phoneme)

    return label


def label2otoini(label, name_wav):
    """
    LabelオブジェクトをOtoIniオブジェクトに変換
    モノフォン、CV、VCV とかの選択肢が必要そう
    otoini_time_order: otoiniの時間オーダー。
    label_time_order : ラベルの時間オーダー。
    """
    # time_order_ratio = label_time_order / otoini_time_order
    time_order_ratio = 10**(-4)

    otoini = _otoini.OtoIni()
    # 各音素PhonemeオブジェクトをOtoオブジェクトに変換して、OtoIniに格納する。
    for phoneme in label:
        oto = _otoini.Oto()
        oto.filename = name_wav
        oto.alias = phoneme.symbol
        oto.offset = phoneme.start * time_order_ratio
        oto.overlap = 0.0
        oto.preutterance = 0.0
        oto.consonant = (phoneme.end - phoneme.start) * time_order_ratio
        oto.cutoff = - (phoneme.end - phoneme.start) * time_order_ratio
        otoini.append(oto)
    return otoini


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass

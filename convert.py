#!/usr/bin/env python3
# coding: utf-8
"""
UTAU関連ファイルの相互変換
"""
from . import label, otoini, table

# from . import ust
# from pysnooper import snoop


def main():
    """ここ書く必要なくない？"""
    print('AtomとReaperが好き')


def ust2otoini(ustobj, name_wav, path_tablefile, mode='romaji_cv', dt=100):
    """
    UstクラスオブジェクトからOtoIniクラスオブジェクトを生成
    機能選択部分
    """
    allowed_modes = ['mono', 'romaji_cv']
    if mode == 'romaji_cv':
        otoiniobj = ust2otoini_romaji_cv(ustobj, name_wav, dt)
        otoiniobj.kana2romaji(path_tablefile)
    elif mode == 'mono':
        otoiniobj = ust2otoini_mono(ustobj, name_wav, path_tablefile)
    else:
        raise ValueError('argument \'mode\' must be in {}'.format(allowed_modes))
    return otoiniobj


def ust2otoini_mono(ustobj, name_wav, path_tablefile, dt=100):
    """
    UstクラスオブジェクトからOtoIniクラスオブジェクトを生成
    vowel_otoの対称は母音以外に 'N', 'cl' なども含まれる。    mode : otoiniのエイリアス種別選択
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
    d = table.load(path_tablefile)  # ひらがなローマ字対応表の辞書
    d.update({'R': ['pau'], 'pau': ['pau'], 'br': ['br'], 'sil': ['sil']})
    notes = ustobj.values
    tempo = ustobj.tempo

    l = []  # simple_otoを入れるリスト
    t = 0  # ノート開始時刻を記録
    for note in notes[2:-1]:
        length = note.get_length_ms(tempo)
        simple_oto = otoini.Oto()
        simple_oto.filename = name_wav
        simple_oto.alies = note.lyric
        simple_oto.lblank = t
        simple_oto.overlap = 0
        simple_oto.onset = 0
        simple_oto.fixed = length
        simple_oto.rblank = -length  # 負で左ブランク相対時刻, 正で絶対時刻
        l.append(simple_oto)
        t += length  # 今のノート終了位置が次のノート開始位置
    # 音素単位に分割
    new = []  # mono_otoを入れるリスト
    for simple_oto in l:
        phones = d[simple_oto.alies]
        # 子音+母音 「か(k a)」
        if len(phones) == 2:
            # 子音部分
            first_oto = otoini.Oto()
            first_oto.filename = name_wav
            first_oto.alies = phones[0]
            first_oto.lblank = simple_oto.lblank - (2 * dt)
            first_oto.overlap = 0
            first_oto.onset = dt
            first_oto.fixed = 2 * dt
            first_oto.rblank = - 2 * dt
            new.append(first_oto)
            # 母音部分
            second_oto = otoini.Oto()
            second_oto.filename = name_wav
            second_oto.alies = phones[1]
            second_oto.lblank = simple_oto.lblank - dt
            second_oto.overlap = 0
            second_oto.onset = dt
            second_oto.fixed = 2 * dt
            second_oto.rblank = simple_oto.rblank - dt
            new.append(second_oto)
        # 母音など 「あ(a)」「ん(cl)」「っ(cl)」「(pau)」「(br)」「(sil)」
        elif len(phones) == 1:
            first_oto = otoini.Oto()
            first_oto.filename = name_wav
            first_oto.alies = phones[0]
            first_oto.lblank = simple_oto.lblank - dt
            first_oto.overlap = 0
            first_oto.onset = dt
            first_oto.fixed = 2 * dt
            first_oto.rblank = simple_oto.rblank - dt
            new.append(first_oto)
        # 子音+半母音+母音 「ぐぁ(g w a)」
        elif len(phones) == 3:
            # 子音部分
            first_oto = otoini.Oto()
            first_oto.filename = name_wav
            first_oto.alies = phones[0]
            first_oto.lblank = simple_oto.lblank - (2 * dt)
            first_oto.overlap = 0
            first_oto.onset = dt
            first_oto.fixed = 2 * dt
            first_oto.rblank = - 2 * dt
            new.append(first_oto)
            # 半母音部分
            second_oto = otoini.Oto()
            second_oto.filename = name_wav
            second_oto.alies = phones[1]
            second_oto.lblank = simple_oto.lblank - dt
            second_oto.overlap = 0
            second_oto.onset = dt
            second_oto.fixed = 2 * dt
            second_oto.rblank = - 2 * dt
            new.append(second_oto)
            # 母音部分
            third_oto = otoini.Oto()
            third_oto.filename = name_wav
            third_oto.alies = phones[2]
            third_oto.lblank = simple_oto.lblank
            third_oto.overlap = 0
            third_oto.onset = dt
            third_oto.fixed = 2 * dt
            third_oto.rblank = simple_oto.rblank - (2 * dt)
            new.append(third_oto)
        else:
            raise ValueError('len(alies) must be in [1, 2, 3]')

    mono_otoini = otoini.OtoIni()
    mono_otoini.values = new
    return mono_otoini


def ust2otoini_romaji_cv(ustobj, name_wav, dt=100):
    """
    UstクラスオブジェクトからOtoIniクラスオブジェクトを生成
    dt   : 左ブランク - オーバーラップ - 先行発声 - 固定範囲と右ブランク の距離
    mode : otoiniのエイリアス種別選択
    【パラメータ設定図】
      | 左ブランク |オーバーラップ| 先行発声 | 固定範囲 |   右ブランク   |
      |   (dt)ms   |    (dt)ms    |  (dt)ms  |  (dt)ms  | (length-2dt)ms |
    """
    notes = ustobj.values
    tempo = ustobj.tempo
    o = otoini.OtoIni()
    l = []  # otoini生成元にするリスト
    t = 0  # ノート開始時刻を記録

    for note in notes[2:-1]:
        length = note.get_length_ms(tempo)
        oto = otoini.Oto()
        oto.filename = name_wav
        oto.alies = note.lyric
        oto.lblank = t - (2 * dt)
        oto.overlap = dt
        oto.onset = 2 * dt
        oto.fixed = min(3 * dt, length + 2 * dt)
        oto.rblank = -(length + 2 * dt)  # 負で左ブランク相対時刻, 正で絶対時刻
        l.append(oto)
        t += length  # 今のノート終了位置が次のノート開始位置

    l[0].lblank = 0  # 最初の左ブランクを0にする
    l[0].ovealap = 0  # 最初のオーバーラップを0にする
    o.values = l
    return o


def otoini2label(otoiniobj, mode='auto', otoini_time_order=10**(-3), label_time_order=10**(-7)):
    """
    OtoIniクラスオブジェクトからLabelクラスオブジェクトを生成
    発声開始: オーバーラップ
    発声終了: 次のノートのオーバーラップ
    発音記号: エイリアス流用
    otoini_time_order: otoiniの時間単位の桁。
    label_time_order : ラベルの時間単位の桁。
    """
    otoini_values = otoiniobj.values
    time_order_ratio = otoini_time_order / label_time_order
    print('time_order_ratio:', time_order_ratio)

    allowed_modes = ['auto', 'mono', 'romaji_cv']
    # エイリアスのタイプ自動判別
    if mode == 'auto':
        if otoiniobj.is_mono():
            mode = 'mono'
        else:
            mode = 'romaji_cv'

    if mode == 'mono':
        print('mode: OtoIni(mono) -> Label(mono)')
        # [[発音開始時刻, 発音記号], ...] の仮リストにする
        tmp = []
        for oto in otoini_values:
            t_start = (oto.lblank + oto.onset) * time_order_ratio
            tmp.append([t_start, oto.alies])
            # [[発音開始時刻, 発音終了時刻, 発音記号], ...]
        lines = [[v[0], tmp[i + 1][0], v[1]] for i, v in enumerate(tmp[:-1])]
        # ↓内包表記を展開した場合↓-----
        # lines = []
        # for i, v in enumerate(tmp[:-1]):
        #     lines.append([v[0], tmp[i+1][0], v[1]])
        # -------------------------------
        # 最終ノートの処理
        last_oto = otoini_values[-1]
        # 発声開始位置
        t_start = (last_oto.lblank + last_oto.onset) * time_order_ratio
        # 発声終了位置(右ブランクの符号ごとの挙動違いに対応)
        t_end = last_oto.rblank2 * time_order_ratio
        # 最終ノートをリストに追加
        lines.append([t_start, t_end, last_oto.alies])

    elif mode == 'romaji_cv':
        print('mode: OtoIni(romaji_cv) -> Label(mono)')
        # [[発音開始時刻, 発音記号], ...] の仮リストにする
        tmp = []
        for oto in otoini_values:
            t_start = (oto.lblank + oto.overlap) * time_order_ratio
            tmp.append([t_start, oto.alies])

        # [[発音開始時刻, 発音終了時刻, 発音記号], ...]
        lines = [[v[0], tmp[i + 1][0], v[1]] for i, v in enumerate(tmp[:-1])]
        # ↓内包表記を展開した場合↓-----
        # lines = []
        # for i, v in enumerate(tmp[:-1]):
        #     lines.append([v[0], tmp[i+1][0], v[1]])
        # -------------------------------

        # 最終ノートの処理
        last_oto = otoini_values[-1]
        # 発声開始位置
        t_start = (last_oto.lblank + last_oto.overlap) * time_order_ratio
        # 発声終了位置(右ブランクの符号ごとの挙動違いに対応)
        t_end = last_oto.rblank2 * time_order_ratio
        # 最終ノートをリストに追加
        lines.append([t_start, t_end, last_oto.alies])

    else:
        raise ValueError('argument \'mode\' must be in {}'.format(allowed_modes))

    # Labelクラスオブジェクト化
    lab = label.Label()
    lab.values = lines
    return lab

def label2otoini(labelobj, name_wav,
                 otoini_time_order=10**(-3), label_time_order=10**(-7)):
    """
    LabelオブジェクトをOtoIniオブジェクトに変換
    モノフォン、CV、VCV とかの選択肢が必要そう
    otoini_time_order: otoiniの時間単位の桁。
    label_time_order : ラベルの時間単位の桁。
    """
    time_order_ratio = label_time_order / otoini_time_order
    # Otoオブジェクトを格納するリスト
    l = []
    lines = labelobj.values
    for line in lines:
        line = [v * time_order_ratio for v in line[:2]] + line[2:]
        t = line[1] - line[0]
        oto = otoini.Oto()
        oto.filename = name_wav
        oto.alies = line[2]
        oto.lblank = line[0]
        oto.overlap = 0.0
        oto.onset = 0.0
        oto.fixed = t
        oto.rblank = -t
        l.append(oto)
    # クラスオブジェクト化
    o = otoini.OtoIni()
    o.values = l
    return o


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass

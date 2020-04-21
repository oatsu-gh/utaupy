#!/usr/bin/env python3
# coding: utf-8
"""
UTAU関連ファイルの相互変換
"""
from . import label, otoini

# from . import ust
# from pysnooper import snoop


def main():
    """ここ書く必要なくない？"""
    print('AtomとReaperが好き')


def ust2otoini(ustobj, name_wav, dt=100):
    """
    UstクラスオブジェクトからOtoIniクラスオブジェクトを生成
    dt     : 左ブランクと先行発声の時間距離
    overlap: オーバーラップと先行発声の距離
    【パラメータ設定図】
      | 左ブランク |オーバーラップ| 先行発声 | 固定範囲 |   右ブランク   |
      |   (dt)ms   |    (dt)ms    |  (dt)ms  |  (dt)ms  | (length-2dt)ms |
    """
    notes = ustobj.values
    tempo = ustobj.tempo
    o = otoini.OtoIni()
    l = []
    t = 0
    for note in notes[2:-1]:
        length = note.get_length_ms(tempo)
        oto = otoini.Oto()
        oto.filename = name_wav
        oto.alies = note.lyric
        oto.lblank = max(t - (2 * dt), 0)
        oto.overlap = dt
        oto.onset = 2 * dt
        oto.fixed = min(3 * dt, length + 2 * dt)
        # oto.fixed = length + 2 * dt
        oto.rblank = -(length + 2 * dt)  # 負で左ブランク相対時刻, 正で絶対時刻
        l.append(oto)
        t += length  # 今のノート終了位置が次のノート開始位置
    o.values = l
    return o


def otoini2label(otoiniobj, otoini_time_order=10**(-3), label_time_order=1):
    """
    OtoIniクラスオブジェクトからLabelクラスオブジェクトを生成
    発声開始: オーバーラップ
    発声終了: 次のノートのオーバーラップ
    発音記号: エイリアス流用
    label_time_order: ラベルの時間単位の桁。
    """
    otoini_values = otoiniobj.values
    time_order_ratio = otoini_time_order / label_time_order
    print('time_order_ratio:', time_order_ratio)

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
    lblank = last_oto.lblank
    rblank = last_oto.rblank
    # 発声開始位置
    t_start = (lblank + last_oto.overlap) * time_order_ratio
    # 発声終了位置
    # 右ブランクの符号ごとの挙動違いに対応
    t_end = max(rblank, lblank - rblank) * time_order_ratio
    # 最終ノートをリストに追加
    lines.append([t_start, t_end, last_oto.alies])

    # Labelクラスオブジェクト化
    lab = label.Label()
    lab.values = lines
    return lab


def label2otoini(labelobj, name_wav, otoini_time_order=10**(-3), label_time_order=1):
    """
    LabelオブジェクトをOtoIniオブジェクトに変換
    モノフォン、CV、VCV とかの選択肢が必要そう
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

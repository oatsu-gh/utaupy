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


def otoini2label(otoiniobj):
    """
    OtoIniクラスオブジェクトからLabelクラスオブジェクトを生成
    発声開始: オーバーラップ
    発声終了: 次のノートのオーバーラップ
    発音記号: エイリアス流用
    """
    otolist = otoiniobj.values
    lab = label.Label()

    # [[発音開始時刻, 発音記号], ...] の仮リストにする
    tmp = []
    for oto in otolist:
        t = (oto.lblank + oto.overlap) / 1000
        s = oto.alies
        tmp.append([t, s])

    # 一つのリストにまとめる
    l = [[v[0], tmp[i + 1][0], v[1]] for i, v in enumerate(tmp[:-1])]
    # ↓内包表記を展開した場合↓
    # l = []
    # for i, v in enumerate(tmp[:-1]):
    #     l.append([v[0], tmp[i+1][0], v[1]])

    # 最終ノートの処理
    v = tmp[-1]
    rblank = otolist[-1].rblank / 1000
    t_end = max(rblank, v[0] - rblank)  # 右ブランクの符号ごとの挙動違いに対応
    l.append([v[0], t_end, v[1]])

    # Labelクラスオブジェクト化
    lab.values = l
    return lab


def label2otoini(labelobj, name_wav):
    """
    LabelオブジェクトをOtoIniオブジェクトに変換
    モノフォン、CV、VCV とかの選択肢が必要そう
    """
    # Otoオブジェクトを格納するリスト
    otolist = []
    for line in labelobj.values:
        line = [v * 1000 for v in line[:2]] + line[2:]  # 単位換算(s -> ms)
        t = line[1] - line[0]
        oto = otoini.Oto()
        oto.filename = name_wav
        oto.alies = line[2]
        oto.lblank = line[0]
        oto.overlap = 0.0
        oto.onset = 0.0
        oto.fixed = t
        oto.rblank = -t
        otolist.append(oto)
    # クラスオブジェクト化
    o = otoini.OtoIni()
    o.values = otolist
    return o


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass

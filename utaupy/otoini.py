#! /usr/bin/env python3
# Copyright (c) oatsu
"""
setParam用のINIファイルとデータを扱うモジュールです。
"""

import re
from collections import UserList

# TODO: setParam用のコメントファイルを扱えるようにする。


def main():
    """
    直接実行されたときの挙動
    """
    print('耳ロボPとsetParamに卍感謝卍')


def load(path, mode='r', encoding='cp932'):
    """
    otoiniを読み取ってオブジェクト生成
    """
    # otoiniファイルを読み取る
    path = str(path).strip('"')
    with open(path, mode=mode, encoding=encoding) as f:
        lines = [line.strip() for line in f.readlines()]

    # Otoクラスオブジェクトのリストを作る
    otoini = OtoIni()
    for line in lines:
        params = re.split('[=,]', line.strip())
        params = params[:2] + [float(v) for v in params[2:]]
        oto = Oto()
        (
            oto.filename,
            oto.alias,
            oto.offset,
            oto.consonant,
            oto.cutoff,
            oto.preutterance,
            oto.overlap,
        ) = params
        otoini.append(oto)
    return otoini


class OtoIni(UserList):
    """
    oto.iniを想定したクラス
    """

    def replace_aliases(self, before, after):
        """
        エイリアスを置換する
        """
        for oto in self:
            oto.alias = oto.alias.replace(before, after)
        return self

    def apply_regex(self, func, *args, pattern=None):
        """
        エイリアスが正規表現に完全一致したら、その行で関数を実行する。

        Parameters:
            func (function): 対象行に実行する関数名。
            *args (Tuple): funcの引数。複数可能。
            pattern (str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。
        """
        # 正規表現がNone以外なら、正規表現に完全一致した行をフィルタリング
        if pattern is not None:
            regex = re.compile(rf'{pattern}')
            filtered_otos = [oto for oto in self if regex.fullmatch(oto.alias)]
        # 違えば全行をフィルタリング
        else:
            filtered_otos = list(self)

        # フィルタリングした行に関数を実行
        [func(oto, *args) for oto in filtered_otos]
        return self

    def drop_duplicates(self, keep='first'):
        """
        重複行を削除する。対象は全行。

        Parameters:
            keep (str): 'first' の時は最初の行を残し、'last' の時は最後の行を残す。
        """
        seen_aliases = set()  # 確認済みのエイリアス
        index_map = {}  # 最初または最後の出現位置

        for index, oto in enumerate(self):
            # firstのとき
            if keep == 'first':
                if oto.alias not in seen_aliases:
                    seen_aliases.add(oto.alias)
                    index_map[oto.alias] = index
            # lastのとき
            elif keep == 'last':
                index_map[oto.alias] = index

        unique_otoini = [self[index] for index in sorted(index_map.values())]

        self.data = unique_otoini
        return self

    def round(self, digits=3, pattern=None):
        """
        小数点以下の桁数を指定して四捨五入する。

        Parameters:
            digits (int): 小数点以下の桁数。0は整数。省略時は3。
            pattern (str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。
        """
        # 入力を整数として取得
        digits = int(digits)

        # 一致した行 or 全行で四捨五入
        def round_func(oto):
            oto.offset = round(oto.offset, digits)
            oto.consonant = round(oto.consonant, digits)
            oto.cutoff = round(oto.cutoff, digits)
            oto.preutterance = round(oto.preutterance, digits)
            oto.overlap = round(oto.overlap, digits)

        return self.apply_regex(round_func, pattern=pattern)

    def init_overlap_ratio(self, bpm=120, preutterance=None, ratio=1 / 3, pattern=None):
        """
        オーバーラップを先行発声で割る。乗算も可。
        先行発声、固定範囲、右ブランク(cutoff)の位置は変わらない。

        Parameters:
            bpm (float): 収録BPM。
            preutterance (float): 先行発声の固定値。省略時は収録BPMから計算する。
            ratio (float): 「1/3」と書くと1/3に、「1.5」と書くと1.5倍にする。
            pattern (str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。

        Example of Use:
            import utaupy
            path, otoing = setparam.load()
            # 収録BPM140で、オーバーラップを先行発声の1/3にする
            otoing.init_overlap_ratio(bpm=140, ratio=1/3)
        """
        if preutterance is not None:
            # 先行発声を入力したとき
            new_preutterance = float(preutterance)
            new_overlap = new_preutterance * ratio
        else:
            # 収録BPMを入力したとき
            bpm = float(bpm)
            new_preutterance = (60000 / bpm) / 2
            new_overlap = new_preutterance * ratio

        # 一致した行 or 全行で計算
        def overlap_ratio_func(oto):
            moving_value = oto.preutterance - new_preutterance
            oto.offset = oto.offset + moving_value
            oto.preutterance = new_preutterance
            oto.overlap = new_overlap
            oto.consonant -= moving_value
            if oto.cutoff < 0:  # マイナス値のcutoffは、offsetと連動して動く
                oto.cutoff += moving_value
            else:  # プラス値のcutoffは、offsetが動いても変わらない
                oto.cutoff = oto.cutoff

        return self.apply_regex(overlap_ratio_func, pattern=pattern)

    def is_mono(self):
        """
        モノフォン形式のエイリアスになっているか判定する。
        すべてのエイリアスに空白がなければモノフォンと判断する。
        返り値はbool。
        """
        return all((' ' not in oto.alias) for oto in self)

    def monophonize(self):
        """
        音素ごとに分割する。
        otoini→label 変換の用途を想定
        音素の発声開始位置: 左ブランク=先行発声
        """
        # 新規OtoIniを作るために、otoを入れるリスト
        mono_otoini = OtoIni()
        for oto in self:
            phonemes = oto.alias.split()
            if len(phonemes) == 1:
                mono_otoini.append(oto)
            elif len(phonemes) in [2, 3]:
                name_wav = oto.filename
                # 1文字目(オーバーラップから先行発声まで)------------
                mono_oto = Oto()
                mono_oto.filename = name_wav
                mono_oto.alias = phonemes[0]
                mono_oto.offset = (
                    oto.offset + oto.overlap
                )  # オーバーラップの位置に左ブランクを移動
                mono_oto.preutterance = 0
                mono_otoini.append(mono_oto)
                # 2文字目(先行発声から固定範囲まで)----------------
                mono_oto = Oto()
                mono_oto.filename = name_wav
                mono_oto.alias = phonemes[1]
                mono_oto.offset = oto.offset + oto.preutterance  # 先行発声の位置に左ブランクを移動
                mono_oto.preutterance = 0
                mono_otoini.append(mono_oto)
                if len(phonemes) == 3:
                    # 3文字目(固定範囲から右ブランクまで)----------------
                    mono_oto = Oto()
                    mono_oto.filename = name_wav
                    mono_oto.alias = phonemes[2]
                    mono_oto.offset = (
                        oto.offset + oto.consonant
                    )  # 固定範囲の位置に左ブランクを移動
                    mono_oto.preutterance = 0
                    mono_otoini.append(mono_oto)
            else:
                print('\n[ERROR in otoini.monophonize()]----------------')
                print('  1エイリアスの音素数は 1, 2, 3 以外対応していません。')
                print(f'  phonemes: {phonemes}')
                print('  文字を連結して処理を続行します。')
                print('-----------------------------------------------\n')
                mono_otoini.append(oto)
        return mono_otoini

    def write(self, path, mode='w', encoding='cp932'):
        """
        ファイル出力
        """
        s = '\n'.join([str(oto) for oto in self]) + '\n'
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s


class Oto:
    """
    oto.ini中の1モーラ
    """

    def __init__(self):
        self.filename: str = ''
        self.alias: str = ''
        self.offset = 0
        self.consonant = 0
        self.cutoff = 0
        self.preutterance = 0
        self.overlap = 0
        self.comment = None

    def __str__(self):
        s = '{}={},{},{},{},{},{}'.format(  # noqa: UP032
            self.filename,
            self.alias,
            round(float(self.offset), 4),
            round(float(self.consonant), 4),
            round(float(self.cutoff), 4),
            round(float(self.preutterance), 4),
            round(float(self.overlap), 4),
        )
        return s  # noqa: RET504

    @property
    def cutoff2(self):
        """
        右ブランクを絶対時刻で取得する
        """
        cutoff = self.cutoff
        if cutoff > 0:
            raise ValueError(f'Cutoff(右ブランク) must be negative : {str(self)}')
        return self.offset - cutoff

    @cutoff2.setter
    def cutoff2(self, absolute_cutoff_time):
        """
        右ブランクを絶対時刻で受け取り、負の値で上書きする
        """
        if absolute_cutoff_time < 0:
            raise ValueError(
                f'Argument "absolute_cutoff_time" must be positive : {absolute_cutoff_time}'  # noqa: E501
            )
        self.cutoff = self.offset - absolute_cutoff_time


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass

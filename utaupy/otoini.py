#! /usr/bin/env python3
# coding: utf-8
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
    path = path.strip('"')
    with open(path, mode=mode, encoding=encoding) as f:
        lines = [line.strip() for line in f.readlines()]

    # Otoクラスオブジェクトのリストを作る
    otoini = OtoIni()
    for line in lines:
        params = re.split('[=,]', line.strip())
        params = params[:2] + [float(v) for v in params[2:]]
        oto = Oto()
        (oto.filename, oto.alias, oto.offset, oto.consonant,
         oto.cutoff, oto.preutterance, oto.overlap) = params
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
                mono_oto.offset = oto.offset + oto.overlap  # オーバーラップの位置に左ブランクを移動
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
                    mono_oto.offset = oto.offset + oto.consonant  # 固定範囲の位置に左ブランクを移動
                    mono_oto.preutterance = 0
                    mono_otoini.append(mono_oto)
            else:
                print('\n[ERROR in otoini.monophonize()]----------------')
                print('  1エイリアスの音素数は 1, 2, 3 以外対応していません。')
                print('  phonemes: {}'.format(phonemes))
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
        s = '{}={},{},{},{},{},{}'.format(
            self.filename,
            self.alias,
            round(float(self.offset), 4),
            round(float(self.consonant), 4),
            round(float(self.cutoff), 4),
            round(float(self.preutterance), 4),
            round(float(self.overlap), 4)
        )
        return s

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
                f'Argument "absolute_cutoff_time" must be positive : {absolute_cutoff_time}')
        self.cutoff = self.offset - absolute_cutoff_time


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass

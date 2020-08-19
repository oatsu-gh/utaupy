#!python3
# coding: utf-8
"""
setParam用のINIファイルとデータを扱うモジュールです。
"""
import re

# from . import table


def main():
    """実行されたときの挙動"""
    print('耳ロボPとsetParamに卍感謝卍')


def load(path, mode='r', encoding='shift-jis'):
    """otoiniを読み取ってオブジェクト生成"""
    # otoiniファイルを読み取る
    with open(path, mode=mode, encoding=encoding) as f:
        l = [re.split('[=,]', s.strip()) for s in f.readlines()]
    # # 入力ファイル末尾の空白行を除去
    # while l[-1] == ['']:
    #     del l[-1]

    # Otoクラスオブジェクトのリストを作る
    otolist = []
    for v in l:
        oto = Oto()
        oto.from_otoini(v)
        otolist.append(oto)
    # OtoIniクラスオブジェクト化
    o = OtoIni()
    o.values = otolist
    return o


class OtoIni:
    """oto.iniを想定したクラス"""

    def __init__(self):
        # 'Oto'クラスからなるリスト
        self.__values = []

    @property
    def values(self):
        """中身を確認する"""
        return self.__values

    @values.setter
    def values(self, list_of_oto):
        """中身を上書きする"""
        self.__values = list_of_oto

    def replace_aliases(self, before, after):
        """エイリアスを置換する"""
        for oto in self.__values:
            oto.alias = oto.alias.replace(before, after)
        return self

    def is_mono(self):
        """
        モノフォン形式のエイリアスになっているか判定する。
        返り値はbool。
        """
        return all(len(v.alias.split()) == 1 for v in self.values)

    def kana2romaji(self, d_table, replace=True):
        """
        エイリアスをローマ字にする
        replace:
          Trueのときエイリアスをローマ字に書き換え
          Falseのときエイリアスは平仮名のまま
        """
        for oto in self.__values:
            try:
                oto.alias = ' '.join(d_table[oto.alias])
            except KeyError as e:
                print(f'[ERROR] KeyError in utaupy.otoini.OtoIni.kana2romaji: {e}')

    def monophonize(self):
        """
        音素ごとに分割する。
        otoini→label 変換の用途を想定
        音素の発声開始位置: 左ブランク=先行発声
        """
        # 新規OtoIniを作るために、otoを入れるリスト
        l = []
        for oto in self.__values:
            phonemes = oto.alias.split()
            if len(phonemes) == 1:
                l.append(oto)
            elif len(phonemes) in [2, 3]:
                name_wav = oto.filename
                # 1文字目(オーバーラップから先行発声まで)------------
                mono_oto = Oto()
                mono_oto.filename = name_wav
                mono_oto.alias = phonemes[0]
                mono_oto.offset = oto.offset + oto.overlap  # オーバーラップの位置に左ブランクを移動
                mono_oto.preutterance = 0
                l.append(mono_oto)
                # 2文字目(先行発声から固定範囲まで)----------------
                mono_oto = Oto()
                mono_oto.filename = name_wav
                mono_oto.alias = phonemes[1]
                mono_oto.offset = oto.offset + oto.preutterance  # 先行発声の位置に左ブランクを移動
                mono_oto.preutterance = 0
                l.append(mono_oto)
                if len(phonemes) == 3:
                    # 3文字目(固定範囲から右ブランクまで)----------------
                    mono_oto = Oto()
                    mono_oto.filename = name_wav
                    mono_oto.alias = phonemes[2]
                    mono_oto.offset = oto.offset + oto.consonant  # 固定範囲の位置に左ブランクを移動
                    mono_oto.preutterance = 0
                    l.append(mono_oto)
            else:
                print('\n[ERROR in otoini.monophonize()]----------------')
                print('  エイリアスの音素数は 1, 2, 3 以外対応していません。')
                print('  phonemes: {}'.format(phonemes))
                print('  文字を連結して処理を続行します。')
                print('-----------------------------------------------\n')
                l.append(oto)
        self.__values = l

    def write(self, path, mode='w', encoding='shift-jis'):
        """OtoIniクラスオブジェクトをINIファイルに出力"""
        s = ''
        for oto in self.__values:
            l = []
            l.append(oto.filename)
            l.append(oto.alias)
            l.append(oto.offset)
            l.append(oto.consonant)
            l.append(oto.cutoff)
            l.append(oto.preutterance)
            l.append(oto.overlap)
            # 数値部分を丸めてから文字列に変換
            l = l[:2] + [str(round(float(v), 4)) for v in l[2:]]
            s += '{}={},{},{},{},{},{}\n'.format(*l)  # 'l[0]=l[1],l[2],...'
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s


class Oto:
    """oto.ini中の1モーラ"""

    def __init__(self):
        keys = ('FileName', 'Alias', 'Offset',
                'Consonant', 'Cutoff', 'Preutterance', 'Overlap')
        tpl = (None, None, 0, 0, 0, 0, 0, 0)
        self.__d = dict(zip(keys, tpl))

    def __str__(self):
        return f'\'{self.alias}\'\t<utaupy.otoini.Oto object at {id(self)}>'

    def from_otoini(self, l):
        """1音分のリストをもらってクラスオブジェクトにする"""
        keys = ('FileName', 'Alias', 'Offset',
                'Consonant', 'Cutoff', 'Preutterance', 'Overlap')
        # 数値部分をfloatにする
        l = l[:2] + [float(v) for v in l[2:]]
        self.__d = dict(zip(keys, l))
        return self

    # ここからノートの全値の処理----------------------
    @property
    def values(self):
        """中身を確認する"""
        return self.__d

    @values.setter
    def values(self, d):
        """中身を上書きする"""
        self.__d = d
    # ここまでノートの全値の処理----------------------

    # ここからノートの各値の処理----------------------
    @property
    def filename(self):
        """wavファイル名を確認する"""
        return self.__d['FileName']

    @filename.setter
    def filename(self, x):
        """wavファイル名を上書きする"""
        self.__d['FileName'] = x

    @property
    def alias(self):
        """エイリアスを確認する"""
        return self.__d['Alias']

    @alias.setter
    def alias(self, x):
        """エイリアスを上書きする"""
        self.__d['Alias'] = x

    @property
    def offset(self):
        """左ブランクを確認する"""
        return self.__d['Offset']

    @offset.setter
    def offset(self, x):
        """左ブランクを上書きする"""
        self.__d['Offset'] = x

    @property
    def consonant(self):
        """固定範囲を確認する"""
        return self.__d['Consonant']

    @consonant.setter
    def consonant(self, x):
        """固定範囲を上書きする"""
        self.__d['Consonant'] = x

    @property
    def cutoff(self):
        """右ブランクを確認する"""
        return self.__d['Cutoff']

    @cutoff.setter
    def cutoff(self, x):
        """右ブランクを上書きする"""
        self.__d['Cutoff'] = x

    @property
    def cutoff2(self):
        """右ブランクを絶対時刻で取得する"""
        return max(self.__d['Cutoff'], self.__d['Offset'] - self.__d['Cutoff'])

    # OffsetがNullのとき処理できない
    @cutoff2.setter
    def cutoff2(self, x):
        """右ブランクを絶対時刻で受け取り、負の値で上書きする"""
        self.__d['Cutoff'] = self.__d['Offset'] - x

    @property
    def preutterance(self):
        """先行発声を取得する"""
        return self.__d['Preutterance']

    @preutterance.setter
    def preutterance(self, x):
        """先行発声を上書きする"""
        self.__d['Preutterance'] = x

    @property
    def overlap(self):
        """オーバーラップを取得する"""
        return self.__d['Overlap']

    @overlap.setter
    def overlap(self, x):
        """オーバーラップを上書きする"""
        self.__d['Overlap'] = x
    # ここまでノートの各値の処理----------------------


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass

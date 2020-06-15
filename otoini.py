#!/usr/bin/env python3
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
    # 入力ファイル末尾の空白行を除去
    while l[-1] == ['']:
        del l[-1]

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

    # def kana2romaji(self, path_table, replace=True, dt=100):
    #     """
    #     エイリアスをローマ字にする
    #     かな→ローマ字 変換表のパス
    #     replace:
    #       Trueのときエイリアスをローマ字に書き換え
    #       Falseのときエイリアスは平仮名のまま
    #     """
    #     # ローマ字変換表読み取り
    #     d = table.load(path_table)
    #     d.update({'R': ['pau'], 'pau': ['pau'], 'sil': ['sil'],
    #               '息': ['br'], '吸': ['br'], 'br': ['br']})
    #     # 発音記号の分割数によってパラメータを調整
    #     for oto in self.__values:
    #         kana = oto.alias.split()[-1]
    #         try:
    #             romaji = d[kana]
    #         # KeyErrorはリストにするだけで返される
    #         except KeyError as e:
    #             print('\n[KeyError in otoini.kana2romaji]---------')
    #             print('想定外の文字が kana として入力されました。')
    #             print('該当文字列(kana):', kana)
    #             print('エラー詳細(e)   :', e)
    #             print('--------------------------------------\n')
    #             romaji = d[kana]
    #         # 歌詞をローマ字化
    #         if replace is True:
    #             oto.alias = ' '.join(romaji)
    #         # モノフォン
    #         if len(romaji) == 1:
    #             # print('  alias: {}\t-> {}\t: オーバーラップ右シフト・先行発声右詰め'.format(alias, romaji))
    #             oto.overlap = 2 * dt
    #             oto.preutterance = oto.consonant
    #         # おもにCV形式のとき
    #         elif len(romaji) == 2:
    #             # print('  alias: {}\t-> {}\t: そのまま'.format(alias, romaji))
    #             pass
    #         # おもにCCV形式のとき
    #         elif len(romaji) == 3:
    #             # print('  alias: {}\t-> {}\t: そのままでいい？'.format(alias, romaji))
    #             pass
    #         elif len(romaji) >= 4:
    #             print('  [ERROR]---------')
    #             print('  1,2,3音素しか対応していません。')
    #             print('  alias: {}\t-> {}\t: そのままにします。'.format(kana, romaji))
    #             print('  ----------------')

    def monophonize(self):
        """音素ごとに分割"""
        # 新規OtoIniを作るために、otoを入れるリスト
        l = []
        for oto in self.__values:
            aliases = oto.alias.split()
            if len(aliases) == 1:
                l.append(oto)
            elif len(aliases) in [2, 3]:
                name_wav = oto.filename
                # 1文字目(オーバーラップから先行発声まで)------------
                tmp = Oto()
                a = aliases[0]
                t = oto.offset + oto.overlap  # オーバーラップの位置から
                tmp.filename = name_wav
                tmp.alias = a
                tmp.offset = t
                tmp.overlap = 0
                l.append(tmp)
                # 2文字目(先行発声から固定範囲まで)----------------
                tmp = Oto()
                a = aliases[1]
                t = oto.offset + oto.preutterance  # 先行発声の位置から
                tmp.filename = name_wav
                tmp.alias = a
                tmp.offset = t
                tmp.overlap = 0
                l.append(tmp)
                if len(aliases) == 3:
                    # 3文字目(固定範囲から右ブランクまで)----------------
                    tmp = Oto()
                    a = aliases[2]
                    t = oto.offset + oto.consonant  # 固定範囲の位置から
                    tmp.filename = name_wav
                    tmp.alias = a
                    tmp.offset = t
                    tmp.overlap = 0
                    l.append(tmp)
            else:
                print('\n[ERROR in otoini.monophonize()]----------------')
                print('エイリアスのローマ字分割数は 1, 2, 3 以外対応していません。')
                print('aliases: {}'.format(aliases))
                print('文字を連結して処理を続行します。')
                print('-----------------------------------------------\n')
                l.append(oto)
        self.values = l

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
        l = [None] * 7
        self.__d = dict(zip(keys, l))

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

    # OffsetがNullのとき処理できず、バグのもとになるので無効化
    # @cutoff2.setter
    # def cutoff2(self, x):
    #     """右ブランクを上書きする。負の値に強制する。"""
    #     self.__d['Cutoff'] = min(x, self.__d['Offset'] - x)

    @property
    def preutterance(self):
        """先行発声を確認する"""
        return self.__d['Preutterance']

    @preutterance.setter
    def preutterance(self, x):
        """先行発声を上書きする"""
        self.__d['Preutterance'] = x

    @property
    def overlap(self):
        """右ブランクを確認する"""
        return self.__d['Overlap']

    @overlap.setter
    def overlap(self, x):
        """右ブランクを上書きする"""
        self.__d['Overlap'] = x
    # ここまでノートの各値の処理----------------------


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass

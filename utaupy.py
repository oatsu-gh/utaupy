#!/usr/bin/env python3
# coding: utf-8
"""
UTAUのデータ整理用モジュール
クラスを使ってがんばる
"""
# import os
# from utaupy import ust
# from utaupy import convert

# def ust2ini_solo(path_ust, path_ini):
#     """USTファイルをINIファイルに変換する"""
#     basename = os.path.basename(path_ust)
#     print('converting UST->INI:', basename)
#     u = ust.load(path_ust)
#     o = convert.ust2otoini(u, basename)
#     o.write(path_ini)
#     return o

def main():
    """デバッグ用実装"""
    print('UST, otoini などを編集するためのモジュールです。')
    print('クラス Ust, Note, Otoini, Oto を実装済みです。')


if __name__ == '__main__':
    main()
    input('Press enter to exit.')

if __name__ == '__init__':
    print('ξ・ヮ・) < UtauPy imported.')

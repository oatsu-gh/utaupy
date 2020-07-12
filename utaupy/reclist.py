#!python3
# coding: utf-8
"""
UTAUの録音リストを扱うモジュール
録音リストは休憩する部分で空白行を入れてね
"""
import re
from pprint import pprint


def main():
    """直接実行されたときの動作"""
    print('---録音リストを扱うためのモジュールです。importして使ってね。---')
    print('録音リスト読み取り動作チェックをします。')
    # pathを標準入力
    path_reclist = input('録音リストのパスを入力してください。\n>>> ')
    # OREMOのコメントの扱いを質問
    oremo = input('OREMO用のコメントを含んでいますか？(Y/n)\n>>> ') in ['Y', 'y', 'Ｙ', 'ｙ']
    # 録音リストの空行の扱いを質問
    remove_blankline = input('空行を削除しますか？(Y/n)\n>>> ') in ['Y', 'y', 'Ｙ', 'ｙ']
    # 録音リストを読み取る
    l = load(path_reclist, remove_blankline=remove_blankline, oremo=oremo)
    print('\n取得結果---------------------------')
    pprint(l)
    print('-----------------------------------')


def load(path, mode='r', encoding='shift-jis', remove_blankline=True, oremo=False):
    """
    録音リストを読み取ってオブジェクト生成
    path    : 録音リストのパス
    mode    : ファイルをopen()するときののモード
    rmblank : 空行を削除するかどうか
    oremo   : 録音ソフトウェア「OREMO」用のコメントの有無。あるならTrue
    """
    # 録音リストのデータ用リスト
    l = []

    # OREMOのコメントを無視する
    if oremo:
        with open(path, mode=mode, encoding=encoding) as f:
            l = [line.strip().split()[0] for line in f.readlines()]
    # OREMOのコメントを無視しないが、全角スペースで分割する
    else:
        with open(path, mode=mode, encoding=encoding) as f:
            for line in f.readlines():
                l += re.split('[　 ]', line.strip())
    # 空行を削除する
    if remove_blankline:
        l = [v for v in l if v != '']

    return l


if __name__ == '__main__':
    main()
    input('Press Enter to exit.')

#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2024 八歌
"""
トライ木(辞書)を扱うモジュールです。
使用例はotoini.py(辞書作成例はcreate_cv_dict、使用例はconvert_cv)にあります。
"""


class TrieNode:
    """
    TrieNode: トライ木のノードを表すクラス。
    children: 子ノードを保持する辞書。
    is_end_of_word: 単語の終わりを示すフラグ。
    params: 追加のパラメータを保持。
    """
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.params = {}


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, **params):
        """
        文字列とそのパラメータをトライ木に挿入する。

        Parameters:
        params (dict): 文字列とそのパラメータを含む辞書。
        """
        chars = params.pop('chars', None)
        if not chars:
            raise ValueError("文字列を含む 'chars' パラメータが必要です")

        for word in chars:
            node = self.root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
            node.is_end_of_word = True
            node.params.update(params)

    def search(self, word):
        """
        指定された単語を検索し、そのパラメータを返す。

        Parameters:
        word (str): 検索する単語。

        Returns:
        dict: 単語が見つかった場合、そのパラメータを返す。見つからなければNone。
        """
        node = self.root
        for char in word:
            node = node.children.get(char)
            if not node:
                return None
        return node.params if node.is_end_of_word else None

    def parse_value(self, value):
        """
        文字列を数値に変換する。

        Parameters:
        value (str): 変換する文字列。

        Returns:
        int/float/str: 変換された数値または元の文字列。
        """
        try:
            return float(value) if '.' in value else int(value)
        except ValueError:
            return value

    def parse_and_insert(self, dict_data):
        """
        辞書データを解析してトライ木に挿入する。

        Parameters:
        dict_data (str): 辞書データの文字列。
        """
        for line in dict_data.strip().split('\n'):
            parts = [part.strip() for part in line.split(',')]
            params = {}
            for part in parts:
                if '=' in part:
                    key, value = part.split('=')
                    params[key.strip()] = self.parse_value(value.strip())
                else:
                    params.setdefault('chars', []).append(part.strip())
            self.insert(**params)


if __name__ == "__main__":
    pass

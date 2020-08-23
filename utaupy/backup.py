#!python
# coding: utf-8
# Copyright (c) oatsu
"""
入出力ファイルのバックアップを取りたいときに使う
"""

from datetime import datetime
from os import path, makedirs
from shutil import copy2


def backup_io(path_file, outdirname):
    """
    ファイル名に時刻を組み込んでバックアップ
    入出力ファイル向け。
    """
    # バックアップ用のフォルダを生成
    makedirs(f'backup/{outdirname}', exist_ok=True)

    basename, ext = path.splitext(path.basename(path_file))
    now = datetime.now().strftime('%Y%m%d_%H%M%S')

    copy2(path_file, f'backup/{outdirname}/{basename}__{now}{ext}')

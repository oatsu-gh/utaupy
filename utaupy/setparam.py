#! /usr/bin/env python3
# coding: utf-8
"""
setParamプラグインで設定(原音設定など)を読み込むモジュールです。
"""
import os
import sys
from utaupy import otoini as _otoini


def load():
    """
    setParamプラグインの汎用的な初期設定を行う。

    Reference:
        ・原音設定に対してできること: utaupy > otoini.py > class OtoIni
        ・原音設定以外も読み込むとき: def read_inparam 以降に記載

    Example of Use:
        import utaupy  # インポート
        path, otoing = setparam.load()  # 原音設定を読み込む、OtoIniクラスのインスタンス化
        otoing.round(1)  # 原音設定を編集(例: 小数点以下1桁で四捨五入)
        otoing.write(path)  # 原音設定を保存
    """
    path = read_inparam('oto_sp_path')
    otoini = _otoini.load(path)
    otoing = _otoini.OtoIni(otoini)
    return path, otoing


def read_inparam(key=None):
    """
    inParam.txtを読み込む。

    Reference:
        setParamプラグインの仕様: setParam.exeのあるフォルダ > plugins > README.txt

    Example of Use:
        import utaupy
        vb_dir = setparam.read_inparam('vb_dir')  # 一部だけ取得
        settings = setparam.read_inparam()  # もしくは全てを辞書として取得
        vb_dir = settings['vb_dir']  # 辞書の中から音源パスを取得
    """
    # inParam.txtを探す
    cur_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    par_dir = os.path.dirname(cur_dir)
    in_param_path = os.path.join(par_dir, 'inParam.txt')

    # inParam.txtを読み込む
    with open(in_param_path, 'r', encoding='cp932') as f:
        lines = [line.strip() for line in f.readlines()]
    vb_dir = lines[0]
    oto_sp_path = lines[1]
    f0_interval = float(lines[2])
    power_interval = float(lines[3])
    view_rows = int(lines[4])
    select_rows_str = lines[5]
    select_rows = (
        list(map(int, select_rows_str.split(',')))
        if ',' in select_rows_str
        else int(select_rows_str))

    # inParam.txtのパスを元に、残りのパスを取得
    oto_ini_path = os.path.join(vb_dir, 'oto.ini')
    comment_txt_path = os.path.join(vb_dir, 'oto-comment.txt')
    comment_sp_path = os.path.join(vb_dir, 'oto-autoEstimation-comment.txt')

    settings = {
        'cur_dir': cur_dir,  # プラグイン本体の保存フォルダのパス
        'vb_dir': vb_dir,  # 処理対象の音源フォルダのパス
        'oto_sp_path': oto_sp_path,  # 反映用の原音設定のパス(ここから読み、ここに保存すること)
        'oto_ini_path': oto_ini_path,  # 原音設定のパス
        'f0_interval': f0_interval,  # F0の抽出間隔(単位=秒)
        'power_interval': power_interval,  # パワーの抽出間隔(単位=秒)
        'view_rows': view_rows,  # setParamの波形窓で現在表示しているデータの行番号
        'select_rows': select_rows,  # setParamのパラメータ一覧表で現在選択しているセルの行番号
        'comment_sp_path': comment_sp_path,  # 反映用のsetParam用コメントテキストのパス
        'comment_txt_path': comment_txt_path,  # setParam用コメントテキストのパス
    }
    if key:
        return settings.get(key, None)
    return settings

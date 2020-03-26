# utaupy

UTAU周辺のデータ処理を行うPythonのパッケージです。READMEは書いてる途中です。

## 利用規約

- LICENSE ファイルをご覧ください。

- table/japanese.table は [きりたん歌唱DB](https://zunko.jp/kiridev/login.php) からコピーしたものです。

## 処理できるファイル

- .ust (UTAU)
- .ini (setParam)
- .lab (歌唱データベース用音素ラベル)
- .table (ローマ字かな対応表)

- UTAUプラグインの処理は準備中です（2020年3月26日時点）



## 機能概要

- INI, UST, LAB ファイルのデータをクラスオブジェクトとして扱います。
- INI, UST, LAB ファイルを相互変換できます。ただし不可逆の処理が多いです。



## 機能詳細

そのうち書きます

### ust, label, otoini, table

```
from utaupy import ust

ust_path = 'dirname/namae.ust'
u = ust.load(ust_path)
```

で UST ファイルをクラス Ust() として扱えます。LAB, INI を扱いたいときは  label, otoini を import してください。Ust() は Note() を要素として持つリスト型です。

```
for note in u.get_values():
    lyric = note.get_lyric()
    print(lyric)
```

と書けば歌詞を出力できます。一般的に紹介すると

- `note.set_xxxx(a)` でxxxxの値をaで上書きできます。

- `note.set_yyyy(a)` でyyyyの値をaで上書きできます。

### convert

各ファイルを変換できます。こんなかんじ↓

```
from utaupy import convert

u = ust.load(ust_path)     # USTファイルを読み取り
o = convert.ust2otoini(u)  # OtoIniクラスオブジェクトに変換

outpath = 'dirname/namae.ini' # INIファイルの出力パス
wav_name = 'sample.wav'       # INIファイルに記載するWAVファイル名
o.write(outpath, wav_name)    # ファイル出力
```



## 連絡先

- Twitter: @oatsu_c

- GitHub: oatsu-gh




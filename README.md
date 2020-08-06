# utaupy

UTAU周辺のデータ処理を行うPythonのパッケージです。READMEは書いてる途中です。

## 利用規約

LICENSE ファイルをご覧ください。

## 処理できるファイル

- .ust (UTAU)
- .txt (UTAU Plugin Script)
- .txt (録音リスト)
- .ini (setParam)
- .lab (歌唱データベース用音素ラベル)
- .table (ローマ字かな対応表)
- .svp (Synthesizer V R2)
- .csv (REAPER リージョン・マーカー用)



## 機能概要

- INI, UST, LAB ファイルのデータをクラスオブジェクトとして扱います。
- INI, UST, LAB ファイルを変換できます。ただし不可逆の処理が多いです。



## 機能詳細

そのうち書きます

### ust, label, otoini, table

```Python
from utaupy import ust

ust_path = 'dirname/namae.ust'
u = ust.load(ust_path)
```

で UST ファイルをクラス Ust() として扱えます。LAB, INI を扱いたいときは  label, otoini を import してください。Ust() は Note() を要素として持つリスト型です。

```Python
for note in u.values:
    lyric = note.lyric
    print(lyric)
```

property で getter と setter 設定してあるパラメータについては書き換えもできます。

```Python
note.lyric = 'あ'
print(note.lyric)  # 'あ'
```

### convert

各ファイルを変換できます。こんなかんじ↓

```Python
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

# utaupy
[![PyPI](https://img.shields.io/pypi/v/utaupy.svg)](https://pypi.python.org/pypi/utaupy)

UTAU周辺のデータ処理を行うPythonのパッケージです。READMEは書いてる途中です。
PythonでUTAUプラグインを作りたい場合は、C# 用の **[utauPlugin](https://github.com/delta-kimigatame/utauPlugin)** をPythonに移植した **[pyUtau](https://github.com/UtaUtaUtau/pyUtau)** のほうがいいかもしれません。ビブラートやピッチの扱いが便利そうです。

## 利用規約

LICENSE ファイルをご覧ください。

## 処理できるファイル

- .ust (UTAU)
- .txt (UTAU Plugin Script)
- .txt (録音リスト)
- .ini (setParam および UTAU音源原音設定)
- .lab (歌唱データベース用音素ラベル)
- .table (ローマ字かな対応表)
- .svp (Synthesizer V R2)
- .csv (REAPER リージョン・マーカー用)



## 機能概要

- INI, UST, LAB ファイルのデータをクラスオブジェクトとして扱います。
- INI, UST, LAB ファイルを変換できます。ただし不可逆の処理が多いです。



# Methods

---

## utaupy.ust

---

### Ust(collections.UserList)

UST ファイルを取り扱うためのクラス

### load(path)

USTファイルを読み取り、Ust オブジェクトにする。

```Python
ustobj = utaupy.ust.load(path)
print(type(ustobj))
# <class 'utaupy.ust.Ust'>
```

---

## utaupy.otoini

UTAUの原音設定ファイルを扱うモジュール。setParamでの利用を想定。

---

### class utaupy.otoini.OtoIni(collections.UserList)

oto.ini ファイルを扱うためのクラス。

---

### class utaupy.otoini.Oto(collections.UserDict)

oto.ini に含まれる各原音のパラメータを扱うクラス。

---

## utaupy.table

かなローマ字変換表などを扱うモジュール。

## utaupy.convert

Ust オブジェクト、OtoIni オブジェクト、Label オブジェクトなどを変換するモジュール。

## utaupy.reaper

REAPER (DAW) のリージョン・マーカー用CSVファイルを扱うモジュール。

## utaupy.utau

UTAUエディタで行う操作の代替と、UTAU音源の原音値取得などをするモジュール。「パラメータ自動調整」などができる。

## utaupy.utauplugin

UTAUプラグインをつくるためのモジュール。utaupy.utauplugin.UtauPlugin クラスは utaupy.ust.Ust を継承し、プラグイン用に最適化した子クラス。

使用例として半音上げプラグインを貼っておきます。

```Python
import utaupy

def notenum_plus1(utauplugin):
    """
    utauplugin: utaupy.utauplugin.UtauPlugin class object
    全てのノートを半音上げる
    """
    # 全ノートを取得
    notes = utauplugin.notes
    # 半音上げ
    for note in notes:
        note.notenum += 1

if __name__ == '__main__':
    # automatically
    # read the utau plugin script
    # load as utaupy.utauplugin.UtauPlugin class object
    # overwrite the utau plugin script
    utaupy.utauplugin.run(notenum_plus1)
```





## 連絡先

- Twitter: @oatsu_c

- GitHub: oatsu-gh

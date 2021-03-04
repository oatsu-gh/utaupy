@rem 次の1行は初回のドキュメント生成コマンド
@rem sphinx-apidoc -Ff -o docs/ utaupy/
cd docs
make html

@PyPIにアップロード
rd /s /q dist build utaupy.egg-info
python setup.py sdist bdist_wheel
twine check dist/*
REM twine upload --repository testpypi dist/* --verbose
twine upload --repository pypi dist/* --verbose

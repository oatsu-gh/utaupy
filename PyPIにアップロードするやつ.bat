@REM PyPIにアップロードするやつ

RD /s /q dist build utaupy.egg-info
python -m build
twine check dist/*
REM twine upload --repository testpypi dist/* --verbose
twine upload --repository pypi dist/* --verbose

PAUSE

@rem PyPIにアップロードするやつ

rd /s /q dist build utaupy.egg-info
python setup.py sdist bdist_wheel
twine check dist/*
REM twine upload --repository testpypi dist/* --verbose
twine upload --repository pypi dist/* --verbose

PAUSE

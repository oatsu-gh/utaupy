rd /s /q dist build utaupy.egg-info
python setup.py sdist bdist_wheel
twine check dist/*
twine upload --repository testpypi dist/* --verbose
REM twine upload --repository pypi dist/* --verbose

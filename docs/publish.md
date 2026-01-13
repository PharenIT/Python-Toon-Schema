# Publish Checklist

1. Update version in `pyproject.toml` and `src/toon_format.py`.
2. Run tests:

```
python -m pytest
```

3. Build artifacts:

```
python -m build
```

4. Check package metadata:

```
python -m twine check dist/*
```

5. Upload to TestPyPI (optional):

```
python -m twine upload --repository testpypi dist/*
```

6. Upload to PyPI:

```
python -m twine upload dist/*
```

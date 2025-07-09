# contextgrab

`contextgrab` is a command-line tool that copies file and notebook contents to your clipboard. When given a path, it reads files or Jupyter notebooks. If a directory is provided, it walks the directory recursively, respecting patterns in `.gitignore`.

```
Usage: contextgrab [--include-outputs] [--stdout] PATH
```

- If `PATH` is a file, the file name and contents are copied to the clipboard.
- If `PATH` is a Jupyter notebook (`.ipynb`), the pretty printed notebook contents are copied. Use `--include-outputs` to also include cell outputs.
- If `PATH` is a folder, each contained file is copied with its relative path.

The resulting text is copied to your clipboard for easy pasting into LLMs or other tools. Use `--stdout` to print the text instead of copying.

Install with:

```
pip install -e .
```

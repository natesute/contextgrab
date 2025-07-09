# contextgrab

`contextgrab` is a command-line tool that copies file and notebook contents to your clipboard. When given a path, it reads files or Jupyter notebooks. If a directory is provided, it walks the directory recursively, respecting patterns in `.gitignore`.

```
Usage: contextgrab [--include-outputs] [--stdout] PATH [PATH ...]
```

- Each `PATH` may be a file or directory.
- Files are copied with a header of the file name.
- Jupyter notebooks are pretty printed, optionally including outputs with `--include-outputs`.
- Directories are walked recursively with file paths listed relative to the directory.

The resulting text is copied to your clipboard for easy pasting into LLMs or other tools. Use `--stdout` to print the text instead of copying.

Install with:

```
pip install -e .
```

On Linux, `contextgrab` uses `pyperclip`, which requires `xclip` or `xsel` for
clipboard access. If these are missing, the tool prints a clear error and falls
back to stdout. Install one of them via your package manager for clipboard
support.

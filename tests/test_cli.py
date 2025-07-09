from pathlib import Path

import nbformat
import pyperclip

from contextgrab import cli


class Box:
    value = None


def test_read_file(tmp_path, monkeypatch):
    file = tmp_path / "hello.txt"
    file.write_text("hi")

    box = Box()
    monkeypatch.setattr(pyperclip, "copy", lambda text: setattr(box, "value", text))
    cli.main([str(file)])
    assert box.value == "FILE: hello.txt\nhi"


def test_walk_directory_respects_gitignore(tmp_path, monkeypatch):
    sub = tmp_path / "sub"
    sub.mkdir()
    included = sub / "a.txt"
    excluded = sub / "b.log"
    included.write_text("A")
    excluded.write_text("B")
    (sub.parent / ".gitignore").write_text("*.log\n")

    box = Box()
    monkeypatch.setattr(pyperclip, "copy", lambda text: setattr(box, "value", text))
    cli.main([str(sub)])
    assert "a.txt" in box.value
    assert "b.log" not in box.value


def create_notebook(path: Path) -> None:
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_markdown_cell("md"))
    nb.cells.append(
        nbformat.v4.new_code_cell(
            "1+1",
            outputs=[nbformat.v4.new_output("execute_result", data={"text/plain": "2"}, execution_count=1)],
        )
    )
    nbformat.write(nb, path)


def test_notebook_include_outputs(tmp_path, monkeypatch):
    nb_path = tmp_path / "nb.ipynb"
    create_notebook(nb_path)
    box = Box()
    monkeypatch.setattr(pyperclip, "copy", lambda text: setattr(box, "value", text))
    cli.main(["--include-outputs", str(nb_path)])
    assert box.value.endswith("md\n1+1\n2")


def test_stdout_flag(tmp_path, capsys):
    file = tmp_path / "hello.txt"
    file.write_text("hey")
    cli.main(["--stdout", str(file)])
    out = capsys.readouterr().out.strip()
    assert out == "FILE: hello.txt\nhey"


def test_multiple_paths(tmp_path, monkeypatch):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("A")
    b.write_text("B")

    box = Box()
    monkeypatch.setattr(pyperclip, "copy", lambda text: setattr(box, "value", text))
    cli.main([str(a), str(b)])
    assert "FILE: a.txt\nA" in box.value
    assert "FILE: b.txt\nB" in box.value

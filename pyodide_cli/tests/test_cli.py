import pathlib
import shutil
import subprocess
from multiprocessing import Process, Queue, set_start_method
from subprocess import check_output

import pytest

try:
    set_start_method("fork")
except RuntimeError:
    pass


@pytest.fixture(scope="module")
def plugins(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("plugin-test")
    source_plugin = pathlib.Path(__file__).parent / "plugin-test"

    tmp_plugin = tmp_dir / "plugin-test"
    shutil.copytree(source_plugin, tmp_plugin)

    subprocess.run(["pip", "install", str(tmp_plugin)])

    yield

    subprocess.run(["pip", "uninstall", "-y", "plugin-test"])


def test_cli_help():
    output = check_output(["pyodide", "--help"]).decode("utf-8")
    assert "A command line interface for Pyodide." in output


def test_cli_version(plugins):
    output = check_output(["pyodide", "--version"]).decode("utf-8")
    assert "pyodide CLI version:" in output
    assert "plugin-test version: 1.0.0" in output


def test_click_click_object_defintion():
    # By default the typer-click-object is not defined
    # Run in a separate process to make s
    q = Queue()

    def func(q: Queue, with_sphinx=False):
        import sys

        if with_sphinx:
            sys.modules["sphinx"] = None  # type: ignore
        import pyodide_cli.app

        q.put(dir(pyodide_cli.app))

    p = Process(target=func, args=(q,))
    p.start()
    p.join()
    app_dir = q.get()
    assert "typer_click_object" not in app_dir

    p = Process(target=func, args=(q,), kwargs={"with_sphinx": True})
    p.start()
    p.join()
    app_dir = q.get()
    assert "typer_click_object" in app_dir


def test_plugin_origin(plugins):
    output = check_output(["pyodide", "--help"]).decode("utf-8")
    msg = "Registered by plugin-test:"

    assert msg in output


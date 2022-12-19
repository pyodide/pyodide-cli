from multiprocessing import Process, Queue
from subprocess import check_output


def test_cli_help():
    output = check_output(["pyodide", "--help"]).decode("utf-8")
    msg = "A command line interface for Pyodide."
    assert msg in output


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

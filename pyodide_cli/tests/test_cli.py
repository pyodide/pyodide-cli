from subprocess import check_output


def test_cli_help():
    output = check_output(["pyodide", "--help"]).decode("utf-8")
    msg = "A command line interface for Pyodide."
    assert msg in output

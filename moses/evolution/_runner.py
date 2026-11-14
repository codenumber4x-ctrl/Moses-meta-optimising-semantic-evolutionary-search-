"""Runs a candidate program in a child process.

Reads {"source", "entry_point", "cases"} as JSON from stdin and writes
{"results": [{"output": ...} | {"error": ...}, ...]} or {"error": ...} to stdout.
Uses only the standard library so it can run with `python -I`.
"""

import contextlib
import io
import json
import sys


def _error(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"[:300]


def main() -> None:
    request = json.load(sys.stdin)
    namespace = {"__name__": "candidate"}
    captured = io.StringIO()  # keeps candidate prints out of the JSON reply

    with contextlib.redirect_stdout(captured):
        try:
            exec(compile(request["source"], "candidate.py", "exec"), namespace)
            func = namespace[request["entry_point"]]
        except KeyError:
            reply = {"error": f"program does not define {request['entry_point']}()"}
        except BaseException as exc:
            reply = {"error": _error(exc)}
        else:
            results = []
            for args in request["cases"]:
                try:
                    output = func(*args)
                    json.dumps(output)  # outputs must survive the trip back
                    results.append({"output": output})
                except BaseException as exc:
                    results.append({"error": _error(exc)})
            reply = {"results": results}

    sys.stdout.write(json.dumps(reply))


if __name__ == "__main__":
    main()

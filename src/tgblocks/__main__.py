# Allows `python -m tgblocks run examples/hello.tg`.

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())

from .parser import build_parser
from ..ui.home import show_home


def main() -> None:
    args = build_parser().parse_args()
    if not hasattr(args, "func"):
        show_home(args)
        return
    args.func(args)

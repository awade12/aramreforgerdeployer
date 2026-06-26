from .parser import build_parser


def main() -> None:
    (args := build_parser().parse_args()).func(args)

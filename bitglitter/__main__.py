import argparse
from .cli.args import parser

def cli():
    parser.parse_known_args()


if __name__ == '__main__':
    cli()

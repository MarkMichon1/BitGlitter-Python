from .cli.cli_args import parser
from .cli.utilities import valid_args


def main():
    # test input = python3 -m bitglitter --write writeparams
    params = valid_args(parser.parse_args())
    if 'write' in params: 
        print('Testing')    

if __name__ == '__main__':
    main()
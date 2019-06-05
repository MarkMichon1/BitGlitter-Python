from .cli.args import parser
from .write.write import write
from .cli.analyzer import CliArgumentParser
from .cli.utilities import validate_args

def main():
    # python3 -m bitglitter --write image_path output_mode
	parsed_args = CliArgumentParser(parser)
	
	if 'write' in parsed_args:
		parsed_args.write()
	

if __name__ == '__main__':
    main()
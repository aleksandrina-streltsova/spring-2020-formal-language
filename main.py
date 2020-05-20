from antlr4 import *
from argparse import ArgumentParser, FileType
from src.language.antlr.query import print_script_tree, script_is_correct, run_script


def main():
    console_parser = ArgumentParser()
    console_parser.add_argument('-r', '--run', action='store_true', help='run script')
    console_parser.add_argument('-i', nargs='?', type=FileType('r'), dest='infile', help='parse script from file')
    console_parser.add_argument('-o', nargs='?', type=FileType('w'), dest='outfile', help='write tree to file')
    args = console_parser.parse_args()
    if args.infile:
        stream = InputStream(args.infile.read())
    else:
        stream = StdinStream()
    if args.run:
        result = run_script(stream)
        if args.outfile:
            args.outfile.write(result)
        else:
            print(result)
    else:
        if args.outfile:
            print_script_tree(stream, args.outfile)
        else:
            if script_is_correct(stream):
                print("script is correct")
            else:
                print("script is incorrect")


if __name__ == '__main__':
    main()

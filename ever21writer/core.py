import os
import sys
from ever21writer.converter import EverConverter
import argparse


def main():
    parser = argparse.ArgumentParser(prog=None, description="Convert Evernote.enex files to Markdown", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('enex-file', help="the path to the Evernote.enex file")
    parser.add_argument('-o', '--output', help="the path to the output file or directory, leave black to output to the terminal (stdout)")
    args = parser.parse_args()
    enex_file = vars(args)['enex-file']
    output = args.output
    filepath = os.path.expanduser(enex_file)
    if not os.path.exists(filepath):
        print 'File does not exist: %s' % filepath
        sys.exit(1)
    converter = EverConverter(filepath, simple_filename=output)
    converter.convert()
    sys.exit()


if __name__ == '__main__':
    main()

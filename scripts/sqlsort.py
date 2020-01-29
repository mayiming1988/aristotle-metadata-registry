"""
Script to sort lines in an sql file inside a create statement
Used in db_compare.sh
"""
from typing import List, TextIO
import sys
import re

# Flag for appending comma
append_comma = True

# Markers used for debugging
dashes = '-' * 20
start_marker = dashes + ' Sort Start ' + dashes
end_marker = dashes + ' Sort End ' + dashes

# Regex used to find sorting boundaries
start_regex = re.compile(r'^CREATE.* \(\r?$')
end_regex = re.compile(r'^\);?\r?$')


def append_line_comma(line: str) -> str:
    """Add comma to line before it's newline if required"""
    # Only append if not already there
    if not line.endswith(','):
        return line + ','

    return line


def sort_brackets(file: TextIO, debug=False) -> List[str]:
    """Return lines of file, with lines between brackets sorted"""
    bracketed: List[str] = []
    lines: List[str] = []
    in_brackets = False

    # Loop thorough file by line
    for full_line in file:
        line = full_line.rstrip('\r\n')

        if start_regex.match(line):
            # If found start string
            in_brackets = True
            lines.append(line)
        elif end_regex.match(line):
            # If found end string
            in_brackets = False
            if debug:
                lines.append(start_marker)
            lines.extend(sorted(bracketed))
            if debug:
                lines.append(end_marker)
            bracketed.clear()
            lines.append(line)
        else:
            # Add lines to respective lists
            if in_brackets:
                # Add comma if flag is on
                if append_comma:
                    bracketed.append(append_line_comma(line))
                else:
                    bracketed.append(line)
            else:
                lines.append(line)

    return lines


def main():
    lines = sort_brackets(sys.stdin)
    sys.stdout.write('\n'.join(lines))


if __name__ == '__main__':
    main()

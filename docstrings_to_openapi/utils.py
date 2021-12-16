import sys


def prepare_docstring(s, tabsize=4):
    """
    Convert a docstring into lines of parseable reST.  Remove common leading
    indentation, where the indentation of a given number of lines (usually just
    one) is ignored.

    Return the docstring as a list of lines usable for inserting into a
    docutils ViewList (used as argument of nested_parse().)  An empty line is
    added to act as a separator between this docstring and following content.

    NOTE: This function is from Sphinx.
    """
    # NOTE: Do we really want to ignore indentation of the first line?
    ignore = 1
    lines = s.expandtabs(tabsize).splitlines()
    # Find minimum indentation of any non-blank lines after ignored lines.
    margin = sys.maxsize
    for line in lines[ignore:]:
        content = len(line.lstrip())
        if content:
            indent = len(line) - content
            margin = min(margin, indent)
    # Remove indentation from ignored lines.
    for i in range(ignore):
        if i < len(lines):
            lines[i] = lines[i].lstrip()
    if margin < sys.maxsize:
        for i in range(ignore, len(lines)):
            lines[i] = lines[i][margin:]
    # Remove any leading blank lines.
    while lines and not lines[0]:
        lines.pop(0)
    # make sure there is an empty line at the end
    if lines and lines[-1]:
        lines.append('')
    return lines


def remove_start_and_end_empty_strings(lines):
    if len(lines) == 0:
        return lines
    while len(lines[0]) == 0:
        lines.pop(0)
    while len(lines[-1]) == 0:
        lines.pop(-1)
    return lines

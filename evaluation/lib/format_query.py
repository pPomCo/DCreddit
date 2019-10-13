

def escape_lucene_special_chars(string):
    for c in ['\\', '+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']',
              '^', '"', '~', '*', '?', ':', '/', ',', '.', "'"]:
        string = string.replace(c, ' ')
    return string


if __name__ == "__main__":
    import sys

    # Delete special characters from stdin
    for line in sys.stdin:
        line = escape_lucene_special_chars(line).lower()
        print(line, end="")

    # Empty line at the end
    print()

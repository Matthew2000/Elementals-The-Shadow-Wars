import string

#modified from https://gist.github.com/seanh/93666
def sanitize_filename(file_name):
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in file_name if c in valid_chars)
    return filename

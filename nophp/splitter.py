import re


def split_php(text):
    pattern = r'(<\?php.*?\?>)|(.*)'

    # Find all matches
    matches = re.findall(pattern, text, re.DOTALL)

    # Extract the portions inside and outside the PHP code block
    text = ''.join(match[0] for match in matches).strip()
    html = ''.join(match[1] for match in matches).strip()
    return text, html

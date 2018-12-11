import re


def pretify_camel_case(camelcase):
    return re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', camelcase)


def capmatch(match):
    return match.group(0).title()


def capitalize_words(text):
    return re.sub(r'[ ](.)', capmatch, text.title())

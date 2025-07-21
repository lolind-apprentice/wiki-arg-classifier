import re

def normalise_label(label: str) -> str:
    """
    Lower-case, strip brackets, drop anything after '(' or '+'
    e.g.  'value + editorial process (article)' -> 'value'
    """
    label = str(label).lower().strip()
    label = re.split(r'[+(]', label)[0].strip()
    label = label.replace('[', '').replace(']', '')
    label = label.replace("'", "")  
    if label in {"editorial process", "editorial process article", "others argument"}:
        return "editorial/meta"
    return label



"""
Misc tools (for handling with metadata, etc.)
"""


# ---------------------------
# Imports
# ---------------------------

import yaml
#import panflute


# ---------------------------
# Functions
# ---------------------------

def write_metadata(md_fn, style_options):
    yaml_fn = md_fn.parent / (md_fn.stem + '.yaml')
    with yaml_fn.open('w') as fh:
        yaml.dump(style_options, fh, default_flow_style=False)
    return yaml_fn


#def get_metadata(fn):
#    # NOT CURRENTLY USED
#    with open(fn, 'r') as fh:
#        doc = panflute.convert_text(fh.read(), standalone=True)
#    
#    style = doc.get_metadata('style')
#    return {'style': style}

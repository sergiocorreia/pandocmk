"""
Misc tools (for handling with metadata, etc.)
"""


# ---------------------------
# Imports
# ---------------------------

import yaml
from pathlib import Path
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


def get_filename(fn, subfolder=None):
	path = Path(__file__).resolve().parent
	fixed_fn = (path / subfolder / fn) if subfolder else (path / fn)

	# Fail gracefully
	fn = str(fixed_fn) if fixed_fn.is_file() else fn

	return fn


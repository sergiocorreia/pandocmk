"""
Build command line call and run Pandoc
"""


# ---------------------------
# Imports
# ---------------------------

from pathlib import Path

import panflute

from .view import run_viewer
from .utils import get_metadata
from .metadata import options2arguments


# ---------------------------
# Functions
# ---------------------------

def run_pandoc(pandoc_options, md_fn, ext, verbose):
	assert ext in ('pdf', 'tex')
	assert isinstance(pandoc_options, dict)

	if pandoc_options['output'] is None:
		out_fn = md_fn.parent / (md_fn.stem + f'.{ext}')
	else:
		out_fn = Path(pandoc_options['output'])
		out_fn = out_fn.parent / (out_fn.stem + f'.{ext}') # Ensure we output .tex when we need to

	pandoc_options['output'] = out_fn
	pandoc_args = options2arguments(pandoc_options)
	pandoc_args.append(str(md_fn))
	
	if verbose:
	    print('- Pandoc call:')
	    print(f'  pandoc {" ".join(pandoc_args)}')
	
	panflute.run_pandoc(args=pandoc_args)
	return out_fn # In case we want to view the file later



def build_output(md_fn, view, timeit, tex, verbose, pandoc_options):

    # Build .tex output through Pandoc
    if tex:
    	out_fn = run_pandoc(pandoc_options, md_fn, 'tex', verbose)

    # Build .pdf output through Pandoc
    out_fn = run_pandoc(pandoc_options, md_fn, 'pdf', verbose)

    # View PDF in SumatraPDF
    if view:
        run_viewer(out_fn, verbose)

    if verbose:
        print(f'- File {out_fn} built!')

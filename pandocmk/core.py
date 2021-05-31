"""
Build command line call and run Pandoc
"""


# ---------------------------
# Imports
# ---------------------------

import time
from pathlib import Path

import panflute

from .view import run_viewer
#from .utils import get_metadata
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
    fix_citation_options(pandoc_options, ext)
    pandoc_args = options2arguments(pandoc_options)
    pandoc_args.append(str(md_fn))
    
    if verbose:
        print('[pandocmk] Pandoc call:')
        print(f'    pandoc {" ".join(pandoc_args)}')
    
    wait = 0.05
    while True:
        err = inner_run_pandoc(pandoc_args)

        if err:
            # Set wait time in seconds, before trying again
            if wait < 1:
                wait * 2
            else:
                wait += 1
            wait = min(5.0, wait)
            if verbose:
                print(f'[pandocmk] error encountered; sleeping for {wait:4.1f} seconds')
            time.sleep(wait)
        else:
            if verbose:
                print(f'[pandocmk] Pandoc call completed')
            break

    return out_fn # In case we want to view the file later


def inner_run_pandoc(pandoc_args):
    # If there is a latex error ("Undefined control sequence", etc.)
    # we will abort without a huge traceback
    # https://stackoverflow.com/questions/17784849/print-an-error-message-without-printing-a-traceback-and-close-the-program-when-a
    try:
        panflute.run_pandoc(args=pandoc_args)
        return False  # error = False
    except IOError as err:
        if error_is_fatal(err):
            raise SystemExit()
        return True # error = True


def error_is_fatal(e):
    '''If there is a deeper error (such as a not-found filter) we will abort altogether'''

    # If there are no arguments (i.e. text message then we can't do anything)
    if not e.args:
        return False

    if 'Could not find executable' in e.args[0]:
        return True

    if 'invalid api version' in e.args[0]:
        return True
    
    if 'Unknown option' in e.args[0]:
        return True
    
    return False


def fix_citation_options(options, ext):
    # With -tex- output we need to have "citeproc" off and "natbib" on
    # With -pdf- output we need to have "natbib" off and "citeproc" on
    # In both cases the option needs to be AT THE END so it gets run after all filters
    # (because filters can include further text)
    assert ext in ('pdf', 'tex')
    
    citation_opt = None
    for opt in ('citeproc', 'natbib'):
        if opt in options:
            citation_opt = opt
            break

    if citation_opt is not None:
        del options[citation_opt]
        new_option = 'citeproc' if ext=='pdf' else 'natbib'
        options[new_option] = True


def build_output(md_fn, view, timeit, tex, verbose, pandoc_options):

    if verbose:
        tic = time.perf_counter()

    # Build .tex output through Pandoc
    if tex:
        out_fn = run_pandoc(pandoc_options, md_fn, 'tex', verbose)

    # Build .pdf output through Pandoc
    out_fn = run_pandoc(pandoc_options, md_fn, 'pdf', verbose)

    # View PDF in SumatraPDF
    if view:
        run_viewer(out_fn, verbose)

    if verbose:
        toc = time.perf_counter()
        print(f"[pandocmk] file '{out_fn}' built in {toc - tic:0.1f} seconds")

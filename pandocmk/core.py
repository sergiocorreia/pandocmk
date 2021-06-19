"""
Build command line call and run Pandoc
"""


# ---------------------------
# Imports
# ---------------------------

import time
import shutil
from pathlib import Path
from subprocess import Popen, PIPE

import panflute

from .view import run_viewer
#from .utils import get_metadata
from .metadata import options2arguments


# ---------------------------
# Functions
# ---------------------------

def run_pandoc(pandoc_options, md_fn, ext, retry, verbose):
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

        if err and not retry:
            if verbose:
                print(f'[pandocmk] error encountered; stopping')
            return None
        elif err:
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


def build_output(md_fn, view, timeit, tex, latexmk, retry, verbose, pandoc_options):

    if verbose:
        tic = time.perf_counter()

    # Build .tex output through Pandoc
    if tex:
        out_fn = run_pandoc(pandoc_options, md_fn, 'tex', retry, verbose)
        # Exit if pandoc call failed (so we don't call latexmk or pandoc again)
        if out_fn is None:
            exit()


    # Build .pdf output through Pandoc
    if latexmk:
        assert tex
        # latexmk academic-markdown.tex -pdf -halt-on-error -quiet
        tex_fn = md_fn.with_suffix('.tex')
        out_fn = run_latexmk(tex_fn, verbose=verbose)
    else:
        out_fn = run_pandoc(pandoc_options, md_fn, 'pdf', retry, verbose)

    # View PDF in SumatraPDF
    if view:
        run_viewer(out_fn, verbose)

    if verbose:
        toc = time.perf_counter()
        print(f"[pandocmk] file '{out_fn}' built in {toc - tic:0.1f} seconds")


def run_latexmk(fn, verbose):
    options = {'pdf': True, 'halt-on-error': True, 'quiet': True, 'output-directory': './tmp'}
    cmd = ['latexmk', str(fn)] + options2arguments(options)

    if verbose:
        print('[pandocmk] latexmk call:')
        print(f'    {" ".join(cmd)}')

    # We will want to keep our base folder neat so we'll move as much as possible to ./tmp
    tmp_path = fn.parent / 'tmp'

    # Delete .tex file from temp folder if it exists (else latexmk fails)
    (tmp_path / fn.name).unlink(missing_ok=True)

    # Run latexmk
    panflute.shell(cmd)

    # Copy .tex file
    shutil.move(fn, tmp_path / fn.name)

    # Copy .yaml file
    yaml_fn = fn.with_suffix('.yaml')
    shutil.move(yaml_fn, tmp_path / yaml_fn.name)

    # Move PDF from tmp folder (use shutil.copy2 to overwrite and keep metadata)
    pdf_fn = fn.with_suffix('.pdf')
    src = tmp_path / pdf_fn.name
    dst = pdf_fn.name
    shutil.move(src, dst)
    return pdf_fn

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
        tic = time.perf_counter()
    
    panflute.run_pandoc(args=pandoc_args)

    if verbose:
        toc = time.perf_counter()
        print(f'[pandocmk] Pandoc call completed in  {toc - tic:0.1f} seconds')

    return out_fn # In case we want to view the file later


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


def build_output(md_fn, view, timeit, tex, latexmk,verbose, pandoc_options):

    if verbose:
        tic = time.perf_counter()

    # Build .tex output through Pandoc
    if tex:
        out_fn = run_pandoc(pandoc_options, md_fn, 'tex', verbose)
        # Exit if pandoc call failed (so we don't call latexmk or pandoc again)
        if out_fn is None:
            exit()

    # Build .pdf output through Pandoc
    if latexmk:
        assert tex
        # latexmk academic-markdown.tex -pdf -halt-on-error -quiet
        tex_fn = md_fn.with_suffix('.tex')
        pdf_engine = pandoc_options[ 'pdf-engine']
        assert pdf_engine in ('xelatex', 'pdflatex')  # We can add more engines, but need to customize the -latexmk- call accordingly
        out_fn = run_latexmk(tex_fn, pdf_engine, verbose=verbose)
    else:
        out_fn = run_pandoc(pandoc_options, md_fn, 'pdf', verbose)

    # View PDF in SumatraPDF
    if view:
        run_viewer(out_fn, verbose)

    if verbose:
        toc = time.perf_counter()
        print(f"[pandocmk] file '{out_fn}' built in {toc - tic:0.1f} seconds")


def run_latexmk(fn, pdf_engine, verbose):
    options = {'pdf': True, 'halt-on-error': True, 'quiet': True, 'output-directory': './tmp'}

    if pdf_engine == 'xelatex':
        options['pdfxe'] = True

    cmd = ['latexmk', str(fn)] + options2arguments(options)

    if verbose:
        print('[pandocmk] latexmk call:')
        print(f'    {" ".join(cmd)}')
        tic = time.perf_counter()

    # We will want to keep our base folder neat so we'll move as much as possible to ./tmp
    tmp_path = fn.parent / 'tmp'

    # Delete .tex file from temp folder if it exists (else latexmk fails)
    (tmp_path / fn.name).unlink(missing_ok=True)

    # Run latexmk
    try:
        panflute.shell(cmd)
    except IOError:
        pass

    if verbose:
        toc = time.perf_counter()
        print(f'[pandocmk] latexmk call completed in  {toc - tic:0.1f} seconds')

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

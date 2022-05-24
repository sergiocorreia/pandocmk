"""
Code for interfacing with the user through the CLI
"""


# ---------------------------
# Imports
# ---------------------------

from pathlib import Path

import click
import backoff

from .version import __version__
from .metadata import get_pandoc_options
from .core import build_output
from .watch import monitor_file


# ---------------------------
# Functions
# ---------------------------

help_str = r"""
Pandocmk: A minimalistic make for pandoc
========================================

Note: [FILE] must come first; and options must be --key=val or --key

pandocmk [FILES] [OPTIONS] [PANDOC OPTIONS]
"""

@click.command(help=help_str, context_settings=dict(ignore_unknown_options=True) )
@click.version_option(version=__version__)
@click.argument('file', type=click.Path(exists=True))
@click.option('--view', is_flag=True, default=False, help="open output file in a viewer such as SumatraPDF for .pdf")
@click.option('--watch', '-w', is_flag=True, default=False, help="monitor the input files for changes, and rebuild as needed")
@click.option('--timeit', '--time', is_flag=True, default=False, help="show build time")
@click.option('--draft', is_flag=True, default=False, help="NOT IMPLEMENTED. When building a Latex PDF, choose faster options (pdflatex, etc)")
@click.option('--tex', is_flag=True, default=False, help="save .tex output besides .pdf")
@click.option('--latexmk', is_flag=True, default=False, help="build pdf with latexmk; implies --tex")
@click.option('--verbose', '-v', is_flag=True, default=False, help="show debugging information")
@click.option('--strict', '-s', is_flag=True, default=True, help="stop with error if style not found")
@click.option('--retry', '-r', is_flag=True, default=False, help="try again in case of error (useful with --watch)")
@click.argument('pandoc_args', nargs=-1, type=click.UNPROCESSED)

def main(file, view, watch, timeit, draft, tex, latexmk, verbose, strict, retry, pandoc_args):

    if latexmk:
        tex = True

    if verbose:
        print(f'[pandocmk] {verbose=}')

    md_fn = Path(file)
    assert md_fn.suffix == '.md'
    assert md_fn.is_file()

    # Get Pandoc options from CLI and YAML
    # This also creates a temporary {filename}.yaml file with metadata based on styles
    pandoc_options = get_pandoc_options(pandoc_args, md_fn, verbose=verbose, strict=strict)

    # Optionally add watch
    f = monitor_file if watch else build_output 

    # Optionally add back-off for errors
    # https://github.com/litl/backoff/blob/master/backoff/_wait_gen.py
    if retry:
        f = backoff.on_exception(wait_gen=backoff.expo, exception=Exception,
                                 base=1, max_value=20,
                                 max_tries=1000, max_time=600, giveup=error_is_fatal, on_backoff=print_backoff)(f)

    f(md_fn, view=view, timeit=timeit, tex=tex, latexmk=latexmk, verbose=verbose, pandoc_options=pandoc_options)


def print_backoff(args):
    pass
    #print(args)
    print('BACKOFF CAUGHT AN ERROR >>>')


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


#def inner_run_pandoc(pandoc_args):
#    # If there is a latex error ("Undefined control sequence", etc.)
#    # we will abort without a huge traceback
#    # https://stackoverflow.com/questions/17784849/print-an-error-message-without-printing-a-traceback-and-close-the-program-when-a
#    try:
#        panflute.run_pandoc(args=pandoc_args)
#        return False  # error = False
#    except IOError as err:
#        if error_is_fatal(err):
#            raise SystemExit()
#        return True # error = True


if __name__ == '__main__':
    main()
"""
Code for interfacing with the user through the CLI
"""


# ---------------------------
# Imports
# ---------------------------

from pathlib import Path
import click

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
@click.option('--verbose', '-v', is_flag=True, default=False, help="show debugging information")
@click.option('--strict', '-s', is_flag=True, default=True, help="stop with error if style not found")
@click.argument('pandoc_args', nargs=-1, type=click.UNPROCESSED)


def main(file, view, watch, timeit, draft, tex, verbose, strict, pandoc_args):

    if verbose:
        print(f'[pandocmk] {verbose=}')

    md_fn = Path(file)
    assert md_fn.suffix == '.md'
    assert md_fn.is_file()

    # Get Pandoc options from CLI and YAML
    # This also creates a temporary {filename}.yaml file with metadata based on styles
    pandoc_options = get_pandoc_options(pandoc_args, md_fn, verbose=verbose, strict=strict)

    # Always run early on
    build_output(md_fn, view=view, timeit=timeit, tex=tex, verbose=verbose, pandoc_options=pandoc_options)

    # Run on-demand if required
    if watch:
        monitor_file(md_fn, timeit=timeit, tex=tex, verbose=verbose, pandoc_options=pandoc_options)        
        monitor_file(path, md_fn, timeit, verbose, pandoc_args)


if __name__ == '__main__':
    main()
"""
Code for interfacing with the user through the CLI
"""


# ---------------------------
# Imports
# ---------------------------

from pathlib import Path
import click
import panflute

from .utils import get_metadata, dict2args


# ---------------------------
# Functions
# ---------------------------

help_str = """
Pandocmk: A minimalistic make for pandoc
========================================

pandocmk [OPTIONS] [FILES]
  --view			open output file in a viewer such as SumatraPDF for .pdf
  --watch			monitor the input files for changes, and rebuild as needed
  --tex				save .tex output besides .pdf
  --timeit			show build time
  --verbose			show debugging information

  --draft			NOT IMPLEMENTED.
                    When building a Latex PDF, choose faster options (pdflatex, etc)

Note: other options are passed to Pandoc
"""

@click.command(help=help_str)
@click.argument('file', type=click.Path(exists=True))
@click.option('--view', is_flag=True, default=False, help="TBD")
@click.option('--watch', '-w', is_flag=True, default=False, help="TBD")
@click.option('--timeit', '--time', is_flag=True, default=False, help="TBD")
@click.option('--draft', is_flag=True, default=False, help="Use faster pdflatex and other speedups; not implemented yet")
@click.option('--tex', is_flag=True, default=False, help="Save .tex output")
@click.option('--verbose', '-v', is_flag=True, default=False, help="TBD")
@click.argument('pandoc_args', nargs=-1, type=click.UNPROCESSED)

def main(file, view, watch, timeit, draft, tex, verbose, pandoc_args):

    md_fn = Path(file)
    assert md_fn.suffix == '.md'
    assert md_fn.is_file()

    # Always run early on
    inner(md_fn, view=view, timeit=timeit, tex=tex, verbose=verbose, pandoc_args=pandoc_args)

    # Run on-demand if required
    if watch:
        path = '.'
        print(f'Monitoring file "{md_fn}" in directory {path}')
        # view=False as we don't need Sublime to steal windows focus every time we save
        event_handler = MarkdownUpdateHandler(md_fn, False, timeit, verbose, pandoc_args)
        monitor_file(path, event_handler)


def inner(md_fn, view, timeit, tex, verbose, pandoc_args):
    #print('PASSTHROUGH OPTIONS:', pandoc_args)

    # Get style
    metadata_fn = None

    ## metadata = get_metadata(md_fn)
    ## style = metadata['style']
    ## if verbose:
    ##     print(f'- Style:        {style}')
    ## if style not in styles:
    ##     print(f'WARNING: Unknown style {style}; valid styles are {list(styles.keys())}; using "article" as default')
    ## style_options = styles.get(style, 'notes')
    ## #options = {**styles[style]} # Copy dict
    ## if verbose:
    ##     print('- Settings:')
    ##     for k, v in style_options.items():
    ##         print(f'      {k}: {v}')

    ## # Write style
    ## metadata_fn = write_metadata(md_fn, style_options)

    # Call Tex
    if tex:
        pdf_fn = md_fn.parent / (md_fn.stem + '.tex')
        pandoc_options = {'from': 'markdown', 'to': 'latex', 'standalone': True,
            'pdf-engine': 'xelatex',
            'output': pdf_fn}
        if metadata_fn:
        	pandoc_options['metadata-file'] = metadata_fn
        	            
        pandoc_args = dict2args(pandoc_options, md_fn)
        panflute.run_pandoc(args=pandoc_args)
        if verbose:
            print('- Pandoc call:')
            print(f'      pandoc {" ".join(pandoc_args)} {md_fn}')
        assert False


    # Call Pandoc
    pdf_fn = md_fn.parent / (md_fn.stem + '.pdf')
    pandoc_options = {'from': 'markdown', 'to': 'latex', 'standalone': True,
        'pdf-engine': 'xelatex',
        'output': pdf_fn}
    if metadata_fn:
    	pandoc_options['metadata-file'] = metadata_fn
    
    pandoc_args = dict2args(pandoc_options, md_fn)
    if verbose:
        print('- Pandoc call:')
        print(f'      pandoc {" ".join(pandoc_args)}')
    panflute.run_pandoc(args=pandoc_args)

    # Call Sumatra
    if view:
        run_viewer(pdf_fn)

    print('- Update complete')


if __name__ == '__main__':
    main()
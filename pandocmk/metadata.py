"""
Code for interfacing with the user through the CLI
"""


# ---------------------------
# Imports
# ---------------------------

import yaml
from pathlib import Path

# Used to access static files (i.e. .yaml files)
# https://stackoverflow.com/a/20885799/3977107
from importlib.resources import read_text

from .utils import write_metadata, get_filename

# ---------------------------
# Functions
# ---------------------------

def get_pandoc_options(args, md_fn, verbose=False, strict=False):

    # Priority of Pandoc CLI options (right overrides left):
    # hardcoded here -> Default YAML file -> Markdown YAML header -> pandocmk CLI options

    # Set default Pandoc options
    options = {'from': 'markdown',
               'to': 'latex',
               'standalone': True,
               'pdf-engine': 'xelatex',
               'output': None}

    # Load default YAML styles
    default_styles = read_text("pandocmk", "default-styles.yaml")
    default_styles = yaml.safe_load(default_styles)

    # Get markdown YAML header
    meta = get_yaml_metadata(md_fn)
    style = meta.get('style', 'default') # If style does not exist, use 'default'

    # Override defaults with YAML styles
    if style in default_styles:
        if verbose:
            print(f'[pandocmk] {style=}')
        style_settings = default_styles[style]

        # Replace templates with those in the pandocmk template folder
        # Note that we only do so for the default options, so users can change this
        template = style_settings.get('pandoc', {}).get('template')
        if template:
            template = get_filename(template, subfolder='templates')
            style_settings['pandoc']['template'] = template

        # Same for filters
        filters = style_settings.get('pandoc', {}).get('filter')
        if filters:
            filters = [get_filename(filter, subfolder='filters') for filter in filters] 
            style_settings['pandoc']['filter'] = filters

        # Override Pandoc CLI options
        options.update(style_settings.get('pandoc', {}))

        # Flatten YAML file (when we include we often end up with lists-of-lists which look ugly)
        style_settings = flatten_dict(style_settings)

        # Add metadata YAML file
        temp_yaml_fn = write_metadata(md_fn, style_settings)
        options['metadata-file'] = str(temp_yaml_fn)

    else:
        if strict:
            raise SystemExit(f'[pandocmk] Error! {style=} not found')
        else:
            print(f'[pandocmk] Warning! {style=} not found')
    
    # Override current options with markdown YAML header
    new_options = meta.get('pandoc', {})
    #if 'header-includes' in options and 'header-includes' in new_options:
    #    new_options['header-includes'] = options['header-includes'] + new_options['header-includes']
    options.update(new_options)

    # Override current options with CLI options
    new_options = arguments2options(args)
    #if 'header-includes' in options and 'header-includes' in new_options:
    #    new_options['header-includes'] = options['header-includes'] + new_options['header-includes']
    options.update(new_options)


    # Bibtex hates relative bibliography paths, so we have to resolve to an absolute path
    bibliography = options.get('bibliography')
    if bibliography is not None:
        fn = Path(bibliography).resolve()
        assert fn.is_file()
        fn = str(fn.with_suffix('')) # Bibtex cannot receive the .bib extension
        fn = fn.replace('\\', '/') # Bibtex expects a/b, not a\b
        options['bibliography'] = fn 

    return options


def flatten_dict(d):
    assert isinstance(d, dict)
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = flatten_dict(v)
        elif isinstance(v, list):
            v = [item if isinstance(item, list) else [item] for item in v]
            d[k] = [subitem for item in v for subitem in item]
    return d


def arguments2options(args):
    """
    Convert CLI arguments into a dict
    
    - Warns of Pandoc options that do not start with '--' (we only support --opt=val and --flag)
    - TODO: Add support for -O val
    """

    assert not isinstance(args, str)  # TODO: generalize it to allow iterables but not strings
    options = {}
    for arg in args:
        if not arg.startswith('--'):
            print(f'WARNING: option {arg} does not start with "--"; ignored')
            continue
        arg = arg[2:].split('=')  # Given "--key=val" or "--flag" it will return "key" or "flag"
        options[arg[0]] = arg[1] if len(arg) == 2 else True

    return options


def options2arguments(options):
    args = []
    for k, v in options.items():
        # If there are multiple filters, we need to expand them to multiple arguments:
        # filter=[a,b] --> "-F a -F b"
        if k == 'filter' and isinstance(v, list):  # not very robust (e.g. fails with tuple)
            for vv in v:
                args.append(f'--{k}={vv}')
        else:
            args.append(f'--{k}' if isinstance(v, bool) else f'--{k}={v}')
    return args


def get_yaml_metadata(fn):

    # YAML chokes if we try to parse the whole file
    # Thus we'll select the YAML header and parse only that
    # See: https://stackoverflow.com/a/32496719/3977107

    # First line outside of YAML directives or comments must be "---"
    # Last line of YAML header must be "---" or "..."

    with fn.open(encoding='utf8') as fh:
        data = []
        is_first_line = True
        
        for line in fh:
            
            # Detect first line
            if is_first_line:

                # YAML directives such as "%YAML 1.2"
                if line.startswith(u'%'):
                    continue

                # Comments
                if line.lstrip().startswith('#'):
                    continue
                
                # Actual first line
                if line == '---\n' or line.startswith('--- '):
                    is_first_line = False
                    continue
                
                # No more special cases
                return {}

            # Detect last line
            if not is_first_line:

                if line == '---\n' or line.startswith('--- '):
                    break
                
                if line == '...\n' or line.startswith('... '):
                    break

            data.append(line)

    data = yaml.safe_load(''.join(data))
    return data

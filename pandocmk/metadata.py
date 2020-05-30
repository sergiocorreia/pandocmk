"""
Code for interfacing with the user through the CLI
"""


# ---------------------------
# Imports
# ---------------------------

import yaml

# Used to access static files (i.e. .yaml files)
# https://stackoverflow.com/a/20885799/3977107
from importlib.resources import read_text

from .utils import write_metadata

# ---------------------------
# Functions
# ---------------------------

def get_pandoc_options(args, md_fn, verbose=False):

    # Option priority (right overrides left)
    # hardcoded -> default yaml -> markdown header -> CLI

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
    style = meta.get('style') # If style does not exist, use "DEFAULT"!!! BUGBUG

    # Override defaults with YAML styles
    if style in default_styles:
        if verbose:
            print(f'[pandocmk] {style=}')
        style_settings = default_styles[style]
        
        # Override Pandoc CLI options
        options.update(style_settings.get('pandoc', {}))

        # Flatten YAML file (when we include we often end up with lists-of-lists which look ugly)
        style_settings = flatten_dict(style_settings)

        # Add metadata YAML file
        temp_yaml_fn = write_metadata(md_fn, style_settings)
        options['metadata-file'] = str(temp_yaml_fn)
    
    # Override current Pandoc CLI options with markdown YAML header
    options.update(meta.get('pandoc', {}))

    # Override current Pandoc CLI options with CLI options
    options.update(arguments2options(args))

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
    return [f'--{k}' if isinstance(v, bool) else f'--{k}={v}' for k, v in options.items()]


def get_yaml_metadata(fn):

    # YAML chokes if we try to parse the whole file
    # Thus we'll select the YAML header and parse only that
    # See: https://stackoverflow.com/a/32496719/3977107

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
                is_first_line = False

            # Detect last line
            if not is_first_line:

                if line == '---\n' or line.startswith('--- '):
                    break
                
                if line == '...\n' or line.startswith('... '):
                    break

            data.append(line)

    data = yaml.safe_load(''.join(data))
    return data

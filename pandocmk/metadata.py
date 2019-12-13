"""
Code for interfacing with the user through the CLI
"""


# ---------------------------
# Imports
# ---------------------------

import yaml


# ---------------------------
# Functions
# ---------------------------

def get_pandoc_options(args, md_fn, verbose=False):

    # Default options
    options = {'from': 'markdown',
               'to': 'latex',
               'standalone': True,
               'pdf-engine': 'xelatex',
               'output': None}

    # Get YAML header and use it to override default options
    meta = get_yaml_metadata(md_fn)
    options.update(meta.get('pandoc', {}))

    # Get CLI options and use them to override YAML options
    options.update(arguments2options(args))

    return options


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

    # YAML chockes if we try to parse the whole file
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

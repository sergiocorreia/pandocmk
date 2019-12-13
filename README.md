# `pandocmk`: a minmalist make tool for Pandoc

Writers of complex Pandoc documents often run into three issues:

1. Very long command-line options that they need to remember (or copy-paste) all the time
2. Need for extensibility, which can be mostly solved via filters (at the cost of #1)
3. Pre/post processing tools, which *can* be solved via more complex one-liners (`pandoc ... && SumatraPDF output.pdf && ...`)

The goal of `pandocmk` is to simplify using Pandoc, by helping with #1 and a little bit with #3 (#2 is covered by e.g. `panflute`). It uses information from the YAML metadata field to build the command-line arguments, and also has extra arguments for extras I find useful (such as monitoring a file and auto-building as needed, auto-viewing in a PDF viewer, etc.).


## Existing tools

There are several good existing tools:

1. [`pandocomatic`](https://heerdebeer.org/Software/markdown/pandocomatic/) (Ruby)
2. [`panrun`](https://github.com/mb21/panrun) (Ruby; powers [panwriter](https://panwriter.com/))
3. [`rmarkdown`](https://rmarkdown.rstudio.com/) (R; powers [bookdown](https://bookdown.org/) and RStudio)
4. [`panzer`](https://github.com/msprev/panzer) (Python; inactive)

However, they don't completely fill my needs, which leads to this package.


## Usage

`pandocmk` has a few custom command-line options. Everything else is forwarded to Pandoc (and overrides whatever is set in the YAML metadata). Thus, in practice this is just a Pandoc wrapper with a few extras.

```
pandocmk [OPTIONS] [FILES]
  --view			open output file in a viewer such as SumatraPDF for .pdf
  --watch			monitor the input files for changes, and rebuild as needed
  --tex				save .tex output besides .pdf
  --timeit			show build time
  --verbose			show debugging information

  --draft			NOT IMPLEMENTED.
                    When building a Latex PDF, choose faster options (pdflatex, etc)

Note: other options are passed to Pandoc
```


## Installation

To install pandocmk, open the command line and type:

```bash
pip install pandocmk
```

Note: pandocmk requires Python 3.7 or higher.

## Uninstall

```bash
pip uninstall pandocmk
```

## Dev Install

After cloning the repo and opening the pandocmk folder:

`python setup.py install`: install the package locally

`python setup.py develop`: install locally with a symlink so changes are automatically updated


# Roadmap

- `v0.1`: use the `pandoc` metadata to build the CLI arguments
- `v0.2`: add support for the `--view` and `--watch` options
- `v0.3`: tweaks based on what we learned so far
- `v0.4`: add support for styles (should we name them output, defaults, etc.?)

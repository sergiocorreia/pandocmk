"""
Panflute filter for media files (tables, figures, estimates)

This Pandoc filter processes code blocks representing tables,
figures, and related elements (such as Tikz diagrams).
Each block is parsed as a YAML block
and used to input and build the corresponding .tex lines.
"""

# ---------------------------
# Imports
# ---------------------------

import re
from pathlib import Path
#from functools import partial

import panflute as pf


# ---------------------------
# Main filter functions
# ---------------------------

def prepare(doc):
    doc.tables = []
    doc.figures = []

    # Find position of backmatter so we don't move anything after it
    doc.backmatter_index = find_backmatter(doc)

    # Place bibliography
    # a) Before backmatter if it exists
    # b) At the end of the document otherwise
    bibliography = doc.get_metadata('bibliography')
    if bibliography:
        pos = doc.backmatter_index if doc.backmatter_index is not None else len(doc.content) + 1
        snippet = [r'\clearpage{}', rf'\bibliography{{{bibliography}}}']
        snippet = pf.RawBlock('\n'.join(snippet), format='latex')
        doc.content.insert(pos, snippet)
        #doc.content[pos:pos] = snippet
        if doc.backmatter_index:
            doc.backmatter_index += 1


def finalize(doc):
    has_backmatter = doc.tables or doc.figures
    if has_backmatter:
        pos = doc.backmatter_index   # Already searched by prepare()
        if pos is None:
            raise IndexError('Backmatter not found; add div with identifier "backmatter":\n::: {#backmatter}\n:::\n')
        backmatter = [pf.RawBlock(r'\clearpage', format='latex'), pf.Header(pf.Str('Figures and Tables'), level=1, identifier='backmatter', classes=['unnumbered'])]
        for figure in doc.figures:
            backmatter.append(figure)
        for table in doc.tables:
            backmatter.append(table)
        doc.content[pos] = pf.Div(*backmatter)
    pass


def table_fenced_action(options, data, element, doc):

    title = options.get('title', 'Untitled Table')
    subtitle = options.get('subtitle', '')
    note = options.get('note', '')

    # Run this before converting title to tex
    label = options.get('label', title2label(title))

    title = convert_text(text=title, doc=doc)
    subtitle = convert_text(text=subtitle, doc=doc)
    note = convert_text(text=note, doc=doc)

    source = options['source'] # mandatory
    is_landscape = options.get('orientation', 'portrait') == 'landscape'
    size = options.get('size', 5)

    pagebreak = doc.metadata.get('media-pagebreak', False) # Force pagebreak after media
    media_in_back = decide_media_on_back(element, doc)

    #title_suffix = ' --- ' if subtitle else ''
    title_suffix = '. ' if subtitle else ''

    snippet = ['% Table generated by panflute filter "media.py"']
    snippet.append(r'{')
    snippet.append(r'\setstretch{1.0}') # force single spacing
    if is_landscape: snippet.append(r'\begin{landscape}')
    snippet.append(r'  \begin{table}[htpb]')
    snippet.append(r'    \centering')
    snippet.append(r'    \begin{threeparttable}')
    snippet.append(rf'    \caption{{\textbf{{{title}{title_suffix}}}{subtitle}}}')
    snippet.append(rf'    \input{{"{source}"}}')
    snippet.append(r'    \begin{tablenotes}')
    snippet.append(rf'    \footnotesize \item {note}')
    snippet.append(r'    \end{tablenotes}')
    snippet.append(rf'    \label{{{label}}}')
    snippet.append(r'    \end{threeparttable}')
    snippet.append(r'  \end{table}')
    if is_landscape: snippet.append(r'\end{landscape}')
    snippet.append(r'}')
    if pagebreak: snippet.append(r'\clearpage')

    file_found = Path(source).is_file()
    snippet = latexblock(snippet, file_found)

    if media_in_back:
        doc.tables.append(snippet)
        msg = rf'\begin{{center}}\hyperref[{label}]{{[\Cref{{{label}}} about here]}}\end{{center}}'
        return pf.RawBlock(msg, format='latex')
    else:
        return snippet


def figure_fenced_action(options, data, element, doc):

    title = options.get('title', 'Untitled Table')
    subtitle = options.get('subtitle', '')
    note = options.get('note', '')

    # Run this before converting title to tex
    label = options.get('label', title2label(title))

    title = convert_text(text=title, doc=doc)
    subtitle = convert_text(text=subtitle, doc=doc)
    note = convert_text(text=note, doc=doc)

    source = options['source'] # mandatory
    is_landscape = options.get('orientation', 'portrait') == 'landscape'
    size = options.get('size', 5)

    pagebreak = doc.metadata.get('media-pagebreak', False) # Force pagebreak after media
    media_in_back = decide_media_on_back(element, doc)

    #title_suffix = ' --- ' if subtitle else ''
    title_suffix = '. ' if subtitle else ''

    # TODO: Multiple panels (with subfloat, hfill, etc.)

    snippet = ['% Figure generated by panflute filter "media.py"']
    snippet.append(r'{')
    snippet.append(r'\setstretch{1.0}') # force single spacing
    if is_landscape: snippet.append(r'\begin{landscape}')
    snippet.append(r'  \begin{figure}[htpb]')
    snippet.append(r'    \centering')
    snippet.append(rf'    \includegraphics[width=1.0\textwidth]{{"{source}"}}')
    snippet.append(rf'    \caption{{\textbf{{{title}{title_suffix}}}{subtitle}}}')
    snippet.append(rf'    \label{{{label}}}')
    snippet.append(r'  \end{figure}')
    if is_landscape: snippet.append(r'\end{landscape}')
    snippet.append(r'}')
    if pagebreak: snippet.append(r'\clearpage')

    file_found = Path(source).is_file()
    snippet = latexblock(snippet, file_found)

    if media_in_back:
        doc.figures.append(snippet)
        msg = rf'\begin{{center}}\hyperref[{label}]{{[\Cref{{{label}}} about here]}}\end{{center}}'
        return pf.RawBlock(msg, format='latex')
    else:
        return snippet



def stlog_fenced_action(options, data, element, doc):

    title = options.get('title', '')
    subtitle = options.get('subtitle', '')
    label = options.get('label', title2label(title))

    title = convert_text(text=title, doc=doc)
    subtitle = convert_text(text=subtitle, doc=doc)

    source = options['source'] # mandatory
    size = options.get('size', 5)

    pagebreak = doc.metadata.get('media-pagebreak', False) # Force pagebreak after media
    media_in_back = decide_media_on_back(element, doc)

    # OVERRIDE MEDIA ON BACK
    media_in_back = False

    title_suffix = '. ' if subtitle else ''

    snippet = ['% Snippet generated by panflute filter "media.py"']
    snippet.append(r'{')
    
    if title or subtitle:
        snippet.append(r'  \begin{figure}[htpb]')
        snippet.append(r'    \centering')
    
    snippet.append(r'\begin{stlog}')
    snippet.append(rf'\input{{{source}}}\nullskip')
    snippet.append(r'\end{stlog}')
    
    if title or subtitle:
        snippet.append(rf'    \caption{{\textbf{{{title}{title_suffix}}}{subtitle}}}')
    if label:
        snippet.append(rf'    \label{{{label}}}')
    if title or subtitle:
        snippet.append(r'  \end{figure}')
    snippet.append(r'}')

    if pagebreak: snippet.append(r'\clearpage')

    file_found = Path(source).is_file()
    snippet = latexblock(snippet, file_found)

    if media_in_back:
        doc.figures.append(snippet)
        msg = rf'\begin{{center}}\hyperref[{label}]{{[\Cref{{{label}}} about here]}}\end{{center}}'
        return pf.RawBlock(msg, format='latex')
    else:
        return snippet


# ---------------------------
# Aux functions
# ---------------------------

def convert_text(text, doc):
    '''Create function that converts text taking into account citations'''
    #bibliography = doc.get_metadata('bibliography')
    #extra_args = ['--natbib', f'--bibliography="{bibliography}"'] if '@' in text and bibliography is not None else []
    extra_args = ['--natbib'] # no need to pass --bibliography
    # TODO: Allow citeproc with .pdf destination (instead of .tex destination)
    return pf.convert_text(text=text, output_format='latex', extra_args=extra_args)


def find_backmatter(doc):
    for i, elem in enumerate(doc.content):
        if isinstance(elem, pf.Div) and elem.identifier == 'backmatter':
            return i # we could also have used elem.index
    return None


def decide_media_on_back(elem, doc):
    media_in_back = doc.metadata.get('media-in-back', True) # Move media to back

    # Don't move to back if we are already after the backmatter i.e. if we are in the appendix
    # Note that this code is fragile (doesn't work if it's nested within divs)
    if doc.backmatter_index is not None and elem.parent.tag=='Doc' and elem.index > doc.backmatter_index:
        media_in_back = False

    return media_in_back


def title2label(title):
    #label = pf.stringify(title)
    label = title.lower().replace(' ', '-')
    label = re.sub(r'[^a-z_.-]+', '', label)
    return label


def latexblock(code, file_found=True):
    """LaTeX block"""
    if file_found:
        return pf.RawBlock('\n'.join(code), format='latex')
    else:
        return pf.CodeBlock('\n'.join(code))


# ---------------------------
# Main
# ---------------------------

def main(doc=None):
    tags = {'table': table_fenced_action, 'figure': figure_fenced_action, 'stlog': stlog_fenced_action}
    return pf.run_filter(action=pf.yaml_filter, prepare=prepare, finalize=finalize, tags=tags, doc=doc) 


if __name__ == '__main__':
    main()
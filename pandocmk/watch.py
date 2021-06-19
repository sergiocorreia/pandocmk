"""
Code related to monitoring changes to input files
"""


# ---------------------------
# Imports
# ---------------------------

import time
import datetime
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .core import build_output


class MarkdownUpdateHandler(FileSystemEventHandler):

    def __init__(self, fn, timeit, tex, latexmk, retry, verbose, pandoc_options):
        self.fn = fn
        self.fn = fn
        self.timeit = timeit
        self.tex = tex
        self.latexmk = latexmk
        self.retry = retry
        self.verbose = verbose
        self.pandoc_options = pandoc_options
        self.last_update =  datetime.datetime(1,1,1) # Pick any old datetime

    def on_moved(self, event):
        return

    def on_created(self, event):
        return

    def on_deleted(self, event):
        return

    def on_modified(self, event):
        if event.is_directory:
            return

        fn_modified = Path(event.src_path)

        #if (fn_modified.suffix != '.md'):
        #    return
        
        if fn_modified.name != self.fn.name:
            return

        t = datetime.datetime.now()
        delta = t - self.last_update

        # Return if not enough time passed (also prevents duplicate entries)
        if delta < datetime.timedelta(seconds=0.1):
            return
        else:
            print(delta)

        print(f' - File "{self.fn}" modified ({t.strftime("%I:%M:%S %p")})')
        # view=False as we don't need SumatraPDF to steal windows focus every time we save
        #self.last_update = t
        build_output(self.fn, view=False, timeit=self.timeit, tex=self.tex, latexmk=self.latexmk, retry=self.retry, verbose=self.verbose, pandoc_options=self.pandoc_options)
        self.last_update = datetime.datetime.now()
        #print(event.src_path, event.key, event.event_type)


# ---------------------------
# Functions
# ---------------------------

def monitor_file(md_fn, timeit, tex, latexmk, retry, verbose, pandoc_options):

    path = '.'
    print(f'Monitoring file "{md_fn}" in directory {path}')

    event_handler = MarkdownUpdateHandler(fn=md_fn, timeit=timeit, tex=tex, latexmk=latexmk, retry=retry, verbose=verbose, pandoc_options=pandoc_options)

    observer = Observer(timeout=1)
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print('File monitor stopped')


"""
Code for opening external viewers (SumatraPDF)
"""


# ---------------------------
# Imports
# ---------------------------

#import subprocess # import Popen, PIPE
import webbrowser


# ---------------------------
# Functions
# ---------------------------

def run_viewer(pdf_fn, verbose=False):
	# https://stackoverflow.com/a/15055133
	webbrowser.open(str(pdf_fn))


def old_run_viewer(pdf_fn, verbose=False):
    cmd = ['SumatraPDF.exe', str(pdf_fn), '-reuse-instance']
    if verbose:
    	print("[CMD]", ' '.join(cmd))
    subprocess.Popen(cmd)

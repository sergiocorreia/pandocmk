"""
Code for opening external viewers (SumatraPDF)
"""


# ---------------------------
# Imports
# ---------------------------

import subprocess # import Popen, PIPE


# ---------------------------
# Functions
# ---------------------------

def run_viewer(pdf_fn, verbose=False):
    cmd = ['SumatraPDF.exe', str(pdf_fn), '-reuse-instance']
    if verbose:
    	print("[CMD]", ' '.join(cmd))
    subprocess.Popen(cmd)

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

def run_viewer(pdf_fn):
    cmd = ['SumatraPDF.exe', str(pdf_fn), '-reuse-instance']
    #nice_print("CMD", cmd)
    subprocess.Popen(cmd)

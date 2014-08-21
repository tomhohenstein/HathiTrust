HathiTrust
==========

Export and process files from Alma to generate annual HathiTrust report of Print Holdings.

The two files:

* HathiTrustAnnualReportPhysicalTitles.ipynb
* HathiTrustAnnualReportPhysicalTitles.py

perform the same operations. The first is an ipython notebook file, my primary development platform. The second is simply an export of the code in a standard python notebook.

These were developed in a python 2.7 environment.

The script assumes the presence of binary marc files with the file extension "*.mrc" reside in the same directory. The script creates a list of the file names, open's each file, reading record by record and creating an entry in the appropriate TSV file for the records.

The script runs without error in my environment, but has not been thoroughly tested. I could probably benefit from additional error and exception handling.




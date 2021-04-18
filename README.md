## encode_to_datamatrix.py
- In: A file needs to be present in the folder `encode/`. The algorigthm will choose the file with the latest date modified.
- Out: A series of datamatrix PNG files `encode/out/*.png`, containing the text of the input file.

## decode_from_datamatrix
- In: A text file of the form `decode/*.txt`, containing the scanned (with help of a 2D barcode scanner) text of all datamatrix fields. The user need not take care of the order in which he scans the fields. Scanning a field twice also has no adverse affects.
- Out: A text file `decode/out.txt` with the text of the original file.

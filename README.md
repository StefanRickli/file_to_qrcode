## encode_to_qrcode.py
- In: A file needs to be present in the folder `encode/in/`. The algorigthm will choose the file with the latest date modified.
- Out: A series of datamatrix PNG files `encode/out/*.png`, containing the text of the input file.

## decode_from_qrcode.py
- In: A text file of the form `decode/in/*.txt`, containing the scanned (with help of a 2D barcode scanner) text of all datamatrix fields. The user need not take care of the order in which he scans the fields. Scanning a field twice also has no adverse affects.
- Out: A file `decode/out/*` with the content of the original file.

## Example output
### First page
![image](https://user-images.githubusercontent.com/19881323/115163513-ca5de380-a0a9-11eb-8190-2083fc931734.png)

### Content pages
![image](https://user-images.githubusercontent.com/19881323/115163517-d47fe200-a0a9-11eb-9ba8-d5302b3cc524.png)

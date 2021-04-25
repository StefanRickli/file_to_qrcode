# A word of caution
This project is very active at the moment and the decoder currently is broken because a lot of changes in the content header happened.

Todo:
- Fix decoder
- Make the program a CLI
- Control app behavior using args
- Add different page layouts
- Add restoration verification
- Add source code of encoder (and decoder?) to the first PDF page

## backup_to_qrcode.py
```
usage: backup_to_qrcode.py [-h] -s SOURCE -d DESTINATION [-l LOGFILE] [--chunk_size CHUNK_SIZE] [--qr_code_eclevel QR_CODE_ECLEVEL] [--preserve_tempfiles]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
  -d DESTINATION, --destination DESTINATION
  -l LOGFILE, --logfile LOGFILE
  --chunk_size CHUNK_SIZE
                        Sets the size of the data chunks in # of characters. Note that this does not inlcude the chunk header.
  --qr_code_eclevel QR_CODE_ECLEVEL
                        Determines the error correction level of the QR code. Valid arguments are "L", "M", "Q", "H"
  --preserve_tempfiles  If destination is a PDF file, this flag will prevent the image files to be deleted
  ```

## restore_from_scan.py
- In: A text file of the form `restore/in/*.txt`, containing the scanned (with help of a 2D barcode scanner) text of all QR codes. The user need not take care of the order in which he scans the fields. Scanning a field twice also has no adverse affects.
- Out: A file in `restore/out/` with the content of the original file.

## Example output
### First page
![image](https://user-images.githubusercontent.com/19881323/115163513-ca5de380-a0a9-11eb-8190-2083fc931734.png)

### Content pages
![image](https://user-images.githubusercontent.com/19881323/115163517-d47fe200-a0a9-11eb-9ba8-d5302b3cc524.png)

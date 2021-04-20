# A word of caution
This project is very active at the moment and the decoder currently is broken because a lot of changes in the content header happened.

Todo:
- Fix decoder
- Rename folders
- Make the program a CLI
- Control app behavior using args
- Add different page layouts
- Add restoration verification
- Add source code of encoder (and decoder?) to the first PDF page
- Use alternative way to refer to a unique commit on first page

## backup_to_qrcode.py
- In: A file needs to be present in the folder `backup/in/`. The algorigthm will choose the file with the latest date modified.
- Out: A series of QR code PNG files `backup/out/*.png`, containing the text of the input file.

## restore_from_scan.py
- In: A text file of the form `restore/in/*.txt`, containing the scanned (with help of a 2D barcode scanner) text of all QR codes. The user need not take care of the order in which he scans the fields. Scanning a field twice also has no adverse affects.
- Out: A file in `restore/out/` with the content of the original file.

## Example output
### First page
![image](https://user-images.githubusercontent.com/19881323/115163513-ca5de380-a0a9-11eb-8190-2083fc931734.png)

### Content pages
![image](https://user-images.githubusercontent.com/19881323/115163517-d47fe200-a0a9-11eb-9ba8-d5302b3cc524.png)

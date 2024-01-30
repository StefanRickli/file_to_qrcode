# Python module that converts any binary file into a PDF with QR codes
## Use Case

I personally use this converter to have a physical, printed, and machine readable copy of my OnlyKey backup which I then put into a bank safe. The backup printouts stack over time but so what, I only do that once in a while, so it hasn't bothered me yet.

The advantage with this approach is that

- I don't need a flash drive in the bank vault that I first have to retrieve, bring to my house, fill with the current backup, then bring it back to the bank. OR,
- I don't need to bring a laptop to the bank where I would manipulate the flash drive.


# A word of caution
This project is not actively maintained and the decoder might be broken because a lot of changes in the content header happened in the last few commits.
As of 2024-01-30, restoration worked for a test text file of moderate size.

Nevertheless, I hope you find it a good source of inspiration, and if you come up with a sensible addition, feel free to make a pull request.

Todo:
- Add different page layouts
- Add restoration verification
- Add source code of decoder (and encoder?) to the first PDF page
- Refactor code such that backup and restore can be tested by testsuite

## backup_to_qrcode.py
```
usage: backup_to_qrcode.py [-h] -s SOURCE -d DESTINATION [-l LOGFILE] [--chunk_size CHUNK_SIZE] [--qr_code_eclevel QR_CODE_ECLEVEL] [--preserve_tempfiles]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
  -d DESTINATION, --destination DESTINATION
                        Can be either a PDF file or a folder. In case of folder, only QR code PNG files are created.
  -l LOGFILE, --logfile LOGFILE
  --chunk_size CHUNK_SIZE
                        Sets the size of the data chunks in # of characters. Note that this does not inlcude the chunk header.
  --qr_code_eclevel QR_CODE_ECLEVEL
                        Determines the error correction level of the QR code. Valid arguments are "L", "M", "Q", "H".
  --preserve_tempfiles  If destination is a PDF file, this flag will prevent the temporary image files to be deleted.
  ```

## restore_from_scan.py
```
usage: restore_from_scan.py [-h] -s SOURCE [-d DESTINATION] [-l LOGFILE]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
  -d DESTINATION, --destination DESTINATION
                        Can be either a file or folder.
  -l LOGFILE, --logfile LOGFILE
```

## Example output
### First page
![image](https://user-images.githubusercontent.com/19881323/115163513-ca5de380-a0a9-11eb-8190-2083fc931734.png)

### Content pages
![image](https://user-images.githubusercontent.com/19881323/115163517-d47fe200-a0a9-11eb-9ba8-d5302b3cc524.png)

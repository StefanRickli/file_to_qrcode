import treepoem


def get_test_qrcode():
    test_string = '0123456789 ABCDEFGHIJKLMNOPQRSTUVWXYZ $ % * + - . / :'

    image = treepoem.generate_barcode('qrcode', test_string, {'eclevel': 'Q'})
    out_filename = './assets/test_scanner_charset.png'
    image.save(out_filename)

    return (test_string, image)

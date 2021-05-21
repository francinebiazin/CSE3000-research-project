from PIL import Image
import imagehash
from os import walk
import csv


mullvad_path = 'data/screenshots/2021-5-19-mullvad'
control_path = 'data/screenshots/2021-5-19-control-test'
results_path = 'analysis/screenshots/2021-5-19-phash.csv'
date = '2021-5-19'

_, _, mullvad_screenshots = next(walk(mullvad_path))
_, _, control_screenshots = next(walk(control_path))


def get_phash_values():
    headers = [
        'Image',
        'Mullvad Hash',
        'Control Hash',
        'Difference'
    ]

    with open(results_path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()

        for image in mullvad_screenshots:
            if image in control_screenshots:
                mullvad_hash = imagehash.average_hash(Image.open(mullvad_path + '/' + image))
                control_hash = imagehash.average_hash(Image.open(control_path + '/' + image))
                difference = mullvad_hash - control_hash
                data = {
                    'Image': image,
                    'Mullvad Hash': mullvad_hash,
                    'Control Hash': control_hash,
                    'Difference': difference
                }
                writer.writerow(data)
            else:
                data = {
                    'Image': image,
                    'Mullvad Hash': 'none',
                    'Control Hash': 'none',
                    'Difference': 'none'
                }
                writer.writerow(data)


get_phash_values()


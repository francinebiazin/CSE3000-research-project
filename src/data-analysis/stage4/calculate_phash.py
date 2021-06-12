from PIL import Image
import imagehash
from os import walk
import csv

date = '2021-6-12'

mullvad_path = 'data/stage4/screenshots/{}-mullvad'.format(date)
control_path = 'data/stage4/screenshots/{}-control'.format(date)
results_path = 'analysis/stage4/screenshots/{}-phash.csv'.format(date)

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
            if date not in image:
                continue
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

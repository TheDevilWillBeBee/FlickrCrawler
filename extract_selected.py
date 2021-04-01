import os
import cv2
import json
import argparse
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from shutil import copyfile


def build_parser():
    parser = argparse.ArgumentParser(description="""Show images to user and allow him to select the desired images.""")
    parser.add_argument('tag', type=str)
    parser.add_argument('--out', type=str, default='data/')
    parser.add_argument('--allow-upsampled', action='store_true', default=False)
    return parser


def extract_selected_images(args):
    if not os.path.exists(os.path.join(args.out, args.tag, "selected_images")):
        os.makedirs(os.path.join(args.out, args.tag, "selected_images"))

    selected_meta = {}
    with open(os.path.join(args.out, f"{args.tag}/meta.json"), 'r') as f:
        meta = json.load(f)

    i = 0
    for photo_id in tqdm(meta):
        if 'is_valid' not in meta[photo_id]['metadata']:
            continue
        if meta[photo_id]['metadata']['is_valid']:
            if not args.allow_upsampled:
                if meta[photo_id]['image']['upsample']:
                    continue
            photo_new_meta = deepcopy(meta[photo_id])
            selected_photo_id = str(i).zfill(6)
            photo_new_meta['image']['file_path'] = photo_new_meta['image']['file_path'].replace(photo_id,
                                                                                                selected_photo_id)
            photo_new_meta['image']['file_path'] = photo_new_meta['image']['file_path'].replace('images',
                                                                                                'selected_images')
            selected_meta[selected_photo_id] = photo_new_meta
            copyfile(meta[photo_id]['image']['file_path'], photo_new_meta['image']['file_path'])
            i += 1

    with open(os.path.join(args.out, f"{args.tag}/selected_meta.json"), 'w') as f:
        f.write(json.dumps(selected_meta, indent=4, sort_keys=True))


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    extract_selected_images(args)

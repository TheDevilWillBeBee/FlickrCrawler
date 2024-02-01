import os
import json
import argparse
import requests
import numpy as np
from PIL import Image
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO



def build_parser():
    parser = argparse.ArgumentParser(description="""Fetch images from Flickr API for a meta file.""")
    parser.add_argument('tag', type=str)
    parser.add_argument('--out', type=str, default='data/')
    parser.add_argument('--num-workers', type=int, default=16)
    parser.add_argument('--limit-total', type=int, default=1000)
    return parser


width, height = 256, 256


def center_crop_resize(image):
    w, h = image.size  # Get dimensions

    s = min(w, h)
    left = (w - s) / 2
    top = (h - s) / 2
    right = (w + s) / 2
    bottom = (h + s) / 2

    # Crop the center of the image
    image = image.crop((left, top, right, bottom))
    image = image.resize((width, height))
    return image


def download_image_and_save(metadata, image_path, photo_id):
    url = metadata['metadata']['download_url']
    # file_extension = url.split('/')[-1].split('.')[-1]
    file_path = f'{image_path}/{photo_id}.jpg'
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))

        upsample = False
        original_size = image.size
        if image.size[0] < width or image.size[1] < height:
            upsample = True

        image = center_crop_resize(image)
        image.save(file_path)

        result = {
            "upsample": upsample,
            "original_size": original_size,
            "file_path": file_path
        }
        return result
    except:
        return None


def update_meta(args):
    with open(os.path.join(args.out, f"{args.tag}/meta.json"), 'r') as f:
        meta = json.load(f)

    image_path = os.path.join(args.out, args.tag, 'images')

    image_list = os.listdir(image_path)
    image_indices = [s.split('.')[0] for s in image_list]

    for photo_id in image_indices:
        if 'image' in meta[photo_id]:
            pass
        else:
            meta[photo_id]['image'] = {
                "file_path": f'{image_path}/{photo_id}.jpg'
            }

    with open(os.path.join(args.out, f"{args.tag}/meta.json"), 'w') as f:
        f.write(json.dumps(meta, indent=4, sort_keys=True))





def fetch_images(args):
    with open(os.path.join(args.out, f"{args.tag}/meta.json"), 'r') as f:
        meta = json.load(f)

    image_path = os.path.join(args.out, args.tag, 'images')
    if not os.path.exists(image_path):
        os.makedirs(image_path)

    worker_pool = multiprocessing.Pool(args.num_workers)
    worker_args = []
    for photo_id in meta:
        if 'image' not in meta[photo_id]:
            worker_args.append((meta[photo_id], image_path, photo_id))

    worker_args = worker_args[:args.limit_total]
    print("Total images to be fetched: ", len(worker_args))
    result = worker_pool.starmap(download_image_and_save, worker_args)
    for r, (_, _, photo_id) in enumerate(worker_args):
        if result[r] is not None:
            meta[photo_id]['image'] = result[r]

    with open(os.path.join(args.out, f"{args.tag}/meta.json"), 'w') as f:
        f.write(json.dumps(meta, indent=4, sort_keys=True))


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    fetch_images(args)
    # update_meta(args)
    executor = ThreadPoolExecutor(max_workers=args.num_workers)

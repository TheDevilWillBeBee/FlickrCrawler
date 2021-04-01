import os
import json
import argparse
import requests
import numpy as np
from PIL import Image
import multiprocessing
from concurrent.futures import ThreadPoolExecutor


def build_parser():
    parser = argparse.ArgumentParser(description="""Fetch images from Flickr API for a meta file.""")
    parser.add_argument('tag', type=str)
    parser.add_argument('--out', type=str, default='data/')
    parser.add_argument('--num-workers', type=int, default=8)
    parser.add_argument('--width', type=int, default=1024)
    parser.add_argument('--height', type=int, default=1024)
    return parser


width, height = None, None


def center_crop_resize(image):
    image = np.array(image)
    crop = np.min(image.shape[:2])
    image = image[(image.shape[0] - crop) // 2: (image.shape[0] + crop) // 2,
            (image.shape[1] - crop) // 2: (image.shape[1] + crop) // 2]
    image = Image.fromarray(image, 'RGB')
    image = image.resize((width, height), Image.LANCZOS)
    return image


def download_image_and_save(metadata, image_path, photo_id):
    url = metadata['metadata']['download_url']
    # file_extension = url.split('/')[-1].split('.')[-1]
    file_path = f'{image_path}/{photo_id}.jpg'
    response = requests.get(url, stream=True)
    image = Image.open(response.raw)
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


def fetch_images(args):
    global width, height
    width = args.width
    height = args.height
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
    executor = ThreadPoolExecutor(max_workers=args.num_workers)

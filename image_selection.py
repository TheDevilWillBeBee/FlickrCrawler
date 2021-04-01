import os
import cv2
import json
import argparse
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor


def build_parser():
    parser = argparse.ArgumentParser(description="""Show images to user and allow him to select the desired images.""")
    parser.add_argument('tag', type=str)
    parser.add_argument('--out', type=str, default='data/')
    return parser


key_mapping = {
    83: "right",
    81: "left",
    ord('a'): "add",
    ord('d'): "delete",

}


def select_images(args):
    with open(os.path.join(args.out, f"{args.tag}/meta.json"), 'r') as f:
        meta = json.load(f)

    meta_updated = deepcopy(meta)
    photo_ids = list(meta.keys())
    i = 0
    while True:
        if i >= len(photo_ids):
            break
        photo_id = photo_ids[i]
        metadata = meta[photo_id]['metadata']
        if "is_valid" in metadata:
            i += 1
            continue
        if 'image' in meta[photo_id]:
            image_path = meta[photo_id]['image']['file_path']
        else:
            i += 1
            continue
        if not os.path.exists(image_path):
            i += 1
            continue
        image = cv2.imread(image_path)
        image = cv2.resize(image, (512, 512))
        cv2.putText(image, f'{photo_id}',
                    (15, 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1)
        cv2.imshow(f"{args.tag}", image)

        k = cv2.waitKey(0)
        if k == 27:  # Escape pressed
            break
        if k not in key_mapping:
            continue
        if key_mapping[k] == 'right':
            i += 1
        elif key_mapping[k] == 'left':
            i -= 1
        elif key_mapping[k] == 'add':
            i += 1
            meta_updated[photo_id]['metadata']['is_valid'] = True
        elif key_mapping[k] == 'delete':
            i += 1
            meta_updated[photo_id]['metadata']['is_valid'] = False

    cv2.destroyAllWindows()

    with open(os.path.join(args.out, f"{args.tag}/meta.json"), 'w') as f:
        f.write(json.dumps(meta_updated, indent=4, sort_keys=True))


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    select_images(args)

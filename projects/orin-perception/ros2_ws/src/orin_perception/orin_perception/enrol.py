# SPDX-License-Identifier: MIT
"""Enrol a face into the gallery from image files, or list it. Live enrolment goes through
the running node instead (publish the name on /orin/enroll), as on the HAT half.

  ros2 run orin_perception enrol -- --name alice --images a.jpg b.jpg  # mean of the files' largest faces
  ros2 run orin_perception enrol -- --list
"""
import argparse
import os
import sys

import cv2
import numpy as np

from . import arcface, scrfd
from .gallery import Gallery
from .trt_runtime import TrtRunner


def embed_largest(det, emb, img, size, thresh):
    blob, r = scrfd.preprocess(img, size)
    faces = scrfd.decode(det(blob), size, r, thresh)
    if not faces:
        return None
    x1, y1, x2, y2, sc, kps = max(faces, key=lambda f: (f[2] - f[0]) * (f[3] - f[1]))
    crop = arcface.norm_crop(img, kps)
    if crop is None:
        return None
    return arcface.normalize(next(iter(emb(arcface.preprocess(crop)).values())))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--name')
    ap.add_argument('--images', nargs='*')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--models-dir', default='~/models')
    ap.add_argument('--gallery-dir', default='~/orin/gallery')
    ap.add_argument('--embedding-model', default='insightface-buffalo_sc/w600k_mbf')
    ap.add_argument('--det-size', type=int, default=640)
    ap.add_argument('--det-thresh', type=float, default=0.5)
    a = ap.parse_args(argv)
    gal = Gallery(a.gallery_dir, a.embedding_model)
    if a.list:
        print(f'{gal.dir}: {gal.names}')
        return 0
    if not a.name or not a.images:
        ap.error('--name and --images are required unless --list')
    md = os.path.expanduser(a.models_dir)
    det = TrtRunner(os.path.join(md, 'det_500m.engine'))
    emb = TrtRunner(os.path.join(md, 'w600k_mbf.engine'))

    embs = []
    for path in a.images:
        img = cv2.imread(path)
        e = embed_largest(det, emb, img, a.det_size, a.det_thresh) if img is not None else None
        print(f'{path}: {"ok" if e is not None else "no face"}')
        if e is not None:
            embs.append(e)
    if not embs:
        print('no face captured; nothing enrolled', file=sys.stderr)
        return 1
    sims = np.asarray(embs) @ np.asarray(embs).T
    print(f'{len(embs)} embeddings; min pairwise cosine between them {sims.min():.3f}')
    gal.add(a.name, np.mean(embs, axis=0))
    print(f'enrolled {a.name!r} -> {gal.dir}; gallery now {gal.names}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

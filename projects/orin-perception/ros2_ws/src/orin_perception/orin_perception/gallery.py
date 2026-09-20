# SPDX-License-Identifier: MIT
"""Enrolled-face gallery, in the format the AI HAT+ 2 half of the perception bench defined
(projects/devastator/software/ros2/hailo_perception): a directory of ``<name>.txt`` files,
each 512 floats one per line, the L2-normalised ArcFace embedding. Match is cosine
(dot product of unit vectors) against every file; best wins if above the threshold.

The *format* is shared between hosts; the *contents* are not: embeddings from different
weights (Hailo's arcface_mobilefacenet vs InsightFace's w600k_mbf) are not comparable, so a
gallery is only meaningful on the host, and with the model, that wrote it. ``model.txt`` in
the directory records which model wrote it; the node warns on a mismatch.
"""
import os

import numpy as np

DIM = 512


class Gallery:
    def __init__(self, gallery_dir, embedding_model, warn=print):
        self.dir = os.path.expanduser(gallery_dir)
        self.embedding_model = embedding_model
        self.names, self.mat = [], np.zeros((0, DIM), np.float32)
        self.load(warn)

    def load(self, warn=print):
        self.names, rows = [], []
        if not os.path.isdir(self.dir):
            self.mat = np.zeros((0, DIM), np.float32)
            return
        tag = os.path.join(self.dir, 'model.txt')
        if os.path.exists(tag):
            written_by = open(tag).read().strip()
            if written_by != self.embedding_model:
                warn(f'gallery {self.dir} was written with {written_by!r}, this node embeds with '
                     f'{self.embedding_model!r}; similarities will be meaningless')
        for fn in sorted(os.listdir(self.dir)):
            if not fn.endswith('.txt') or fn == 'model.txt':
                continue
            v = np.loadtxt(os.path.join(self.dir, fn), dtype=np.float32).reshape(-1)
            if v.size != DIM:
                warn(f'gallery: {fn} has {v.size} values, expected {DIM}')
                continue
            self.names.append(fn[:-4])
            rows.append(v / max(np.linalg.norm(v), 1e-6))
        self.mat = np.asarray(rows, np.float32).reshape(-1, DIM)

    def add(self, name, emb):
        """Write <name>.txt (replacing any previous enrolment of that name) and reload."""
        os.makedirs(self.dir, exist_ok=True)
        emb = np.asarray(emb, np.float32).reshape(-1)
        emb = emb / max(np.linalg.norm(emb), 1e-6)
        np.savetxt(os.path.join(self.dir, f'{name}.txt'), emb, fmt='%.8g')
        with open(os.path.join(self.dir, 'model.txt'), 'w') as f:
            f.write(self.embedding_model + '\n')
        self.load()

    def match(self, emb, threshold):
        """(name or 'unknown', best cosine); best is -1 with an empty gallery, as on the HAT."""
        if len(self.names) == 0:
            return 'unknown', -1.0
        sims = self.mat @ np.asarray(emb, np.float32)
        i = int(sims.argmax())
        return (self.names[i] if sims[i] >= threshold else 'unknown'), float(sims[i])

    def __len__(self):
        return len(self.names)

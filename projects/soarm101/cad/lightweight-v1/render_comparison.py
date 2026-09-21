#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render the actual STEP geometry with a software depth buffer; no GPU needed."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from numba import njit
import numpy as np

from generate import HERE, load_part


@njit
def raster(triangles, colors, width, height):
    pixels = np.ones((height,width,3))*.97
    depth = np.ones((height,width))*(-1e20)
    for i in range(len(triangles)):
        a,b,c = triangles[i]
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:
            continue
        for y in range(max(0,int(min(a[1],b[1],c[1]))), min(height,int(max(a[1],b[1],c[1]))+2)):
            for x in range(max(0,int(min(a[0],b[0],c[0]))), min(width,int(max(a[0],b[0],c[0]))+2)):
                u=((b[1]-c[1])*(x+.5-c[0])+(c[0]-b[0])*(y+.5-c[1]))/den
                v=((c[1]-a[1])*(x+.5-c[0])+(a[0]-c[0])*(y+.5-c[1]))/den
                w=1-u-v
                if u>=-1e-8 and v>=-1e-8 and w>=-1e-8:
                    z=u*a[2]+v*b[2]+w*c[2]
                    if z>depth[y,x]:
                        depth[y,x]=z
                        pixels[y,x]=colors[i]
    return pixels


def draw(shape, color, eye, width=700, height=520):
    vertices, faces=shape.tessellate(.04,.12)
    tri=np.array([v.toTuple() for v in vertices])[np.array(faces)]
    eye=np.array(eye,dtype=float);eye/=np.linalg.norm(eye)
    right=np.cross([0,0,1],eye);right/=np.linalg.norm(right)
    up=np.cross(eye,right)
    R=np.array([right,up,eye])
    n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12)
    light=eye+np.array([-.3,-.3,.6]);light/=np.linalg.norm(light)
    shade=.35+.65*np.maximum(n@light,0)
    colors=np.array(color)[None,:]*shade[:,None]
    projected=tri@R.T
    lo=projected.min(axis=(0,1));hi=projected.max(axis=(0,1));center=(lo+hi)/2
    scale=min((width-60)/(hi[0]-lo[0]),(height-60)/(hi[1]-lo[1]))
    projected=(projected-center)*scale
    projected[:,:,0]+=width/2
    projected[:,:,1]=height/2-projected[:,:,1]
    return raster(projected,colors,width,height)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream",type=Path,required=True)
    args=ap.parse_args()
    geometry=json.loads((HERE/"analysis/geometry.json").read_text())
    slices=json.loads((HERE/"analysis/slices-p3.json").read_text())["parts"]
    modified=[p for p in geometry["parts"] if p["modified"]]
    fig,axs=plt.subplots(len(modified),2,figsize=(12,5*len(modified)),squeeze=False)
    for axes,row in zip(axs,modified):
        name=row["part"]
        for ax,variant,path in zip(axes,["original","candidate"],[args.upstream/row["source"],HERE/"step"/(name+".step")]):
            image=draw(load_part(path),[.76,.81,.87] if variant=="original" else [.28,.72,.70],
                       [1,-1.8,.9] if name=="Base_SO101" else [.6,-.8,2])
            ax.imshow(image);ax.axis("off")
            ax.set_title(f"{name.removesuffix('_SO101')} · {variant}\n{slices[name][variant]['part_mass_g']:.1f} g sliced part")
    fig.suptitle("SO-101: retained prototype changes\nActual STEP geometry · same print settings · strength untested",fontsize=16)
    fig.tight_layout(rect=[0,0,1,.94])
    (HERE/"figures").mkdir(exist_ok=True)
    fig.savefig(HERE/"figures/comparison.png",dpi=140);plt.close(fig)

    names=list(slices)
    a=np.array([slices[n]["original"]["part_mass_g"] for n in names])
    b=np.array([slices[n]["candidate"]["part_mass_g"] for n in names])
    order=np.argsort(a)
    fig,ax=plt.subplots(figsize=(11,6))
    ax.barh(np.arange(len(a))+.18,a[order],height=.36,label="Original",color="#a6b4c3")
    ax.barh(np.arange(len(a))-.18,b[order],height=.36,label="Prototype",color="#239e99")
    ax.set_yticks(np.arange(len(a)),[names[i].replace('_SO101','').replace('_',' ') for i in order])
    ax.set_xlabel("Sliced part mass / g (supports excluded)");ax.legend();ax.grid(axis="x",alpha=.2)
    ax.set_title(f"Eleven prints: {a.sum():.1f} → {b.sum():.1f} g · {100*(1-b.sum()/a.sum()):.1f}% saving")
    fig.tight_layout();fig.savefig(HERE/"figures/mass.png",dpi=150);plt.close(fig)


if __name__=="__main__":
    main()

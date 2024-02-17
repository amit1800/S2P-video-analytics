from pathlib import Path
from typing import List, Tuple, Union

import cv2
import numpy as np
from numpy import ndarray


from torch import Tensor
from typing import Tuple
from torchvision.ops import nms

# image suffixes
SUFFIXES = ('.bmp', '.dng', '.jpeg', '.jpg', '.mpo', '.png', '.tif', '.tiff',
            '.webp', '.pfm')


def letterbox(im: ndarray,
              new_shape: Union[Tuple, List] = (640, 640),
              color: Union[Tuple, List] = (114, 114, 114)) \
        -> Tuple[ndarray, float, Tuple[float, float]]:
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    # new_shape: [width, height]

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[1], new_shape[1] / shape[0])
    # Compute padding [width, height]
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[0] - new_unpad[0], new_shape[1] - new_unpad[
        1]  # wh padding

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im,
                            top,
                            bottom,
                            left,
                            right,
                            cv2.BORDER_CONSTANT,
                            value=color)  # add border
    return im, r, (dw, dh)


def blob(im: ndarray, return_seg: bool = False) -> Union[ndarray, Tuple]:
    seg = None
    if return_seg:
        seg = im.astype(np.float32) / 255
    im = im.transpose([2, 0, 1])
    im = im[np.newaxis, ...]
    im = np.ascontiguousarray(im).astype(np.float32) / 255
    if return_seg:
        return im, seg
    else:
        return im


def path_to_list(images_path: Union[str, Path]) -> List:
    if isinstance(images_path, str):
        images_path = Path(images_path)
    assert images_path.exists()
    if images_path.is_dir():
        images = [
            i.absolute() for i in images_path.iterdir() if i.suffix in SUFFIXES
        ]
    else:
        assert images_path.suffix in SUFFIXES
        images = [images_path.absolute()]
    return images


def det_postprocess(data: Tuple[Tensor, Tensor, Tensor, Tensor]):
    assert len(data) == 4
    iou_thres: float = 0.65
    num_dets, bboxes, scores, labels = data[0][0], data[1][0], data[2][
        0], data[3][0]
    nums = num_dets.item()
    if nums == 0:
        return bboxes.new_zeros((0, 4)), scores.new_zeros(
            (0, )), labels.new_zeros((0, ))
    # check score negative
    scores[scores < 0] = 1 + scores[scores < 0]
    # add nms
    bboxes_n = bboxes.to('cpu').numpy()
    scores_n = scores.to('cpu').numpy()
    idx = nms(bboxes, scores, iou_thres)
    # print(idx)
    bboxes, scores, labels = bboxes[idx], scores[idx], labels[idx]
    bboxes = bboxes[:nums]
    scores = scores[:nums]
    labels = labels[:nums]
    return bboxes, scores, labels

import cv2
import numpy as np
from shapely.geometry import Polygon, Point
import math


def get_center(poly_x, poly_y):
    poly = Polygon([(x, y) for x, y in zip(poly_x, poly_y)])
    c = poly.centroid
    return (c.x, c.y)

def get_length(poly_x, poly_y):
    poly = Polygon([(x, y) for x, y in zip(poly_x, poly_y)])
    xy = poly.minimum_rotated_rectangle.exterior.coords
    return max(Point(xy[0]).distance(Point(xy[1])),
               Point(xy[1]).distance(Point(xy[2])))


def simplify_curve(pts, tolerance):
    """
    The Ramer-Douglas-Pecker algorithm is an algorithm that allows you to reduce the number of curve points
    approximated by a larger point in the series.
    :param pts:
    :param tolerance:
    :return:
    """
    if len(pts) <= 2:
        return pts
    anchor = 0
    floater = len(pts) - 1
    stack = []
    keep = set()

    stack.append((anchor, floater))
    while stack:
        anchor, floater = stack.pop()

        # инициализация отрезка
        if pts[floater] != pts[anchor]:
            anchorX = float(pts[floater][0] - pts[anchor][0])
            anchorY = float(pts[floater][1] - pts[anchor][1])
            seg_len = math.sqrt(anchorX ** 2 + anchorY ** 2)
            # get the unit vector
            anchorX /= seg_len
            anchorY /= seg_len
        else:
            anchorX = anchorY = seg_len = 0.0

        # внутренний цикл:
        max_dist = 0.0
        farthest = anchor + 1
        for i in range(anchor + 1, floater):
            dist_to_seg = 0.0
            # compare to anchor
            vecX = float(pts[i][0] - pts[anchor][0])
            vecY = float(pts[i][1] - pts[anchor][1])
            seg_len = math.sqrt(vecX ** 2 + vecY ** 2)
            # dot product:
            proj = vecX * anchorX + vecY * anchorY
            if proj < 0.0:
                dist_to_seg = seg_len
            else:
                # compare to floater
                vecX = float(pts[i][0] - pts[floater][0])
                vecY = float(pts[i][1] - pts[floater][1])
                seg_len = math.sqrt(vecX ** 2 + vecY ** 2)
                # dot product:
                proj = vecX * (-anchorX) + vecY * (-anchorY)
                if proj < 0.0:
                    dist_to_seg = seg_len
                else:  # расстояние от до прямой по теореме Пифагора:
                    dist_to_seg = math.sqrt(abs(seg_len ** 2 - proj ** 2))
                if max_dist < dist_to_seg:
                    max_dist = dist_to_seg
                    farthest = i

        if max_dist <= tolerance:  # использование отрезка
            keep.add(anchor)
            keep.add(floater)
        else:
            stack.append((anchor, farthest))
            stack.append((farthest, floater))

    keep = list(keep)
    keep.sort()
    return [pts[i] for i in keep]


def plot_result(img, bboxes, masks, polygons):
    """
    Draw in image masks of objects and centre of objects (red point) and classification object
    :param img:
    :param bboxes:
    :param masks:
    :param poly:
    :return:
    """
    img_predict = img.copy()

    poly_centres = []
    median_area = np.median([Polygon(poly).area for poly in polygons if poly.shape[0] > 2])

    all_mask_large = []
    all_mask_small = []
    for bbox, mask, poly in zip(bboxes, masks, polygons):
        count_points = poly.shape[0]
        if count_points <= 2:
            continue
        geom_poly = Polygon(poly)
        poly_centre = geom_poly.centroid
        poly_centres.append([poly_centre.x, poly_centre.y])
        if geom_poly.area < median_area*2/3:
            all_mask_small.append(mask)
        else:
            all_mask_large.append(mask)
    all_mask_large = np.stack(all_mask_large, axis=-1)
    all_mask_small = np.stack(all_mask_small, axis=-1)

    img_predict = draw_mask(img_predict, bw_mask=all_mask_large, chanel_color=2)
    img_predict = draw_mask(img_predict, bw_mask=all_mask_small, chanel_color=1)

    for poly_centre in poly_centres:
        img_predict = cv2.circle(img_predict, poly_centre, 10, [255, 0, 0], -1)

    for bbox in bboxes:
        xtl, ytl, xbr, ybr, conf = bbox
        img_predict = cv2.rectangle(img_predict, (int(xtl), int(ytl)), (int(xbr), int(ybr)), [255, 0, 0], 2)

    return img_predict


def draw_mask(img, bw_mask, opacity=0.5, chanel_color=2):
    union_mask = bw_mask * 255
    height, width = img.shape[:2]
    overlay = np.zeros((height, width, 3), dtype=np.uint8)
    overlay[:, :, chanel_color] = union_mask.copy()
    dst = cv2.addWeighted(img, 1, overlay, opacity, 0)
    return dst


def restore_predict(img_orig, img_resize, bboxes, masks):
    restore_boxes = []
    restore_masks = []
    height_orig, width_orig = img_orig.shape[:2]
    height_resize, width_resize = img_resize.shape[:2]
    scale_coef = height_orig/height_resize
    for bbox, mask in zip(bboxes[0], masks[0]):
        restore_boxes.append(np.append(bbox[:4] * scale_coef, bbox[4]))
        restore_masks.append(cv2.resize(mask*256, (height_orig, width_orig))//255)
    return restore_boxes, restore_masks

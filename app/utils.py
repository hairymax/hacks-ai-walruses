import cv2
import numpy as np
from shapely.geometry import Polygon, Point

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

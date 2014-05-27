"""
This code computes the distance between two line segments as
specified by their endpoints in 2D.

Modified from code posted at
http://stackoverflow.com/questions/2824478/shortest-distance-between-two-line-segments
"""
import math
import numpy as np

def segments_distance(x11, y11, x12, y12, x21, y21, x22, y22):
    """
    distance between two segments in the plane:
    one segment is (x11, y11) to (x12, y12)
    the other is   (x21, y21) to (x22, y22)
    """
    if segments_intersect(x11, y11, x12, y12, x21, y21, x22, y22):
        return 0
    # try each of the 4 vertices w/the other segment
    distances = np.empty(4)
    distances[0] = point_segment_distance(x11, y11, x21, y21, x22, y22)
    distances[1] = point_segment_distance(x12, y12, x21, y21, x22, y22)
    distances[2] = point_segment_distance(x21, y21, x11, y11, x12, y12)
    distances[3] = point_segment_distance(x22, y22, x11, y11, x12, y12)
    return np.min(np.abs(distances))

def segments_intersect(x11, y11, x12, y12, x21, y21, x22, y22):
    """
    whether two segments in the plane intersect:
    one segment is (x11, y11) to (x12, y12)
    the other is   (x21, y21) to (x22, y22)
    """
    dx1 = x12 - x11
    dy1 = y12 - y11
    dx2 = x22 - x21
    dy2 = y22 - y21
    delta = dx2 * dy1 - dy2 * dx1
    if delta == 0:
        return False  # parallel segments
    s = (dx1 * (y21 - y11) + dy1 * (x11 - x21)) / delta
    t = (dx2 * (y11 - y21) + dy2 * (x21 - x11)) / (-delta)
    return (0 <= s <= 1) and (0 <= t <= 1)



def point_segment_distance(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == dy == 0:  # the segment's just a point
        return math.hypot(px - x1, py - y1)

    # Calculate the t that minimizes the distance.
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)

    # See if this represents one of the segment's
    # end points or a point in the middle.
    if t < 0:
        dx = px - x1
        dy = py - y1
    elif t > 1:
        dx = px - x2
        dy = py - y2
    else:
        near_x = x1 + t * dx
        near_y = y1 + t * dy
        dx = px - near_x
        dy = py - near_y

    return math.hypot(dx, dy)

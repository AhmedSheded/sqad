import cv2 as cv
from poseModule import PoseDetector
import numpy as np
import math
import os

detector = PoseDetector()


def calculate_angle(point1, point2, point3):

    def vector_length(p1, p2):
        return math.sqrt((p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)

    def dot_product(v1, v2):
        return v1[0] * v2[0] + v1[1] * v2[1]

    vector1 = (point2[1] - point1[1], point2[2] - point1[2])
    vector2 = (point3[1] - point2[1], point3[2] - point2[2])

    length1 = vector_length(point1, point2)
    length2 = vector_length(point2, point3)

    if length1 == 0 or length2 == 0:
        raise ValueError("The length of at least one vector is zero.")

    dot_product_value = dot_product(vector1, vector2)
    cosine_angle = dot_product_value / (length1 * length2)

    # Ensure the value is within the valid range for arccosine
    cosine_angle = min(max(cosine_angle, -1.0), 1.0)

    # Calculate the angle in radians and convert to degrees
    angle_radians = math.acos(cosine_angle)
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

def draw_text_with_background(frame, text, position, font=cv.FONT_HERSHEY_SIMPLEX, font_scale=1, font_thickness=2, bg_color=(0, 0, 255), text_color=(255, 255, 255)):
    # Create a blank image to use as a mask
    mask = np.zeros_like(frame)

    # Get the size of the text box
    (text_width, text_height), baseline = cv.getTextSize(text, font, font_scale, font_thickness)

    # Calculate the position for the rectangle
    rect_x, rect_y = position
    rect_w = text_width + 10  # Add some padding
    rect_h = text_height + 10  # Add some padding

    # Draw the rectangle on the mask
    cv.rectangle(mask, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), bg_color, cv.FILLED)

    # Add the text on the mask
    cv.putText(mask, text, (rect_x + 5, rect_y + text_height + 5), font, font_scale, text_color, font_thickness, cv.LINE_AA)

    # Merge the mask with the original frame
    result = cv.addWeighted(frame, 1, mask, 0.5, 0)

    return result

class MovementState:
    Up = 0
    Down = 1

def process_video(video_path):
    def draw(point1, point2):
        x1, y1 = point1[1], point1[2]
        x2, y2 = point2[1], point2[2]
        cv.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 3)
        cv.circle(frame, (x2, y2), 5, (255, 255, 255), cv.FILLED)
        cv.circle(frame, (x1, y1), 5, (255, 255, 255), cv.FILLED)
        cv.circle(frame, (x1, y1), 10, (230, 230, 230), 5)
        cv.circle(frame, (x2, y2), 10, (230, 230, 230), 5)
    status = MovementState.Down
    counter = 0
    buffer_size = 10  # Adjust as needed
    angle_buffer = []

    cap = cv.VideoCapture(video_path)

    fourcc = cv.VideoWriter_fourcc(*'MP4V')
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    name = 'data/video' + str(len(os.listdir('data')) + 1) + '.mp4'
    writer = cv.VideoWriter(name, fourcc, 30, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = detector.estimate(frame, draw=False)
        points = detector.findPostions(frame, draw=False)

        if len(points) > 0:
            draw(points[15], points[13])
            draw(points[13], points[11])
            draw(points[11], points[23])
            draw(points[23], points[25])
            draw(points[25], points[27])
            draw(points[27], points[31])

        if len(points) > 0:
            p1_3 = [0, points[25][1], points[25][1] + 2]
            angle1 = calculate_angle(points[23], points[25], p1_3) - 9
            cv.putText(frame, str(int(angle1)) + "%", (points[25][1]+4, points[25][2]), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            p2_3 = [0, points[23][1], points[23][1] + 2]
            angle2 = 180 - calculate_angle(points[11], points[23], p2_3)
            cv.putText(frame, str(int(angle2)) + "%", (points[23][1]+4, points[23][2]), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            angle_buffer.append(angle1)  # Add the current angle to the buffer
            if len(angle_buffer) > buffer_size:
                angle_buffer.pop(0)  # Remove the oldest value if the buffer exceeds its size

            avg_angle = sum(angle_buffer) / len(angle_buffer)

            if status == MovementState.Down and avg_angle < 95:
                status = MovementState.Up
                counter += 1
            elif status == MovementState.Up and avg_angle > 100:
                status = MovementState.Down

            if angle2 < 11 and avg_angle < 100:
                frame = draw_text_with_background(frame, 'BEND FORWARD', (5, 45))
            if angle2 > 35:
                frame = draw_text_with_background(frame, 'BEND BACKWARD', (5, 45))
            if avg_angle < 85:
                frame = draw_text_with_background(frame, 'SQUAT TOO DEEP', (5, 85))
            if status == MovementState.Down and 95 < avg_angle < 140:
                frame = draw_text_with_background(frame, 'LOWER YOUR HIPS', (5, 85))

        frame=draw_text_with_background(frame, f'Counter {counter}', (5, 5), bg_color=(0, 255, 0))
        writer.write(frame)
        # cv.imshow('frame', frame)
        if cv.waitKey(1) == 27:
            break

    writer.release()
    cap.release()
    cv.destroyAllWindows()
    return name

process_video('data/d.mp4')

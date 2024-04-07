import cv2
import imutils
import socket
import numpy as np
import time
import base64
from ultralytics import YOLO

# Initialize YOLOv8 model
model = YOLO('yolov8n.pt')

# Define buffer size for UDP socket (adjust as needed)
BUFF_SIZE = 65536

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set socket buffer size to accommodate larger datagrams
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

# Get hostname and IP address
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)  # Use gethostbyname for dynamic IP

# Print the IP address used by the server
print(f"Server IP address: {host_ip}")

# Define port number for communication
port = 9999

# Bind the socket to the specified host and port
socket_address = (host_ip, port)
server_socket.bind(socket_address)

# Print confirmation message
print(f'Listening at: {socket_address}')

# Open video capture (0 for webcam, replace with video file path)
vid = cv2.VideoCapture(0)

# Variables for FPS calculation
fps, st, frames_to_count, cnt = (0, 0, 20, 0)

while True:
    try:
        # Receive message and client address from the connected client
        msg, client_addr = server_socket.recvfrom(BUFF_SIZE)
        print(f'Received connection from: {client_addr}')

        # Define video frame width for resizing
        WIDTH = 400

        while vid.isOpened():
            # Read a frame from the video capture
            ret, frame = vid.read()

            # Check if frame is successfully read
            if not ret:
                print("Error: Frame not read from video source.")
                # Implement error handling strategy (e.g., retry, exit)
                break

            # Resize the frame
            frame = imutils.resize(frame, width=WIDTH)

            # Detect objects using YOLOv8
            results = model.predict(frame, stream=True)
            for result in results:
                annotated_frame = result.plot()

                # Encode the frame and send it over UDP
                _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                message = base64.b64encode(buffer).decode()
                server_socket.sendto(message.encode(), client_addr)

                # Display FPS on the frame
                frame = cv2.putText(frame, f'FPS: {fps}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Display the frame for monitoring (optional)
                # cv2.imshow('TRANSMITTING VIDEO', frame)

                # Capture keyboard input (q to quit)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

                # Calculate FPS every 20 frames
                if cnt == frames_to_count:
                    try:
                        fps = round(frames_to_count / (time.time() - st))
                        st = time.time()
                        cnt = 0
                    except ZeroDivisionError:
                        pass  # Handle division by zero error (initial case)
                cnt += 1

    except KeyboardInterrupt:  # Capture keyboard interrupt for termination
        print("Exiting...")

    # Release resources even if exceptions occur
    finally:
        vid.release()
        # cv2.destroyAllWindows()  # Comment out if not displaying frame
        server_socket.close()

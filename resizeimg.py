import cv2
import numpy as np

# This will fail if the image path is incorrect. Make sure "resources/attendence.png" exists.
imgBackground = cv2.imread("images/5678.jpeg")

# Check if the image was loaded successfully
if imgBackground is None:
    print("Error: Could not read the image. Check the file path.")
else:
    while True:
        resized = cv2.resize(imgBackground, (260, 260))
        cv2.imshow("img", resized)
        
        # Corrected: Added a file extension (e.g., .png)
        cv2.imwrite("out.png", resized) 
        
        # Corrected: waitKey with a capital 'K'
        key = cv2.waitKey(1) 

        # Optional: Add a way to exit the loop
        if key == ord('q'):
            break

# Release resources
cv2.destroyAllWindows()
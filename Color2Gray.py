import cv2

# Load the color image
image_path = ''
color_image = cv2.imread(image_path)

# Convert the color image to grayscale
gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

# Optionally, save the grayscale image
cv2.imwrite('gray.png', gray_image)


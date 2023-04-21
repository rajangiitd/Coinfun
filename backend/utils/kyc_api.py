from backend.utils.image import convert_to_writable
from google.cloud import vision
import os

# Command to run in terminal if API doesn't work
# export  GOOGLE_APPLICATION_CREDENTIALS="/home/rajan/Desktop/COP290/Coinfun/backend/utils/strong-matrix-384420-f3e753c24872.json"

# write a function to know if the image has exactly 1 face
def is_single_face(image_content):
    try:
        """Returns True if the image has exactly 1 face."""
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_content)
        # Performs face detection on the image
        response = client.face_detection(image=image)
        faces = response.face_annotations

        # Returns True if only one face is detected
        return len(faces) == 1
    except Exception as e:
        raise e

# path = "/home/rajan/Desktop/COP290/Coinfun/dataset_creation/profile_pics"
# files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
# for file in files:
#     print(file, is_single_face(convert_to_writable(path + "/" + file)))

# Person5.jpg True
# Person8.jpg True
# Person9.jpg True
# Person18.jpeg True
# Person3.jpg True
# Person13.jpg True
# Person6.jpg True
# Person11.jpg True
# Person10.jpg True
# blank.jpg False
# Person19.jpg True
# Person12.jpg True
# Person14.jpg True
# Person2.jpg True
# Person20.jpg True
# Person16.jpg True
# Person1.jpg True
# Person15.jpg True
# Person7.jpg True
# Person4.jpg True
# Person17.jpg True

# path = "/home/rajan/Desktop/COP290/Coinfun/dataset_creation/payment_images"
# files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
# for file in files:
#     print(file, is_single_face(convert_to_writable(path + "/" + file)))

# images.jpeg False
# Mpeople2.jpg False
# Mpeople1.jpeg False
# blank_face.png False
# img.jpeg False
# download.png False
# Mpeople3.jpg False
# many_people.jpeg False



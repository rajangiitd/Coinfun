import pytest 
from backend.utils.image import convert_to_writable
from backend.utils.kyc_api import is_single_face
import os

def test_is_single_face_when_image_is_blank():
    script_directory = os.path.dirname(os.path.abspath(__file__)) # Define the path to the data directory relative to the script directory
    file_path = script_directory + '/' + 'blank.jpg'
    assert is_single_face(convert_to_writable(file_path)) == False
    
def test_is_single_face_when_image_is_NotBlank():
    script_directory = os.path.dirname(os.path.abspath(__file__)) # Define the path to the data directory relative to the script directory
    file_path = script_directory + '/' + 'trump.jpeg'
    assert is_single_face(convert_to_writable(file_path)) == True
    
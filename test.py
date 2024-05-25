from PIL import Image
import os

class ImageDisplay:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size

    def display(self):
        for y in range(0, self.height, 6):  # Adjust step size for height
            for x in range(0, self.width, 3):  # Adjust step size for width
                cropped_image = self.image.crop((x, y, x + 3, y + 6))  # Crop 3x6 region
                self.display_single_char(cropped_image)
            print()  # Newline after each row

    def display_single_char(self, cropped_image):
        # Resize the cropped image to 1x1 pixel and convert to grayscale
        resized_image = cropped_image.resize((1, 1)).convert('L')
        brightness = resized_image.getpixel((0, 0))

        # Set background color using ANSI escape code
        print(f"\033[48;5;{brightness}m ", end='', flush=True)
# Example usage:
img_str = ImageDisplay('C:\\Users\\12345\\Pictures\\dottest.png')
img_str.display()
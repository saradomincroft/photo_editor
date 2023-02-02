import os
import cv2
from PIL import Image
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox


# browse button to select image input folder
def browse_input_folder():
    root.after(1, open_input_folder)


# select image input folder
def open_input_folder():
    global input_folder_path
    input_folder_path = filedialog.askdirectory()
    input_folder_path = input_folder_path
    input_folder_label.config(text=input_folder_path)


# browse button to select image output folder
def browse_output_folder():
    root.after(1, open_output_folder)


def open_output_folder():
    global output_folder_path
    output_folder_path = filedialog.askdirectory()
    output_folder_path = output_folder_path
    output_folder_label.config(text=output_folder_path)


def run_script():
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    for file in os.listdir(input_folder_path):

        # Convert images so there's no black backgrounds etc, keep aspect ratio
        if file.endswith(('.png', '.jpg', '.bmp', '.jpeg', '.tif')):  # include all these types
            img = Image.open(os.path.join(input_folder_path, file))
            img = img.convert("RGBA")
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, img)

            # Open image and convert to RGB
            img = cv2.imread(os.path.join(input_folder_path, file))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Convert image to the HSV color space
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

            # Define the color range of shadows in the HSV color space
            lower_shadow = (0, 0, 0)
            upper_shadow = (180, 255, 240)

            # Create a mask for the shadows
            shadow_mask = cv2.inRange(hsv, lower_shadow, upper_shadow)

            # Define the color range of reflections in the HSV color space
            lower_reflection = (0, 0, 150)
            upper_reflection = (180, 50, 255)

            # Create a mask for the reflections
            reflection_mask = cv2.inRange(hsv, lower_reflection, upper_reflection)

            # Combine the two masks
            combined_mask = cv2.bitwise_or(shadow_mask, reflection_mask)

            # Invert the mask to select the non-shadow and non-reflection pixels
            no_shadow_or_reflection = cv2.bitwise_not(combined_mask)

            # Multiply the image with the no-shadow and no-reflection mask
            img = cv2.bitwise_and(img, img, mask=no_shadow_or_reflection)

            # fit image into 1200 x 1200 box
            width, height = background.size
            aspect_ratio = width / height
            new_width = 1200
            new_height = 1200
            if width > height:
                new_height = int(new_width / aspect_ratio)
            else:
                new_width = int(new_height * aspect_ratio)
            resized_img = background.resize((new_width, new_height))

            # create white background of 3000 x 2000
            final_img = Image.new("RGB", (3000, 2000), (255, 255, 255))

            # calculate position to paste resized_img in the center
            x_coord = (3000 - new_width) // 2
            y_coord = (2000 - new_height) // 2
            final_img.paste(resized_img, (x_coord, y_coord))

            final_img.save(os.path.join(output_folder_path, os.path.splitext(file)[0] + ".jpg"), optimize=True,
                           format='JPEG')
    print("All images have been resized and saved to the output folder.")
    messagebox.showinfo("Info", "All images have been resized and saved to the output folder.")


root = Tk()
root.title("Image Resizer")

Label(root, text="Select input folder:").grid(row=0, column=0)
input_folder_path = Entry(root)
input_folder_path.grid(row=0, column=1)

browse_input_button = Button(root, text="Browse", command=browse_input_folder)
browse_input_button.grid(row=0, column=2)
input_folder_label = Label(root, text="", bg="white", width=40, height=1)
input_folder_label.grid(row=0, column=1)

Label(root, text="Select output folder:").grid(row=1, column=0)
output_folder_path = Entry(root)
output_folder_path.grid(row=1, column=1)

browse_output_button = Button(root, text="Browse", command=browse_output_folder)
browse_output_button.grid(row=1, column=2)
output_folder_label = Label(root, text="", bg="white", width=40, height=1)
output_folder_label.grid(row=1, column=1)

run_button = Button(root, text="Run", command=run_script)
run_button.grid(row=2, column=1)

root.mainloop()

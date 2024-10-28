import tkinter as tk
from PIL import Image, ImageTk
import dicom2jpg
import pydicom
from tkinter import font
import os
import csv
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def dicom_to_png(dicom_dir, output_dir):
    # Check if output directory exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dicom_dir_list = os.listdir(dicom_dir)
    # Iterate over all files in the dicom directory
    for filename in dicom_dir_list:
        print(filename)
        if filename.endswith(".dcm"):
            # Load the dicom image
            ds = pydicom.dcmread(os.path.join(dicom_dir, filename))

            # Convert dicom image to numpy array
            img = ds.pixel_array

            # Normalize pixel array to use full uint8 range
            img = img / img.max() * 255

            # Convert to uint8
            img = img.astype('uint8')

            # Create PIL image
            im = Image.fromarray(img)

            # im = im.resize((1200, 500))

            # Save the image
            im.save(os.path.join(output_dir, filename.replace('.dcm', '.png')))
    return len(dicom_dir_list)
# Call the function
#dicom_to_png(dicom_dir, export_location)


def get_image_names(directory):
    # Use os.listdir to get the list of file names in the directory
    file_names = os.listdir(directory)

    file_name_locations = [directory + '/' + img for img in file_names]

    return file_names, file_name_locations

class ImageViewer:
    def __init__(self, window, dicom_to_png):
        self.window = window
        self.window.geometry("400x300")
        self.window.iconbitmap('icon.ico')
        self.dicom_folder = None
        self.image_window = None
        self.deid_filename = 'deidentification_output'
        self.image_folder = None
        self.photo_image = None
        self.deid_labels = {}
        self.image_names = None
        self.label = None
        self.image_files = []
        self.index = 0
        self.dicom_to_png = dicom_to_png

        self.window.iconbitmap('icon.ico')

        btn_font = font.Font(family="Arial Black", size=9)
        label_font = font.Font(family='Verdana', size = 8)
        
        # Create a frame to hold the buttons
        frame = tk.Frame(self.window, bg = 'black')
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        label_at_top = tk.Label(frame, text="Select an image folder, and a DICOM folder if conversion needed. \n Select the desired name of the de-identification output.", font = label_font)
        label_at_top.grid(row=0, column=0, pady=2)

        # Button to select image folder
        btn_select_image_folder = tk.Button(frame, text="Select Folder \n for Image Export", command=self.select_image_folder, height=2, width=20, 
                                            font=btn_font, bg = 'white')
        btn_select_image_folder.grid(row=2, column=0, pady=2)

        # Button to select DICOM folder
        btn_select_dicom_folder = tk.Button(frame, text="Select DICOM Folder", command=self.select_dicom_folder, height=2, width=20, font=btn_font, bg = 'white')
        btn_select_dicom_folder.grid(row=1, column=0, pady=2)

        # Button to convert DICOM to PNG
        btn_convert = tk.Button(frame, text="Convert DICOM to PNG", command=self.convert_images, height=2, width=20, font=btn_font, bg = 'white')
        btn_convert.grid(row=4, column=0, pady=2)

        # Proceed if no conversion required
        btn_proceed = tk.Button(frame, text="Proceed If No \nConversion Required", command=self.open_image_window, height=2, width=20, font=btn_font, bg = 'LightGreen')
        btn_proceed.grid(row=5, column=0, pady=2)

        deid_name_btn = tk.Button(frame, text="De-Id Output Name", command=self.open_new_window, height=2, width=20, font=btn_font, bg = 'white')
        deid_name_btn.grid(row=3, column=0, pady=2)        

        # self.label.pack()
    
    def next_image(self):
        self.index += 1
        if self.index == len(self.image_files):
            self.index = 0
        self.show_image()

    def prev_image(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.image_files) - 1
        self.show_image()

    def select_dicom_folder(self):
        self.dicom_folder = filedialog.askdirectory()
        if self.dicom_folder:
            print(f"DICOM folder selected: {self.dicom_folder}")

    def select_image_folder(self):
        self.image_folder = filedialog.askdirectory()
        if self.image_folder:
            print(f"Image folder selected: {self.image_folder}")
        
        self.image_names, self.image_files = get_image_names(self.image_folder)

    def image_labeller(self):
        image = self.image_names[self.index]

        self.deid_labels[image] = 'Contains PHI'


        # Open a CSV file in write mode
        with open(self.deid_filename + '.csv', 'w', newline='') as csv_file:
            # Create a CSV writer
            writer = csv.writer(csv_file)
            writer.writerow(['Filename', 'De-Identification Status', 'De-Identification Status Code'])
            # Write each key-value pair in the dictionary to the CSV file
            for key, value in self.deid_labels.items():
                if value == 'Contains PHI':
                    status_cd = 1
                else:
                    status_cd = 0
                
                writer.writerow([key, value, status_cd])
        

    def open_new_window(self):
        # Create a new window
        new_window = tk.Toplevel(self.window)

        # Create a Label
        label = tk.Label(new_window, text="Enter filename:")
        label.pack()

        # Create a text box
        text_box = tk.Entry(new_window)
        text_box.pack()

        # Function to get text box value
        def get_text_box_value():
            print("Filename: ", text_box.get())
            self.deid_filename = text_box.get()
            new_window.destroy()
        

        # Create a button that will print the text box value when clicked
        button = tk.Button(new_window, text="Submit", command=get_text_box_value)
        button.pack()

    def convert_images(self):
        if self.dicom_folder and self.image_folder:
            # dicom_files = [os.path.join(self.dicom_folder, file) for file in os.listdir(self.dicom_folder) if file.endswith('.dcm')]
            # for dicom_file in dicom_files:
            #     png_file = os.path.join(self.image_folder, os.path.splitext(os.path.basename(dicom_file))[0] + '.png')
    
            dicom_files = self.dicom_to_png(self.dicom_folder, self.image_folder)
            print(f"Converted {dicom_files} DICOM files to PNG")
            
            for image in self.image_names:
                self.deid_labels[image] = 'De-identified'

            self.open_image_window()

        else:
            print("Please select both DICOM and image folders")

    def open_image_window(self):
        self.window.destroy()
        self.image_window = tk.Tk()
        self.image_window.configure(bg='black')
        self.image_window.iconbitmap('icon.ico')
        self.image_window.title("MGH DICOM Image Viewer")
        self.image_window.geometry("1200x500")
        self.label = tk.Label(self.image_window, bg = 'white')
        self.show_image()

        top_frame = tk.Frame(self.image_window, bg = 'black')
        top_frame.pack(side='top', fill='x')

        bottom_frame = tk.Frame(self.image_window)
        bottom_frame.pack(side='bottom', fill='both', expand=True)

        btn_deid = tk.Button(top_frame, text="Contains PHI?", command=self.image_labeller, height=2, width=10, bg = 'FireBrick', fg = 'white')
        btn_deid.pack(side='top', pady=10)

        # btn_exit = tk.Button(top_frame, text="EXIT", command=self.image_window.destroy, height=2, width=10)
        # btn_exit.pack(side='left', padx=10)

        btn_prev = tk.Button(bottom_frame, text="← Previous", command=self.prev_image, height=2, width=10)
        btn_prev.pack(side='left', padx=10)

        btn_next = tk.Button(bottom_frame, text="Next →", command=self.next_image, height=2, width=10)
        btn_next.pack(side='right', padx=10)

        self.label.pack()



        # self.label.pack()


    def show_image(self):
        
        # Load an image using PIL
        image = Image.open(self.image_files[self.index])

        # Resize the image to fit the window
        max_size = (1200, 500)  # replace with the size of your window
        image.thumbnail(max_size)

        # Convert the Image object to a PhotoImage object
        self.photo_image = ImageTk.PhotoImage(image)

        # Update the label with the new PhotoImage object
        self.label.config(image=self.photo_image)

def main():
    window = tk.Tk()
    window.title("DICOM Image Viewer")

    ImageViewer(window, dicom_to_png)

    window.mainloop()

if __name__ == "__main__":
    main()

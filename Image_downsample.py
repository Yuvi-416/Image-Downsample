# Code to down sample series of dicom and tif image using Pydicom and rasterio library

import os
import pydicom
import rasterio
from rasterio.enums import Resampling
import tkinter as tk
from tkinter import filedialog
from tkinter import Tk, simpledialog

# Pass the path to the input and output directory
root = tk.Tk()
root.withdraw()

Input_file_path = filedialog.askdirectory(title="Please select the input image")
Output_file_path = filedialog.askdirectory(title="Please select the folder to save the file")
rescale_factor_selector = simpledialog.askinteger(title="askinteger", prompt="integerInputPlease")
print(rescale_factor_selector)

# Sort image files based on the filename
names = os.listdir(Input_file_path)
names = sorted(names, key=lambda i: int(os.path.splitext(os.path.basename(i))[0]))

for file_name in names:
    if file_name.endswith(".dcm"):
        filename, file_extension = os.path.splitext(file_name)

        # Read the dicom file using Pydicom library
        ds = pydicom.dcmread(Input_file_path + "/" + file_name, force=True)
        Columns, Rows = ds.Columns, ds.Rows
        image_data = ds.pixel_array

        # Down-sample factor
        Rescale_factor = int(rescale_factor_selector)
        data_down_sampling = image_data[::Rescale_factor, ::Rescale_factor]

        # Copy the data back to the original data set
        ds.PixelData = data_down_sampling.tobytes()

        # Update the information regarding the shape of the data array
        ds.Rows, ds.Columns = data_down_sampling.shape

        down_sampled_data = ds.pixel_array
        down_sampled_Columns, down_sampled_Rows = ds.Columns, ds.Rows

        # Save image back to dicom
        dicom_filename = str(Output_file_path) + "/" + str(filename) + ".dcm"
        ds.save_as(filename=dicom_filename, write_like_original=False)

    elif file_name.endswith(".tif"):
        filename, file_extension = os.path.splitext(file_name)

        with rasterio.Env():

            # Read the tif file using Rasterio library
            with rasterio.open(Input_file_path + "/" + file_name) as data:

                # Down-sample factor
                Rescale_factor = int(rescale_factor_selector)

                # Get new rows and column by dividing rescale factor
                downSample = data.read(1, out_shape=(int(data.height / Rescale_factor), int(data.width / Rescale_factor)), resampling=Resampling.bilinear)

                # Downscale image transform
                transform = data.transform * data.transform.scale((data.height / downSample.shape[0]), (data.width / downSample.shape[1]))

                # Update the image profile
                profile = data.profile
                profile.update(transform=transform, width=downSample.shape[1], height=downSample.shape[0])

            # Save image back to tif
            with rasterio.open(str(Output_file_path) + "/" + str(filename) + '.tif', 'w', **profile) as data:
                data.write(downSample, 1)

    else:
        print("File extension doesn't match the requirement. Please select the required file")

root.destroy()
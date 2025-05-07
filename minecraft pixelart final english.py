from PIL import Image, ImageTk  # Import libraries for image processing and displaying images in Tkinter
import tkinter as tk  # Import Tkinter for GUI creation
from tkinter import filedialog, messagebox, colorchooser  # Import file dialog, message box, and color chooser
import os  # Import OS-related functions (path handling, etc.)
import numpy as np  # Import NumPy for array and numerical calculations
from scipy.spatial import KDTree  # Import KDTree data structure for color nearest neighbor search
import mcschematic  # Import library for creating Minecraft schematic files
try:
    import picamera  # Raspberry Pi camera control library
except ImportError:
    class MockPiCamera:
        def __init__(self):
            pass
        def start_preview(self):
            pass
        def stop_preview(self):
            pass
        def capture(self, output):
            with open(output, 'wb') as f:
                f.write(b"Mock image data")
        def close(self):
            pass
    picamera = MockPiCamera
import time  # For time delay
import tempfile  # For creating temporary files

# Minecraft basic color palette (list of RGB tuples)
base_colors = [
    (9999, 9999, 9999), (127, 178, 56), (247, 233, 163), (199, 199, 199), (255, 0, 0),
    (160, 160, 255), (167, 167, 167), (0, 124, 0), (255, 255, 255), (164, 168, 184),
    (151, 109, 77), (112, 112, 112), (64, 64, 255), (143, 119, 72), (255, 252, 245),
    (216, 127, 51), (178, 76, 216), (102, 153, 216), (229, 229, 51), (127, 204, 25),
    (242, 127, 165), (76, 76, 76), (153, 153, 153), (76, 127, 153), (127, 63, 178),
    (51, 76, 178), (102, 76, 51), (102, 127, 51), (153, 51, 51), (25, 25, 25),
    (250, 238, 77), (92, 219, 213), (74, 128, 255), (0, 217, 58), (129, 86, 49),
    (112, 2, 0), (209, 177, 161), (159, 82, 36), (149, 87, 108), (112, 108, 138),
    (186, 133, 36), (103, 117, 53), (160, 77, 78), (57, 41, 35), (135, 107, 98),
    (87, 92, 92), (122, 73, 88), (76, 62, 92), (76, 50, 35), (76, 82, 42),
    (142, 60, 46), (37, 22, 16), (189, 48, 49), (148, 63, 97), (92, 25, 29),
    (22, 126, 134), (58, 142, 140), (86, 44, 62), (20, 180, 133), (100, 100, 100),
    (216, 175, 147), (127, 167, 150),
    (255, 182, 193),  # Light Pink
    (255, 192, 203),  # Pink
    (255, 209, 220),  # Baby Pink
    (255, 223, 229)   # Pale Pink
]

# Extended color palette (includes shading and more colors)
extended_colors = [(9999, 9999, 9999)]*4 + [
    (89, 125, 39), (109, 153, 48), (127, 178, 56), (67, 94, 29), (174, 164, 115),
    (213, 201, 140), (247, 233, 163), (130, 123, 86), (140, 140, 140), (171, 171, 171),
    (199, 199, 199), (105, 105, 105), (180, 0, 0), (220, 0, 0), (255, 0, 0), (135, 0, 0),
    (112, 112, 180), (138, 138, 220), (160, 160, 255), (84, 84, 135), (117, 117, 117),
    (144, 144, 144), (167, 167, 167), (88, 88, 88), (0, 87, 0), (0, 106, 0), (0, 124, 0),
    (0, 65, 0), (180, 180, 180), (220, 220, 220), (255, 255, 255), (135, 135, 135),
    (115, 118, 129), (141, 144, 158), (164, 168, 184), (86, 88, 97), (106, 76, 54),
    (130, 94, 66), (151, 109, 77), (79, 57, 40), (79, 79, 79), (96, 96, 96), (112, 112, 112),
    (59, 59, 59), (45, 45, 180), (55, 55, 220), (64, 64, 255), (33, 33, 135), (100, 84, 50),
    (123, 102, 62), (143, 119, 72), (75, 63, 38), (180, 177, 172), (220, 217, 211),
    (255, 252, 245), (135, 133, 129), (152, 89, 36), (186, 109, 44), (216, 127, 51),
    (114, 67, 27), (125, 53, 152), (153, 65, 186), (178, 76, 216), (94, 40, 114),
    (72, 108, 152), (88, 132, 186), (102, 153, 216), (54, 81, 114), (161, 161, 36),
    (197, 197, 44), (229, 229, 51), (121, 121, 27), (89, 144, 17), (109, 176, 21),
    (127, 204, 25), (67, 108, 13), (170, 89, 116), (208, 109, 142), (242, 127, 165),
    (128, 67, 87), (53, 53, 53), (65, 65, 65), (76, 76, 76), (40, 40, 40), (108, 108, 108),
    (132, 132, 132), (153, 153, 153), (81, 81, 81), (53, 89, 108), (65, 109, 132),
    (76, 127, 153), (40, 67, 81), (89, 44, 125), (109, 54, 153), (127, 63, 178), (67, 33, 94),
    (36, 53, 125), (44, 65, 153), (51, 76, 178), (27, 40, 94), (72, 53, 36), (88, 65, 44),
    (102, 76, 51), (54, 40, 27), (72, 89, 36), (88, 109, 44), (102, 127, 51), (54, 67, 27),
    (108, 36, 36), (132, 44, 44), (153, 51, 51), (81, 27, 27), (17, 17, 17), (21, 21, 21),
    (25, 25, 25), (13, 13, 13), (176, 168, 54), (215, 205, 66), (250, 238, 77), (132, 126, 40),
    (64, 154, 150), (79, 188, 183), (92, 219, 213), (48, 115, 112), (52, 90, 180),
    (63, 110, 220), (74, 128, 255), (39, 67, 135), (0, 153, 40), (0, 187, 50), (0, 217, 58),
    (0, 114, 30), (91, 60, 34), (111, 74, 42), (129, 86, 49), (68, 45, 25), (79, 1, 0),
    (96, 1, 0), (112, 2, 0), (59, 1, 0), (147, 124, 113), (180, 152, 138), (209, 177, 161),
    (110, 93, 85), (112, 57, 25), (137, 70, 31), (159, 82, 36), (84, 43, 19), (105, 61, 76),
    (128, 75, 93), (149, 87, 108), (78, 46, 57), (79, 76, 97), (96, 93, 119), (112, 108, 138),
    (59, 57, 73), (131, 93, 25), (160, 114, 31), (186, 133, 36), (98, 70, 19), (72, 82, 37),
    (88, 100, 45), (103, 117, 53), (54, 61, 28), (112, 54, 55), (138, 66, 67), (160, 77, 78),
    (84, 40, 41), (40, 28, 24), (49, 35, 30), (57, 41, 35), (30, 21, 18), (95, 75, 69),
    (116, 92, 84), (135, 107, 98), (71, 56, 51), (61, 64, 64), (75, 79, 79), (87, 92, 92),
    (46, 48, 48), (86, 51, 62), (105, 62, 75), (122, 73, 88), (64, 38, 46), (53, 43, 64),
    (65, 53, 79), (76, 62, 92), (40, 32, 48), (53, 35, 24), (65, 43, 30), (76, 50, 35),
    (40, 26, 18), (53, 57, 29), (65, 70, 36), (76, 82, 42), (40, 43, 22), (100, 42, 32),
    (122, 51, 39), (142, 60, 46), (75, 31, 24), (26, 15, 11), (31, 18, 13), (37, 22, 16),
    (19, 11, 8), (133, 33, 34), (163, 41, 42), (189, 48, 49), (100, 25, 25), (104, 44, 68),
    (127, 54, 83), (148, 63, 97), (78, 33, 51), (64, 17, 20), (79, 21, 25), (92, 25, 29),
    (48, 13, 15), (15, 88, 94), (18, 108, 115), (22, 126, 134), (11, 66, 70), (40, 100, 98),
    (50, 122, 120), (58, 142, 140), (30, 75, 74), (60, 31, 43), (74, 37, 53), (86, 44, 62),
    (45, 23, 32), (14, 127, 93), (17, 155, 114), (20, 180, 133), (10, 95, 70), (70, 70, 70),
    (86, 86, 86), (100, 100, 100), (52, 52, 52), (152, 123, 103), (186, 150, 126),
    (216, 175, 147), (114, 92, 77), (89, 117, 105), (109, 144, 129), (127, 167, 150),
    (67, 88, 79),
    (255, 182, 193),  # Light Pink
    (255, 192, 203),  # Pink
    (255, 209, 220),  # Baby Pink
    (255, 223, 229)   # Pale Pink
]

# Function mapping block indices to Minecraft block ID strings
def get_block_mapping():
    return {
        0: "minecraft:air",  # Air block
        1: "minecraft:grass_block",  # Grass block
        2: "minecraft:sand",  # Sand block
        3: "minecraft:white_wool",  # White wool
        4: "minecraft:tnt",  # TNT block
        5: "minecraft:ice",  # Ice block
        6: "minecraft:iron_block",  # Iron block
        7: "minecraft:oak_leaves",  # Oak leaves
        8: "minecraft:snow_block",  # Snow block
        9: "minecraft:clay",  # Clay block
        10: "minecraft:dirt",  # Dirt block
        11: "minecraft:stone",  # Stone block
        12: "minecraft:water",  # Water block
        13: "minecraft:oak_planks",  # Oak planks
        14: "minecraft:quartz_block",  # Quartz block
        15: "minecraft:orange_terracotta",  # Orange terracotta
        16: "minecraft:magenta_wool",  # Magenta wool
        17: "minecraft:light_blue_wool",  # Light blue wool
        18: "minecraft:yellow_wool",  # Yellow wool
        19: "minecraft:lime_wool",  # Lime wool
        20: "minecraft:pink_wool",  # Pink wool
        21: "minecraft:gray_wool",  # Gray wool
        22: "minecraft:light_gray_wool",  # Light gray wool
        23: "minecraft:cyan_wool",  # Cyan wool
        24: "minecraft:purple_wool",  # Purple wool
        25: "minecraft:blue_wool",  # Blue wool
        26: "minecraft:brown_wool",  # Brown wool
        27: "minecraft:green_wool",  # Green wool
        28: "minecraft:red_wool",  # Red wool
        29: "minecraft:black_wool",  # Black wool
        30: "minecraft:gold_block",  # Gold block
        31: "minecraft:diamond_block",  # Diamond block
        32: "minecraft:lapis_block",  # Lapis lazuli block
        33: "minecraft:emerald_block",  # Emerald block
        34: "minecraft:podzol",  # Podzol block
        35: "minecraft:netherrack",  # Netherrack
        36: "minecraft:white_terracotta",  # White terracotta
        37: "minecraft:orange_terracotta",  # Orange terracotta
        38: "minecraft:magenta_terracotta",  # Magenta terracotta
        39: "minecraft:light_blue_terracotta",  # Light blue terracotta
        40: "minecraft:yellow_terracotta",  # Yellow terracotta
        41: "minecraft:lime_terracotta",  # Lime terracotta
        42: "minecraft:pink_terracotta",  # Pink terracotta
        43: "minecraft:gray_terracotta",  # Gray terracotta
        44: "minecraft:light_gray_terracotta",  # Light gray terracotta
        45: "minecraft:cyan_terracotta",  # Cyan terracotta
        46: "minecraft:purple_terracotta",  # Purple terracotta
        47: "minecraft:blue_terracotta",  # Blue terracotta
        48: "minecraft:brown_terracotta",  # Brown terracotta
        49: "minecraft:green_terracotta",  # Green terracotta
        50: "minecraft:red_terracotta",  # Red terracotta
        51: "minecraft:black_terracotta",  # Black terracotta
        52: "minecraft:crimson_nylium",  # Crimson nylium
        53: "minecraft:crimson_stem",  # Crimson stem
        54: "minecraft:crimson_hyphae",  # Crimson hyphae
        55: "minecraft:warped_nylium",  # Warped nylium
        56: "minecraft:warped_stem",  # Warped stem
        57: "minecraft:warped_hyphae",  # Warped hyphae
        58: "minecraft:warped_wart_block",  # Warped wart block
        59: "minecraft:deepslate",  # Deepslate
        60: "minecraft:raw_iron_block",  # Raw iron block
        61: "minecraft:glow_lichen",  # Glow lichen
        62: "minecraft:pink_concrete",  # Light pink - pink concrete
        63: "minecraft:pink_concrete",  # Pink - pink concrete
        64: "minecraft:pink_concrete",  # Baby pink - pink concrete
        65: "minecraft:pink_concrete",  # Pale pink - pink concrete
    }

# Function to create a Minecraft schematic file (.litematic) from a color index matrix
def create_schematic_from_idx_matrix(idx_matrix, output_path, schem_name):
    height = len(idx_matrix)  # Matrix height (image height)
    width = len(idx_matrix[0]) if height > 0 else 0  # Matrix width (image width)

    schem = mcschematic.MCSchematic()  # Create new schematic object
    block_mapping = get_block_mapping()  # Get block index to ID mapping dictionary

    for y in range(height):  # Iterate over rows
        for x in range(width):  # Iterate over columns
            idx = idx_matrix[y][x]  # Current color index
            if idx in block_mapping:  # If block mapping exists
                block_id = block_mapping[idx]  # Get block ID
                schem.setBlock((x, 0, y), block_id)  # Place block in schematic (y=0 layer)

    output_dir = os.path.dirname(output_path)  # Output directory path
    schem.save(  # Save schematic file
        output_dir,
        schem_name,
        mcschematic.Version.JE_1_12_1  # Minecraft version 1.12.1 format
    )
    return os.path.join(output_dir, f"{schem_name}.litematic")  # Return saved file path

# GUI application class definition
class App:
    def __init__(self, root):
        self.root = root  # Store root window
        self.file_path = ''  # Initialize selected image file path

        # Create and pack file upload frame
        self.frame = tk.LabelFrame(self.root, padx=10, pady=10)
        self.frame.pack(padx=10, pady=10, fill="x")

        # Create file selection button and bind to upload_file function
        self.file_btn = tk.Button(self.frame, text="Browse File...", command=self.upload_file)
        self.file_btn.pack(side="left")

        # Create camera capture button and bind to capture_from_camera function
        self.capture_btn = tk.Button(self.frame, text="Capture from Camera", command=self.capture_from_camera)
        self.capture_btn.pack(side="left", padx=10)

        # Create label to show selected file name
        self.file_label = tk.Label(self.frame, text="")
        self.file_label.pack(side="left", padx=10)

        # Create image preview label (initially shows 'No image selected')
        self.preview_image_label = tk.Label(self.frame, text="No image selected")
        self.preview_image_label.pack(side="left", padx=10)

        # Initialize variables to store original image size
        self.width = 0
        self.height = 1

        # Create StringVar variables to hold resolution input values
        self.var_res_width = tk.StringVar()
        self.var_res_height = tk.StringVar()

        # Create resolution input frame
        self.resolution_frame = tk.Frame(root)

        # Create and pack resolution label
        self.resolution_label = tk.Label(self.resolution_frame, text="Resolution", font=("Arial", 13))
        self.resolution_label.pack(fill='both')

        # Create and pack width entry
        self.resolution_w_entry = tk.Entry(self.resolution_frame, textvariable=self.var_res_width,
                                           width=6, font=("Arial", 13), justify='right')
        self.resolution_w_entry.pack(side='left')

        # Create and pack multiplication sign label
        self.resolution_x = tk.Label(self.resolution_frame, text="×", font=("Arial", 13))
        self.resolution_x.pack(side='left')

        # Create and pack height entry
        self.resolution_h_entry = tk.Entry(self.resolution_frame, textvariable=self.var_res_height,
                                           width=6, font=("Arial", 13), justify='right')
        self.resolution_h_entry.pack(side='left')

        # Bind focus out and Enter key events for width and height entries to update functions
        self.resolution_w_entry.bind("<FocusOut>", self.update_height)
        self.resolution_w_entry.bind("<Return>", self.unfocus)
        self.resolution_h_entry.bind("<FocusOut>", self.update_width)
        self.resolution_h_entry.bind("<Return>", self.unfocus)

        # Pack resolution frame
        self.resolution_frame.pack(pady=10)

        # Create and pack options frame
        option_frame = tk.Frame(root)
        option_frame.pack(pady=10, anchor="w", padx=20)

        # Create and pack options label
        tk.Label(option_frame, text="Options").pack(anchor='w')

        # Create BooleanVars for options and set default values
        self.var_maintain_aspect_ratio = tk.BooleanVar(value=True)  # Maintain aspect ratio
        self.var_crop = tk.BooleanVar()  # Crop if aspect ratio differs
        self.var_transparent_fill = tk.BooleanVar()  # Fill transparent pixels with color
        self.selected_color = "#ffffff"  # Default fill color for transparent pixels (white)
        self.var_shade = tk.BooleanVar()  # Include shading

        # Create and pack maintain aspect ratio checkbox with command binding
        self.cb0 = tk.Checkbutton(option_frame, text="Maintain Aspect Ratio",
                                  variable=self.var_maintain_aspect_ratio,
                                  command=self.cb0_update_state)
        self.cb0.pack(anchor='w')

        # Create and pack crop checkbox, initially disabled
        self.cb1 = tk.Checkbutton(option_frame, state='disabled',
                                  text="Crop if aspect ratio differs",
                                  variable=self.var_crop)
        self.cb1.pack(anchor='w')

        # Create frame for transparent fill option and color picker button
        self.cb2_frame = tk.Frame(option_frame)

        # Create and pack transparent fill checkbox with command binding
        self.cb2 = tk.Checkbutton(self.cb2_frame, text="Fill transparent pixels with color",
                                  variable=self.var_transparent_fill,
                                  command=self.cb2_update_state)
        self.cb2.pack(anchor='w', side='left')

        # Create and pack color picker button, initially disabled
        self.color_picker = tk.Button(self.cb2_frame, state='disabled',
                                      text="Choose Color...", bg=self.selected_color,
                                      command=self.choose_color)
        self.color_picker.pack(anchor='w', side='left')
        self.cb2_frame.pack()

        # Create and pack shading checkbox
        self.cb3 = tk.Checkbutton(option_frame, text="Include Shading",
                                  variable=self.var_shade)
        self.cb3.pack(anchor='w')

        # Create and pack GO button to start processing
        go_btn = tk.Button(root, text="GO", font=("Arial", 16, "bold"),
                           command=self.go_action)
        go_btn.pack(pady=10)

    # Remove focus from entry widget on Enter key press
    def unfocus(self, event):
        event.widget.master.focus_set()

    # Update height entry based on width input to maintain aspect ratio
    def update_height(self, *args):
        if self.var_maintain_aspect_ratio.get():
            aspect_ratio = self.width / self.height  # Original image aspect ratio
            try:
                width = float(self.var_res_width.get())  # Input width
                height = int(round(width / aspect_ratio, 0))  # Calculate height maintaining ratio
                self.var_res_height.set(f"{height}")  # Update height entry
            except ValueError:
                pass  # Ignore invalid input

    # Update width entry based on height input to maintain aspect ratio
    def update_width(self, *args):
        if self.var_maintain_aspect_ratio.get():
            aspect_ratio = self.width / self.height
            try:
                height = float(self.var_res_height.get())
                width = int(round(height * aspect_ratio, 0))
                self.var_res_width.set(f"{width}")
            except ValueError:
                pass

    # Enable or disable crop option based on maintain aspect ratio checkbox
    def cb0_update_state(self):
        if self.var_maintain_aspect_ratio.get():
            self.var_crop.set(False)  # Disable crop if maintaining aspect ratio
            self.cb1.config(state='disabled')  # Disable crop checkbox
            self.update_height()  # Update height accordingly
        else:
            self.cb1.config(state='normal')  # Enable crop checkbox

    # Enable or disable color picker based on transparent fill checkbox
    def cb2_update_state(self):
        if self.var_transparent_fill.get():
            self.color_picker.config(state='normal')  # Enable color picker
        else:
            self.color_picker.config(state='disabled')  # Disable color picker

    # Open color chooser dialog and update selected color and button appearance
    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Color")
        if color_code[1]:
            self.selected_color = color_code[1]  # Selected color in hex
            hex_color = self.selected_color.lstrip('#')
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]  # Extract RGB
            brightness = (r*299 + g*587 + b*114) / 1000  # Calculate brightness
            # Set text color to white or black depending on brightness
            self.color_picker.config(fg='white' if brightness < 128 else 'black',
                                    bg=self.selected_color)

    # Open file dialog to select image file, then load and preview it
    def upload_file(self):
        self.file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All Files", "*.*")]
        )
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))  # Show file name
            img = Image.open(self.file_path)  # Open image
            self.width, self.height = img.size  # Store original size
            # Resize preview image to max 50 pixels
            preview_size = (
                int(self.width / max(self.width, self.height) * 50),
                int(self.height / max(self.width, self.height) * 50)
            )
            img = img.resize(preview_size, Image.Resampling.LANCZOS)  # High-quality resize
            img_tk = ImageTk.PhotoImage(img)  # Convert for Tkinter
            # Set resolution entries to original image size
            self.resolution_w_entry.delete(0, tk.END)
            self.resolution_w_entry.insert(0, self.width)
            self.resolution_h_entry.delete(0, tk.END)
            self.resolution_h_entry.insert(0, self.height)
            # Show preview image
            self.preview_image_label.config(text='', image=img_tk)
            self.preview_image_label.image = img_tk  # Keep reference

    # Capture photo from Raspberry Pi camera and load it into GUI
    def capture_from_camera(self):
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                temp_filename = tmpfile.name

            camera = picamera.PiCamera()
            camera.resolution = (1024, 768)  # Adjust resolution if needed
            camera.start_preview()
            time.sleep(2)  # Camera warm-up time
            camera.capture(temp_filename)
            camera.stop_preview()
            camera.close()

            # Load captured image into GUI
            self.file_path = temp_filename
            self.file_label.config(text=os.path.basename(self.file_path))
            img = Image.open(self.file_path)
            self.width, self.height = img.size

            # Resize preview image to max 50 pixels
            preview_size = (
                int(self.width / max(self.width, self.height) * 50),
                int(self.height / max(self.width, self.height) * 50)
            )
            img = img.resize(preview_size, Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            # Set resolution entries to original image size
            self.resolution_w_entry.delete(0, tk.END)
            self.resolution_w_entry.insert(0, self.width)
            self.resolution_h_entry.delete(0, tk.END)
            self.resolution_h_entry.insert(0, self.height)

            # Show preview image
            self.preview_image_label.config(text='', image=img_tk)
            self.preview_image_label.image = img_tk

        except Exception as e:
            messagebox.showerror("Error", f"Error capturing photo from camera: {str(e)}")

    # Main processing function triggered by GO button
    def go_action(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select or capture an image file first.")
            return

        file_name, file_ext = os.path.splitext(os.path.basename(self.file_path))  # Split filename and extension
        try:
            w = int(self.var_res_width.get())  # Input width
            h = int(self.var_res_height.get())  # Input height
        except ValueError:
            messagebox.showerror("Error", "Please enter valid resolution values.")
            return

        # Ask user where to save the PNG output file
        output_file_path = filedialog.asksaveasfilename(
            initialfile=f"{file_name}_{w}x{h}_minecraftmap{'_noshade' if not self.var_shade.get() else ''}.png",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All Files", "*.*")],
            title="Select location to save converted image"
        )
        if not output_file_path:
            return  # User cancelled save dialog

        # Schematic file saved in same folder as PNG with related name
        output_folder = os.path.dirname(output_file_path)
        schematic_name = f"{file_name}_{w}x{h}_pixelart"

        try:
            img = Image.open(self.file_path)  # Open original image
            if img.mode != 'RGBA':
                img = img.convert('RGBA')  # Convert to RGBA for transparency handling

            # Resize image with aspect ratio and cropping options
            if self.var_crop.get():
                width_ratio = w / self.width
                height_ratio = h / self.height
                aspect_ratio = self.width / self.height
                if width_ratio > height_ratio:
                    temp_h = int(round(w / aspect_ratio))
                    img_resized = img.resize((w, temp_h), Image.Resampling.NEAREST)
                    top = (temp_h - h) // 2
                    img_resized = img_resized.crop((0, top, w, top + h))  # Crop vertically centered
                else:
                    temp_w = int(round(h * aspect_ratio))
                    img_resized = img.resize((temp_w, h), Image.Resampling.NEAREST)
                    left = (temp_w - w) // 2
                    img_resized = img_resized.crop((left, 0, left + w, h))  # Crop horizontally centered
            else:
                img_resized = img.resize((w, h), Image.Resampling.NEAREST)  # Simple resize

            # Fill transparent pixels with selected color if option enabled
            if self.var_transparent_fill.get():
                background = Image.new('RGBA', (w, h), self.selected_color)  # Create background color
                img_resized = Image.alpha_composite(background, img_resized)  # Alpha composite

            # Convert image pixels to Minecraft palette color indices
            rgba_pixels = list(img_resized.getdata())  # Pixel data list
            palette = extended_colors if self.var_shade.get() else base_colors  # Choose palette
            tree = KDTree(np.array(palette))  # Create KDTree for palette colors

            idx_array = []
            for r, g, b, a in rgba_pixels:
                if a == 0:  # Fully transparent pixel is index 0 (air)
                    idx_array.append(0)
                else:
                    _, idx = tree.query((r, g, b))  # Find nearest palette color index
                    idx_array.append(int(idx))

            # Convert 1D index array to 2D matrix based on image size
            idx_matrix = [idx_array[i*w:(i+1)*w] for i in range(h)]

            # Create output RGBA image from palette indices and save PNG
            rgba_image = np.zeros((h, w, 4), dtype=np.uint8)  # Initialize RGBA array
            mask = np.array(idx_matrix) != 0  # Mask to exclude air blocks
            rgba_image[mask, :3] = np.array(palette)[np.array(idx_matrix)[mask]]  # Apply palette colors
            rgba_image[mask, 3] = 255  # Set opacity
            Image.fromarray(rgba_image, 'RGBA').save(output_file_path)  # Save PNG

            # Create Minecraft schematic file
            schematic_path = create_schematic_from_idx_matrix(
                idx_matrix,
                output_file_path,
                schematic_name
            )

            # Show success message with output paths
            messagebox.showinfo("Success",
                                f"Conversion complete!\n"
                                f"Image: {os.path.abspath(output_file_path)}\n"
                                f"Schematic: {os.path.abspath(schematic_path)}"
                                )

        except Exception as e:
            messagebox.showerror("Error", f"Error during processing: {str(e)}")


# Program entry point - run GUI
if __name__ == "__main__":
    root = tk.Tk()  # Create Tkinter root window
    root.title("Minecraft Pixel Art Converter")  # Set window title
    root.geometry("500x600")  # Set window size
    root.bind_all("<Button-1>", lambda event: event.widget.focus_set())  # Set focus on click
    app = App(root)  # Create App instance and initialize GUI
    root.mainloop()  # Start event loop

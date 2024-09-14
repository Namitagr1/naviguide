import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


def detect_cones(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image at path '{image_path}' could not be loaded.")

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    rgb_color = (254, 52, 16)  # Note that rgb must be updated according to use case (color of obstacles being used)
    hsv_color = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2HSV)[0][0]
    lower_bound = np.array([hsv_color[0] - 10, 100, 100])
    upper_bound = np.array([hsv_color[0] + 10, 255, 255])
    color_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    contours, _ = cv2.findContours(color_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cone_positions = []
    dot_coordinates = []

    for contour in contours:  # Note that this code is specifically for use of cones and images taken from specific distances
        if 1500 < cv2.contourArea(contour) < 30000:
            x, y, w, h = cv2.boundingRect(contour)
            cone_positions.append((x + w / 2, y + h / 2))
            dot_coordinates.append((x + w / 2, y + h * 0.9))
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(image, (int(x + w / 2), int(y + h * 0.9)), 3, (255, 0, 0), -1)

    return cone_positions, dot_coordinates, image


def print_directions():
    if len(instructions) == 0:
        directions_label.config(text="Path Complete")
    else:
        directions_label.config(text=instructions[0])
        instructions.pop(0)


def handle_login():
    global additional_points, instructions, combined_cone_positions
    user = username_entry.get()
    pw = password_entry.get()
    if user != "trial":
        messagebox.showerror("Error", "Invalid login.")
        return
    if pw != "1234":
        messagebox.showerror("Error", "Invalid login.")
        return

    show_main_page()


def show_main_page():
    login_frame.pack_forget()
    main_frame.pack(pady=20)


def generate_path(grid, start, end, grid_resolution):
    path = [start]
    current_position = start
    while current_position[0] < end[0]:
        next_position = (current_position[0] + grid_resolution, current_position[1])
        grid_x = int(round(next_position[0] / grid_resolution))
        grid_y = int(round(next_position[1] / grid_resolution))
        if grid_y < grid.shape[0] and grid_x < grid.shape[1]:
            if grid[grid_y, grid_x]:
                while grid_y < grid.shape[0] and grid[grid_y, grid_x]:
                    current_position = (current_position[0], current_position[1] - grid_resolution)
                    grid_y = int(round(current_position[1] / grid_resolution))
                    path.append(current_position)
            else:
                current_position = next_position
                path.append(current_position)
        else:
            break
    if current_position[1] != end[1]:
        current_position = (end[0], end[1])
        path.append(current_position)

    return path


# Note that the following paths must be updated with obstacle pictures from three different camera angles
front_image_path = "C:/Users/namit/Downloads/ImgTestFin4.jpeg"
back_image_path = "C:/Users/namit/Downloads/ImgTestFin2.jpeg"
right_image_path = "C:/Users/namit/Downloads/ImgTestFin3.jpeg"

front_cones, front_dots, front_image = detect_cones(front_image_path)
back_cones, back_dots, back_image = detect_cones(back_image_path)
right_cones, right_dots, right_image = detect_cones(right_image_path)

cv2.imshow('Highlighted Cones - Front', front_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

combined_cone_positions = []
rectangle_length = 1.8288
rectangle_width = rectangle_length / 1.5
image_width = 1600
scale_x = rectangle_length / image_width
image_height = 1200
scale_y = rectangle_width / image_height
edge_cones = []

for i in range(3):
    x_position = (i + 1) * rectangle_length / 4
    edge_cones.append((x_position, 0))
    edge_cones.append((x_position, rectangle_width))

combined_cone_positions = [pos for pos in combined_cone_positions if None not in pos]
sorted_cone_positions_x = [i[0] for i in sorted(front_dots, key=lambda x: x[0])][3:7]
sorted_cone_positions_y = [i[1] for i in sorted(front_dots, key=lambda x: x[1])]
relevant_y = [i[1] for i in sorted(front_dots, key=lambda x: x[0])][4:6]

for i in relevant_y:
    sorted_cone_positions_y.remove(i)

metric_y = []

for i in range(0, 8, 2):
    metric_y.append((sorted_cone_positions_y[i] + sorted_cone_positions_y[i + 1]) / 2)

for i in range(len(metric_y) - 1):
    point_1_y = relevant_y[0]
    if metric_y[i] < point_1_y < metric_y[i + 1]:
        cone_1_y = (i + 1, (point_1_y - metric_y[i]) / (metric_y[i + 1] - metric_y[i]))

for i in range(len(metric_y) - 1):
    point_2_y = relevant_y[1]
    if metric_y[i] < point_2_y < metric_y[i + 1]:
        cone_2_y = (i + 1, (point_2_y - metric_y[i]) / (metric_y[i + 1] - metric_y[i]))

cone_1_x = (sorted_cone_positions_x[1] - sorted_cone_positions_x[0]) / (sorted_cone_positions_x[-1] - sorted_cone_positions_x[0])
cone_2_x = (sorted_cone_positions_x[2] - sorted_cone_positions_x[0]) / (sorted_cone_positions_x[-1] - sorted_cone_positions_x[0])
final_1 = (rectangle_length - (rectangle_length * (cone_1_y[0] / 5) + (rectangle_length / 5 * cone_1_y[1])), rectangle_width * (1 - cone_1_x)-.1)
final_2 = (rectangle_length - (rectangle_length * (cone_2_y[0] / 5) + (rectangle_length / 5 * cone_2_y[1])), rectangle_width * (1 - cone_2_x))

combined_cone_positions.extend(edge_cones)
additional_points = [final_1, final_2]
combined_cone_positions.extend(additional_points)

fig, ax = plt.subplots()
rect = plt.Rectangle((0, 0), rectangle_length, rectangle_width, linewidth=1, edgecolor='r', facecolor='none')
ax.add_patch(rect)
cone_positions_3d = np.array(combined_cone_positions)
cone_radius_m = 0.03
marker_size = (cone_radius_m / rectangle_length) * fig.dpi ** 2
ax.scatter(cone_positions_3d[:, 0], cone_positions_3d[:, 1], s=marker_size/5, c='blue', marker='o')
additional_points_np = np.array(additional_points)
ax.scatter(additional_points_np[:, 0], additional_points_np[:, 1], s=marker_size/5, c='red', marker='o')

start_point = (0, 0.6096)
end_point = (1.8288, 0.6096)
grid_resolution = 0.01
grid_width = int(rectangle_length / grid_resolution)
grid_height = int(rectangle_width / grid_resolution)


def create_grid(cone_positions, cone_radius, grid_resolution, grid_width, grid_height):
    grid = np.zeros((grid_height, grid_width), dtype=bool)
    radius_in_cells = int(cone_radius / grid_resolution)
    for cone in cone_positions:
        cx, cy = cone
        grid_x = int(cx / grid_resolution)
        grid_y = int(cy / grid_resolution)
        for i in range(-radius_in_cells, radius_in_cells + 1):
            for j in range(-radius_in_cells, radius_in_cells + 1):
                if 0 <= grid_x + i < grid_width and 0 <= grid_y + j < grid_height:
                    if np.sqrt(i ** 2 + j ** 2) <= radius_in_cells:
                        grid[grid_y + j, grid_x + i] = True  # Mark as obstacle
    return grid


grid = create_grid(combined_cone_positions, cone_radius_m, grid_resolution, grid_width, grid_height)
path = generate_path(grid, start_point, end_point, 0.01)
path_np = np.array(path)

ax.plot(path_np[:, 0], path_np[:, 1], c='green', marker='x')
ax.imshow(grid.T, cmap='Greys', origin='lower', extent=[0, rectangle_length, 0, rectangle_width])
ax.set_xlim(-0.5, rectangle_length + 0.5)
ax.set_ylim(-0.5, rectangle_width + 0.5)
ax.set_xlabel('Length (m)')
ax.set_ylabel('Width (m)')
ax.set_title('Cone Positions Map with Path')
plt.savefig('map.png')
plt.show()


def run_mapping_script():
    fig, ax = plt.subplots()
    rect = plt.Rectangle((0, 0), rectangle_length, rectangle_width, linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect)
    cone_positions_3d = np.array(combined_cone_positions)

    cone_radius_m = 0.03
    marker_size = (cone_radius_m / rectangle_length) * fig.dpi ** 2

    ax.scatter(cone_positions_3d[:, 0], cone_positions_3d[:, 1], s=marker_size / 5, c='blue', marker='o')
    additional_points_np = np.array(additional_points)
    ax.scatter(additional_points_np[:, 0], additional_points_np[:, 1], s=marker_size / 5, c='red', marker='o')

    ax.set_xlim(-0.5, rectangle_length + 0.5)
    ax.set_ylim(-0.5, rectangle_width + 0.5)
    ax.set_xlabel('Length (m)')
    ax.set_ylabel('Width (m)')
    ax.set_title('Obstacle Map')

    plt.savefig('map.png')
    plt.close(fig)

    img = Image.open('map.png')
    img = img.resize((533, 400), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    img_label.config(image=img_tk)
    img_label.image = img_tk


def create_path_instructions(path):
    instructions = []
    current_instruction = None
    for i in range(1, len(path)):
        dx = path[i][0] - path[i - 1][0]
        dy = path[i][1] - path[i - 1][1]
        if dx != 0:
            direction = 'right' if dx > 0 else 'left'
            if current_instruction is None or current_instruction[0] != direction:
                if current_instruction is not None:
                    instructions.append(current_instruction)
                current_instruction = (direction, abs(dx))
            else:
                current_instruction = (direction, current_instruction[1] + abs(dx))
        if dy != 0:
            direction = 'up' if dy > 0 else 'down'
            if current_instruction is None or current_instruction[0] != direction:
                if current_instruction is not None:
                    instructions.append(current_instruction)
                current_instruction = (direction, abs(dy))
            else:
                current_instruction = (direction, current_instruction[1] + abs(dy))
        if i == len(path) - 1:
            instructions.append(current_instruction)
    formatted_instructions = []
    for instruction in instructions:
        steps = round((instruction[1])*3.28084)
        if steps == 0:
            steps = 1
        direction = instruction[0]
        if direction == "right":
            direction = "straight"
        elif direction == "down":
            direction = "right"
        elif direction == "up":
            direction = "left"
        else:
            direction = "back"
        if steps == 1:
            step_count = "step"
        else:
            step_count = "steps"
        formatted_instructions.append(f"{steps} {step_count} {direction}")
    return formatted_instructions


instructions = create_path_instructions(path)

root = tk.Tk()
root.title("NaviGuide")
root.geometry("800x600")
root.config(bg="#f7f7f7")

# Create the login frame
login_frame = tk.Frame(root, bg="#f7f7f7")
login_frame.pack(expand=True)

# Create and pack the title
title_label = tk.Label(root, text="NaviGuide", font=("Segoe UI", 30), bg="#f7f7f7", fg="#3f3f3f")
title_label.pack(pady=10)

login_inner_frame = tk.Frame(login_frame, bg="#f7f7f7")
login_inner_frame.pack(pady=10)

tk.Label(login_inner_frame, text="Username:", font=("Segoe UI", 14), bg="#f7f7f7").grid(row=0, column=0, pady=10,
                                                                                        padx=10)
username_entry = tk.Entry(login_inner_frame, font=("Segoe UI", 14))
username_entry.grid(row=0, column=1, pady=10, padx=10)

tk.Label(login_inner_frame, text="Password:", font=("Segoe UI", 14), bg="#f7f7f7").grid(row=1, column=0, pady=10,
                                                                                        padx=10)
password_entry = tk.Entry(login_inner_frame, font=("Segoe UI", 14), show="*")
password_entry.grid(row=1, column=1, pady=10, padx=10)

login_button = tk.Button(login_inner_frame, text="Login", font=("Segoe UI", 14), bg="#1abc9c", fg="#fff",
                         activebackground="#17a085", activeforeground="#fff", bd=0, padx=20, pady=10,
                         command=handle_login)
login_button.grid(row=2, columnspan=2, pady=20)

# Create the main frame
main_frame = tk.Frame(root, bg="#f7f7f7")

button_frame = tk.Frame(main_frame, bg="#f7f7f7")
button_frame.pack(pady=20)

next_direction_button = tk.Button(button_frame, text="Next Direction", font=("Segoe UI", 14), bg="#1a9bfc", fg="#fff",
                                  activebackground="#1477c7", activeforeground="#fff", bd=0, padx=20, pady=10,
                                  command=print_directions)
next_direction_button.grid(row=0, column=0, padx=10)

# Note that the map should not be displayed until after all directions have been displayed
map_button = tk.Button(button_frame, text="Show Map", font=("Segoe UI", 14), bg="#1abc9c", fg="#fff",
                       activebackground="#17a085", activeforeground="#fff", bd=0, padx=20, pady=10,
                       command=run_mapping_script)
map_button.grid(row=0, column=1, padx=10)

# Note that the forward, stop, left, right, and photo buttons currently have no function as they are meant for controlling robot

forward_button = tk.Button(button_frame, text="Forward", font=("Segoe UI", 14), bg="#1a9bfc", fg="#fff",
                           activebackground="#1477c7", activeforeground="#fff", bd=0, padx=20, pady=10)
forward_button.grid(row=1, column=0, padx=10, pady=10)

stop_button = tk.Button(button_frame, text="Stop", font=("Segoe UI", 14), bg="#1a9bfc", fg="#fff",
                        activebackground="#1477c7", activeforeground="#fff", bd=0, padx=20, pady=10)
stop_button.grid(row=1, column=1, padx=10, pady=10)

left_button = tk.Button(button_frame, text="Left", font=("Segoe UI", 14), bg="#1a9bfc", fg="#fff",
                        activebackground="#1477c7", activeforeground="#fff", bd=0, padx=20, pady=10)
left_button.grid(row=2, column=0, padx=10, pady=10)

right_button = tk.Button(button_frame, text="Right", font=("Segoe UI", 14), bg="#1a9bfc", fg="#fff",
                         activebackground="#1477c7", activeforeground="#fff", bd=0, padx=20, pady=10)
right_button.grid(row=2, column=1, padx=10, pady=10)

take_photo_button = tk.Button(button_frame, text="Take Photo", font=("Segoe UI", 14), bg="#1a9bfc", fg="#fff",
                              activebackground="#1477c7", activeforeground="#fff", bd=0, padx=20, pady=10)
take_photo_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

img_label = tk.Label(main_frame, bg="#f7f7f7")
img_label.pack(pady=20)

directions_label = tk.Label(main_frame, text="", font=("Segoe UI", 14), bg="#f7f7f7", fg="#333")
directions_label.pack(pady=20)

footer_label = tk.Label(root, text="Senior Project", font=("Segoe UI", 10), bg="#f7f7f7", fg="#666")
footer_label.pack(side=tk.BOTTOM, pady=10)

root.mainloop()

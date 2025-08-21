# from openpyxl import load_workbook
# from CUSTApp.models import Users, Convocation
# from typing import Tuple
import os

# def upload_student_data(
#     file_path: str,
# ) -> None:

#     total_updated = 0
#     total_rows = 0
#     not_exists = 0
#     wb = load_workbook(filename=file_path, read_only=True)
#     active = wb.active
#     header = next(active.iter_rows(min_row=1, max_row=1, values_only=True))
#     reg_idx = header.index("uu_id")
#     name_idx = header.index("Name")
#     gender_idx = header.index("Gender")
#     father_name_idx = header.index("Father Name")
#     email_idx = header.index("Email personal")
#     designation_idx = header.index("designation")

#     for rows in active.iter_rows(min_row=2, values_only=True):  # Skip the header row
#         reg_no = rows[reg_idx]
#         name = rows[name_idx]
#         father_name = rows[father_name_idx]
#         email = rows[email_idx]
#         gender = rows[gender_idx]
#         designation = rows[designation_idx]
#         user_type = "Staff"
#         try:
#             Users.objects.update_or_create(
#             email=email,
#             defaults={
#                 "uu_id": reg_no,
#                 "name": name,
#                 "father_name": father_name,
#                 "email": email,
#                 "user_type": user_type,
#                 "gender":gender,
#                 "designation":designation
#             },
#         )
#             print("Updated or created sucessfully! for email = ",email)
#         except Users.MultipleObjectsReturned:
#             print("Multiple objects returned for this email ",email)
#             continue
#     print("-" * 10)
#     print(f"Total rows  = {total_rows}")
#     print(f"Total Users updated present in the DB {total_updated}")
#     print(f"Total users to add = {not_exists}")

# def upload_student_images(image_folder: str) -> None:

#     try:
#         images = os.listdir(image_folder)
#         total_images = len(images)

#         for index,image in enumerate(images,):
#             image_path = os.path.join(image_folder, image)
#             reg_no = image.split('.')[0]
#             user = Users.objects.filter(uu_id=reg_no).first()
#             if user:
#                 with open(image_path, 'rb') as img_file:
#                     user.picture.save(image, img_file, save=True)
#                 percent = (index / total_images) * 100
#                 print(f"\rProcessing {index}/{total_images} images ({percent:.2f}%)", end='')

#             else:
#                 continue

#     except FileNotFoundError:
#         print(f"Image folder {image_folder} does not exist.")
#         return


dirs = os.listdir()


def count_number_of_lines(filepath: str):
    with open(filepath, "r") as file:
        number_of_lines = sum(1 for line in file)
    return number_of_lines


def calculate_number_of_lines(file_type, dirs):
    total_number_of_lines = 0
    for dir in dirs:
        # ignore all the folders/files that dont end with the file type
        if dir.startswith("."):
            continue
        ext = os.path.splitext(dir)[1]
        if os.path.isfile(dir):
            if not (ext in file_type):
                continue
            lines = count_number_of_lines(dir)
            total_number_of_lines += lines
            print(f"{dir} is a file. and number of lines = {lines}")

        elif os.path.isdir(dir):
            subdirs = [os.path.join(dir, d) for d in os.listdir(dir)]
            total_number_of_lines += calculate_number_of_lines(file_type, subdirs)

    return total_number_of_lines


total_lines = calculate_number_of_lines([".py",".html"], dirs)
print(total_lines)

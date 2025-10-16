'''
This code is used to process each image of the dataset to not only use a standard camera focus, 
and to amplify the angles used and known for the model.

This method aplyes rotations, some zoom, focus level, etc. to all images and creates variations of every image.
'''

import os
import cv2
import imgaug.augmenters as iaa
from tqdm import tqdm

# Folders
input_dir = "side BN"       # original pictures
output_dir = "sideBN_aug" 
os.makedirs(output_dir, exist_ok=True)

# Definir la secuencia de augmentaciones
# Define augmentations secuences
seq = iaa.Sequential([
    iaa.Fliplr(0.5),  # horizontal flip 
    iaa.Flipud(0.2),  # vertical flip  (less frecuent)
    iaa.Affine(
        rotate=(-25, 25),  # rotation
        scale=(0.9, 1.1),  # small zoom in/out
        shear=(-10, 10)    # small deformation
    ),
    iaa.Multiply((0.7, 1.3)),       # change brigtness
    iaa.LinearContrast((0.6, 1.4)), # change contrast
    iaa.AdditiveGaussianNoise(scale=(0, 0.02*255)), # gaussian noise
    iaa.GaussianBlur(sigma=(0, 1.0)) # focus
])


# Process each image
for img_file in tqdm(os.listdir(input_dir)):
    img_path = os.path.join(input_dir, img_file)
    image = cv2.imread(img_path)
    if image is None:
        continue
    
    filename, ext = os.path.splitext(img_file)

    # Number of variations to generate per image
    for i in range(7):
        aug_img = seq(image=image)
        out_path = os.path.join(output_dir, f"{filename}_aug{i}{ext}")
        cv2.imwrite(out_path, aug_img)

print(f"[INFO] Augmentation completed. Images saved in {output_dir}")

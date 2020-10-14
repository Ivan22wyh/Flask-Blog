import os
from secrets import token_hex
from PIL import Image
from flask import current_app

def save_image(form_image):
	random_hex = token_hex(8)
	_, f_ext = os.path.splitext(form_image.filename)
	img_fn = random_hex + f_ext
	img_path = os.path.join(current_app.root_path, 'static/images/profile_img', img_fn)
	
	output_size = (125, 125)
	i= Image.open(form_image)
	i.thumbnail(output_size)
	i.save(img_path)

	return img_fn

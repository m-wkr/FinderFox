from PIL import Image

def image_converter(path_to_image_file):
    image = Image.open(path_to_image_file)
    image = image.resize((64,64))
    x=0
    y=0
    for i in range(16):
        image.crop(((x*16),(y*16),(x*16+15),(y*16+15))).save("./icons/"+str(i+1)+".png","png")
        x += 1
        if x>=4:
            x = 0
            y += 1

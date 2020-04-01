from scipy.ndimage import rotate
import numpy as np
import cv2 

def translate(img, shift=10, direction='right', roll=False):
    assert direction in ['right', 'left', 'down', 'up'], 'Directions should be top|up|left|right'
    img = img.copy()
    if direction == 'right':
        right_slice = img[:, -shift:].copy()
        img[:, shift:] = img[:, :-shift]
        if roll:
            img[:,:shift] = np.fliplr(right_slice)
        else:
            img[:,:shift] = np.zeros_like(right_slice)
    if direction == 'left':
        left_slice = img[:, :shift].copy()
        img[:, :-shift] = img[:, shift:]
        if roll:
            img[:, -shift:] = left_slice
        else:
            img[:, -shift:] = np.zeros_like(left_slice)
    if direction == 'down':
        down_slice = img[-shift:, :].copy()
        img[shift:, :] = img[:-shift,:]
        if roll:
            img[:shift, :] = down_slice
        else:
            img[:shift, :] = np.zeros_like(down_slice)
    if direction == 'up':
        upper_slice = img[:shift, :].copy()
        img[:-shift, :] = img[shift:, :]
        if roll:
            img[-shift:,:] = upper_slice
        else:
            img[-shift:,:] = np.zeros_like(upper_slice)
    return img


def random_crop(img, crop_size=(10, 10)):
    assert crop_size[0] <= img.shape[0] and crop_size[1] <= img.shape[1], "Crop size should be less than image size"
    img = img.copy()
    w, h = img.shape[:2]
    x, y = np.random.randint(h-crop_size[0]), np.random.randint(w-crop_size[1])
    img = img[y:y+crop_size[0], x:x+crop_size[1]]
    return img


def rotate_img(img, angle, bg_patch=(5,5)):
    assert len(img.shape) <= 3, "Incorrect image shape"
    rgb = len(img.shape) == 3
    if rgb:
        bg_color = np.mean(img[:bg_patch[0], :bg_patch[1], :], axis=(0,1))
    else:
        bg_color = np.mean(img[:bg_patch[0], :bg_patch[1]])
    img = rotate(img, angle, reshape=False)
    mask = [img <= 0, np.any(img <= 0, axis=-1)][rgb]
    img[mask] = bg_color
    return img


def gaussian_noise(img, mean=0, sigma=0.03):
    shape = img.shape
    img = img.copy()
    noise = np.random.normal(mean, sigma, img.shape)*255
    noise = noise.reshape(shape)
    mask_overflow_upper = img+noise >= 255
    # print(img)
    # print(img+noise)
    mask_overflow_lower = img+noise < 0
    noise[mask_overflow_upper] = 1.0
    noise[mask_overflow_lower] = 0
    img = np.add(img, noise, out=img, casting="unsafe")
    # img += noise
    return img


def brightness(img, scale):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(img)
    v = np.clip(v * scale, 0, 255, out=v)
    img = cv2.merge((h, s, v))
    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    return img


def augmentImage(img):
    cp = img.copy()
    h,w = img.shape[0:2]
    # print(h,w)
    images = [img]

    # Translate Image
    # shift_ = int(0.15*w)
    # images.append(translate(cp, direction='up', shift=shift_))
    # images.append(translate(cp, direction='down', shift=shift_))
    # images.append(translate(cp, direction='left', shift=shift_))
    # images.append(translate(cp, direction='right', shift=shift_))

    # # Crop Image
    # crop_part = (int(w*0.9), int(h*0.9))
    # images.append(random_crop(cp, crop_size=crop_part))
    # images.append(random_crop(cp, crop_size=crop_part))
    # images.append(random_crop(cp, crop_size=crop_part))
    # images.append(random_crop(cp, crop_size=crop_part))

    # # Rotate Image
    # # negDegrees = [-30, -25, -20, -18, -16, -14, -10, -6, -2]
    # # posDegrees = [30, 25, 20, 18, 16, 14, 10, 6, 2]

    # # for degree in negDegrees +  posDegrees:
    # #     images.append(rotate_img(cp, angle=degree))

    images.append(rotate_img(cp, angle=-15))
    images.append(rotate_img(cp, angle=15))
    # images.append(rotate_img(cp, angle=-30))
    # images.append(rotate_img(cp, angle=30))

    # # Gaussian Noise Image
    # images.append(gaussian_noise(cp, sigma=0.03))
    # images.append(gaussian_noise(cp, sigma=0.1))

    # Dark and Bright Images
    images.append(brightness(cp, scale=0.4))
    images.append(brightness(cp, scale=1.25))

    return images


if __name__ == "__main__":
    temp = cv2.imread("temp\\1.JPG")
    timg = cv2.resize(temp, (500,500))
    images = augmentImage(timg)
    for ix,i in enumerate(images):
        cv2.imshow(f"Image{ix}",i);
        
    cv2.waitKey(0);
    cv2.destroyAllWindows()

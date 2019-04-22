#!/bin/python
"""
The help functions that transfer a image to a char representation.

Author:
    Wenhao Gao

Content:
    get_char: *function*
        a help function used in img2chars function

    img2chars: *function*
        a help function used in main in video2chars
"""
import numpy as np
from PIL import Image, ImageFont, ImageDraw


def get_char(gray, pixels=None):
    """
    A help function that transfer a gray degree to a char
    The value of a gray degree is from 0 to 255
    Scale it to a length of pixels string and return the char in that location

    :param gray: *int*
        value of gray degree

    :param pixels: *string*
        the char string used to generate char video
        if None, use the default

    :return: *char*
        the char that represent the gray degree input
    """
    if pixels is None:
        pixels = \
            "$#@&%ZYXWVUTSRQPONMLKJIHGFEDCBA098765432?][}{/)(><zyxwvutsrqponmlkjihgfedcba*+1-. "

    index = int(gray * (len(pixels) - 1) / 255)
    return pixels[index]


def img2chars(
        frame,
        chars_width=None,
        put_original=False,
        loc='upper_left',
        original_size=2
):
    """
    A help function that transfer one frame of video into a char represented frame
    Resize the image to the char_img size, and choose a char due to the gray degree of that location
    Then put it back in a blank image as an image, the same color as the original

    if put_original is set to True, the original frame will be placed at connor to compare

    :param frame: *ndarray*
        The frame to be transferred.

    :param chars_width: *int*
        The number of chars in x-axis of output image

    :param put_original: *Boolean*
        If to put original image in the connor

    :param loc: *string*
        The location to place original frame
        choice: 'upper_left', 'upper_right', 'lower_left', 'lower_right'

    :param original_size: *float*
        The size of showed original frame, times of char_img size

    :return: *ndarray*
        The frame representation of transferred frame
    """
    # Set parameters
    font_width = 8
    if chars_width is None:
        chars_width = int(frame.shape[1] / font_width)
    chars_height = int(chars_width * frame.shape[0] / frame.shape[1])
    video_size = int(chars_width * font_width), int(chars_height * font_width)

    # Read in frame and transfer to img and gray img in char size
    img_original = Image.fromarray(frame, 'RGB')
    img = img_original.resize((chars_width, chars_height))
    img_gray = img.convert(mode='L')

    # Build a brush and draw so that can put a char in the image
    img_chars = Image.new('RGB', video_size, color='white')
    brush = ImageDraw.Draw(img_chars)

    # for location in char size image put char picture at that location
    for y in range(chars_height):
        for x in range(chars_width):
            # read in original color and gray degree
            r, g, b = img.getpixel((x, y))
            gray = img_gray.getpixel((x, y))

            # get the char represent the gray degree
            char = get_char(gray)
            position = x * font_width, y * font_width
            # put the char in the blank image
            brush.text(position, char, fill=(r, g, b))

    # out original image on it to compare
    if put_original:
        # set the original image size
        img_put = img_original.resize((int(chars_width * original_size), int(chars_height * original_size)))

        # set the location to put original image
        if loc == 'upper_left':
            origin = (0, 0)
        elif loc == 'upper_right':
            origin = (img_chars.width - img_put.width, 0)
        elif loc == 'lower_left':
            origin = (0, img_chars.height - img_put.height)
        elif loc == 'lower_right':
            origin = (img_chars.width - img_put.width, img_chars.height - img_put.height)
        else:
            raise NameError('What the fuck are you putting in? See the options in docstring')

        # put original image pixel by pixel
        for y in range(img_put.height):
            for x in range(img_put.width):
                position = origin[0] + x, origin[1] + y
                r, g, b = img_put.getpixel((x, y))
                img_chars.putpixel(position, (r, g, b))

    # return img_chars
    return np.array(img_chars)

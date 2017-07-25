#!/usr/bin/env python3
import wx

PROGRAM_TITLE = 'InnoScan'
# width height ratio of letter paper
INITIAL_PANEL_SIZE = (int(216*2.3),int(297*2.3))
THUMBNAIL_SIZE = (int(216*0.4), int(297*0.4))
# quality of screen resizing
RESIZE_QUALITY = wx.IMAGE_QUALITY_BICUBIC

# default scanner settings
# note that this must match with actual scanner parameter
DEFAULT_MODE = 'Color'
DEFAULT_SCAN_AREA = 'Letter'
DEFAULT_TXT_MODE = 'Gray'
DEFAULT_TXT_RES = 150
DEFAULT_TXT_SIZE = 'Letter'
DEFAULT_IMG_MODE = 'Color'
DEFAULT_IMG_RES = 300
DEFAULT_IMG_SIZE = 'Letter'

# anti-halftone filter parameters
GB_RADIUS = 1.0
UM_RADIUS = 2.5
UM_PERCENT = 130
UM_THOLD = 5

# background image alpha channel parameters
ALPHA_THOLD = 220       # threshold value
ALPHA_BGND = 0          # background alpha
ALPHA_FGND = 255        # foreground alpha

# icons
ICON_DIR = './res/'
ICON_SIZE = '32'
ICON_NEW = ICON_DIR + 'new-icon_' + ICON_SIZE + '.png'
ICON_TXT = ICON_DIR + 'text-documents_' + ICON_SIZE + '.png'
ICON_IMG = ICON_DIR + 'photos_' + ICON_SIZE + '.png'
ICON_CRP = ICON_DIR + 'selection-square_' + ICON_SIZE + '.png'
ICON_CUT = ICON_DIR + 'scissors-tool_' + ICON_SIZE + '.png'
ICON_ULD = ICON_DIR + 'up-arrow-upload-button_' + ICON_SIZE + '.png'
ICON_SAV = ICON_DIR + 'down-arrow-download-button_' + ICON_SIZE + '.png'
ICON_SET = ICON_DIR + 'cogwheel_' + ICON_SIZE + '.png'

# watermark font
FONT_DIR = './res/'
# font size for initial drawing
WATERMARK_PNT = 100
# alpha blending
WATERMARK_OPQ = 70

# canny edge initial threshold (before calibration)
CANNY_LOW = 50
CANNY_HIGH = 180
# hough lines threshold
HOUGH_THLIST = (300,250,200,100)

# color scheme data
color_schemes = {
        # ethanschoonover.com/solarized
        'solarized dark':{
            'accent':[
                (0xb5,0x89,0x00),
                (0xcb,0x4b,0x16),
                (0xdc,0x32,0x2f),
                (0xd3,0x36,0x82),
                (0x6c,0x71,0xc4),
                (0x26,0x8b,0xd2),
                (0x2a,0xa1,0x98),
                (0x85,0x99,0x00)],
            'bgnd':[
                (0x00,0x2b,0x36),
                (0x07,0x36,0x42)],
            'fgnd':[
                (0x58,0x6e,0x75),
                (0x65,0x7b,0x83),
                (0x83,0x94,0x96),
                (0x93,0xa1,0xa1)],},
        # ethanschoonover.com/solarized
        'solarized light':{
            'accent':[
                (0xb5,0x89,0x00),
                (0xcb,0x4b,0x16),
                (0xdc,0x32,0x2f),
                (0xd3,0x36,0x82),
                (0x6c,0x71,0xc4),
                (0x26,0x8b,0xd2),
                (0x2a,0xa1,0x98),
                (0x85,0x99,0x00)],
            'bgnd':[
                (0xee,0xe8,0xd5),
                (0xfd,0xf6,0xe3)],
            'fgnd':[
                (0x58,0x6e,0x75),
                (0x65,0x7b,0x83),
                (0x83,0x94,0x96),
                (0x93,0xa1,0xa1)],},
        }

COLOR_SCHEME = 'solarized dark'
# screen magnification
SCREEN_MAG = 3
# define widget minimum size for nice alignment
CTRL_MIN_SIZE = (150,-1)

# image file save / load
IMAGE_DIR = './img'
LOADFILETYPE = 'BMP,EPS,GIF,JPG,PNG files(*.bmp;*.eps;*.gif;*.jpg;*.png)|' \
               '*.bmp;*.eps;*.gif;*.jpg;*.png|All files (*.*)|*.*'
SAVEFILETYPE = 'BMP,EPS,GIF,JPG,PNG files(*.bmp;*.eps;*.gif;*.jpg;*.png)|' \
               '*.bmp;*.eps;*.gif;*.jpg;*.png|PDF file (*.pdf)|*.pdf'

JPGQUALITY = 90
PNGOPTIMIZ = False


if __name__ == "__main__":
    print('')
    print('> This is configuration file for innoscan.py.')
    print('> Run innoscan.py instead.')
    print('')

#!/usr/bin/env python3
import glob
import math
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFont, ImageDraw, ImageFilter
from settings import *

canny_low = CANNY_LOW
canny_high = CANNY_HIGH
IPTEST = [
        'find_canny_thresholds',
        'GetRectifiedImage',
        ]

#--------1---------2---------3---------4---------5---------6---------7---------8
# code taken from shunsukeaihara
#
# https://gist.github.com/shunsukeaihara/4603234
#
def from_pil(pimg):
    pimg = pimg.convert(mode='RGB')
    nimg = np.asarray(pimg)
    nimg.flags.writeable = True

    return nimg

def to_pil(nimg):
    return Image.fromarray(np.uint8(nimg))

def stretch_pre(nimg):
    """
    from 'Applicability Of White-Balancing Algorithms to Restoring Faded
    Colour Slides: An Empirical Evaluation'
    """
    nimg = nimg.transpose(2, 0, 1)
    nimg[0] = np.maximum(nimg[0]-nimg[0].min(),0)
    nimg[1] = np.maximum(nimg[1]-nimg[1].min(),0)
    nimg[2] = np.maximum(nimg[2]-nimg[2].min(),0)

    return nimg.transpose(1, 2, 0)

def grey_world(nimg):
    nimg = nimg.transpose(2, 0, 1).astype(np.uint32)
    mu_g = np.average(nimg[1])
    nimg[0] = np.minimum(nimg[0]*(mu_g/np.average(nimg[0])),255)
    nimg[2] = np.minimum(nimg[2]*(mu_g/np.average(nimg[2])),255)

    return  nimg.transpose(1, 2, 0).astype(np.uint8)

def max_white(nimg):
    if nimg.dtype==np.uint8:
        brightest=float(2**8)
    elif nimg.dtype==np.uint16:
        brightest=float(2**16)
    elif nimg.dtype==np.uint32:
        brightest=float(2**32)
    else:
        brightest==float(2**8)

    nimg = nimg.transpose(2, 0, 1)
    nimg = nimg.astype(np.int32)
    nimg[0] = np.minimum(nimg[0] * (brightest/float(nimg[0].max())),255)
    nimg[1] = np.minimum(nimg[1] * (brightest/float(nimg[1].max())),255)
    nimg[2] = np.minimum(nimg[2] * (brightest/float(nimg[2].max())),255)

    return nimg.transpose(1, 2, 0).astype(np.uint8)

def stretch(nimg):
    return max_white(stretch_pre(nimg))

def retinex(nimg):
    nimg = nimg.transpose(2, 0, 1).astype(np.uint32)
    mu_g = nimg[1].max()
    nimg[0] = np.minimum(nimg[0]*(mu_g/float(nimg[0].max())),255)
    nimg[2] = np.minimum(nimg[2]*(mu_g/float(nimg[2].max())),255)

    return nimg.transpose(1, 2, 0).astype(np.uint8)

def retinex_adjust(nimg):
    """
    from 'Combining Gray World and Retinex Theory for Automatic White
    Balance in Digital Photography'
    """
    nimg = nimg.transpose(2, 0, 1).astype(np.uint32)
    sum_r = np.sum(nimg[0])
    sum_r2 = np.sum(nimg[0]**2)
    max_r = nimg[0].max()
    max_r2 = max_r**2
    sum_g = np.sum(nimg[1])
    max_g = nimg[1].max()
    coefficient = np.linalg.solve(np.array([[sum_r2,sum_r],[max_r2,max_r]]),
            np.array([sum_g,max_g]))

    nimg[0] = np.minimum((nimg[0]**2)*coefficient[0] +
            nimg[0]*coefficient[1],255)
    sum_b = np.sum(nimg[1])
    sum_b2 = np.sum(nimg[1]**2)
    max_b = nimg[1].max()
    max_b2 = max_r**2
    coefficient = np.linalg.solve(np.array([[sum_b2,sum_b],[max_b2,max_b]]),
            np.array([sum_g,max_g]))
    nimg[1] = np.minimum((nimg[1]**2)*coefficient[0] +
            nimg[1]*coefficient[1],255)

    return nimg.transpose(1, 2, 0).astype(np.uint8)

#--------1---------2---------3---------4---------5---------6---------7---------8
# Derive rotation angle and the center coordinate from the Hough lines
#
RAD_45 = np.radians(45)
RAD_90 = np.radians(90)
RAD_SMALL = np.radians(0.5)
MIN_RHOVAR = 1000
MAX_RADVAR = np.radians(2)

def compute_rotation(lines):
    # handle degenerative case
    if lines is None:
        return None

    # copy angles
    ang = np.copy(lines[:,0,1])
    # fold once
    ang[ang > RAD_45] = ang[ang > RAD_45] - RAD_90
    # fold twice if necessary
    ang[ang > RAD_45] = ang[ang > RAD_45] - RAD_90

    # derive indexing set excluding
    idxset = abs(ang - np.median(ang)) < MAX_RADVAR

    # compute rotation angle for later use
    ang_rot = np.mean(ang[idxset])

    # rho and rad of inliers only
    rho = lines[idxset,0,0]
    rad = lines[idxset,0,1]

    # divide rho set into two groups
    if abs(ang_rot) < RAD_SMALL:
        # small angle case
        if ang_rot > 0:
            rho1 = rho[rad < RAD_45]
            rho2 = rho[rad >= RAD_45]
        else:
            rho1 = rho[rad >= RAD_45]
            rho2 = rho[rad < RAD_45]
    else:
        rho1 = rho[rad < RAD_90]
        rho2 = rho[rad >= RAD_90]

    # at least two distictive values should be found in each group
    if rho1.size < 2 or np.var(rho1) < MIN_RHOVAR:
        return None
    if rho2.size < 2 or np.var(rho2) < MIN_RHOVAR:
        return None

    # compute max, min, and mean
    rho1_max = np.max(rho1)
    rho1_min = np.min(rho1)
    # note that only the length matters
    rho1_avg = abs((rho1_max + rho1_min)/2.)

    rho2_max = np.max(rho2)
    rho2_min = np.min(rho2)
    # note that only the length matters
    rho2_avg = abs((rho2_max + rho2_min)/2.)

    # CW rotation
    if ang_rot > 0:
        # size
        lx = rho1_max - rho1_min
        ly = rho2_max - rho2_min
        # centre
        cx = rho1_avg * np.cos(ang_rot) - rho2_avg * np.sin(ang_rot)
        cy = rho1_avg * np.sin(ang_rot) + rho2_avg * np.cos(ang_rot)
        # diagonal length and angle
        dl = np.sqrt(lx**2 + ly**2)/2.
        da = np.arctan(ly/lx)
        # bounding box
        top = cy - dl * np.sin(da + ang_rot)
        bottom = cy + dl * np.sin(da + ang_rot)
        left = cx - dl * np.cos(da - ang_rot)
        right = cx + dl * np.cos(da - ang_rot)

    # CCW rotation
    else:
        # size
        lx = rho2_max - rho2_min
        ly = rho1_max - rho1_min
        # centre
        cx = rho1_avg * np.sin(-ang_rot) + rho2_avg * np.cos(-ang_rot)
        cy = rho1_avg * np.cos(-ang_rot) - rho2_avg * np.sin(-ang_rot)
        # diagonal length and angle
        dl = np.sqrt(lx**2 + ly**2)/2.
        da = np.arctan(ly/lx)
        # bounding box
        top = cy - dl * np.sin(da - ang_rot)
        bottom = cy + dl * np.sin(da - ang_rot)
        left = cx - dl * np.cos(da + ang_rot)
        right = cx + dl * np.cos(da + ang_rot)

    return {'centre':(cx,cy), 'angle': ang_rot,
            'size':(lx,ly), 'bb':(top,left,bottom,right)}

def find_canny_thresholds(img):
    global canny_low, canny_high
    # convert PIL image to opencv image
    cvimg = np.array(img)

    # further convertion into gray image
    if img.mode == 'RGB':
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_RGB2GRAY)

    # high threshold first
    canny_low = 10
    for canny_high in range(200, 50, -10):
        edges = cv2.Canny(cvimg, canny_low, canny_high, apertureSize=3)

        if np.count_nonzero(edges) < 200:
            break

    # low threshold
    for canny_low in range(10, canny_high - 20, 10):
        edges = cv2.Canny(cvimg, canny_low, canny_high, apertureSize=3)

        if np.count_nonzero(edges) < 100:
            break

#--------1---------2---------3---------4---------5---------6---------7---------8
#
def AdjustWhiteBalance(img, method = 'Stretch'):
    # convert PIL to numpy
    arr = from_pil(img)
    #
    if method == 'Stretch':
        arr = stretch(arr)
    elif method == 'Grey World':
        arr = grey_world(arr)
    elif method == 'Retinex':
        arr = retinex(arr)
    elif method == 'Retinex Adjust':
        arr = retinex_adjust(arr)
    elif method == 'Max White':
        arr = max_white(arr)

    # back to PIL and return
    return to_pil(arr)

#
# apply calibration to the image
#
def ApplyCalibration(img, caltype):

    if caltype == 'Color':
        return img.copy()

    elif caltype == 'Gamma':
        return img.copy()

    else:
        return img.copy()

#
#
#
def GetRectifiedImage(img):
    # convert PIL image to opencv image
    cvimg = np.array(img)

    # further convertion into gray image
    if img.mode == 'RGB':
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_RGB2GRAY)

    # canny edge
    edges = cv2.Canny(cvimg, canny_low, canny_high, apertureSize=3)

    # dilate
    edges = cv2.dilate(edges, np.ones((3,3), np.int8))
    # then find contours
    edges, contours, hr = cv2.findContours(edges, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    # draw the contour on the blank background
    blank = np.zeros_like(edges)
    cv2.drawContours(blank, contours, -1, (255,255,255), 1)

    # Hough lines probabilistic
    for thold in HOUGH_THLIST:
        lines = cv2.HoughLines(blank, 1, np.pi/720, thold)
        rot = compute_rotation(lines)

        if rot is not None:
            break

    if rot is None:
        # do nothing and just return
        return None, (0,0)

    # bounding box, angle, size, centre
    (t,l,b,r) = rot['bb']
    ang = math.degrees(rot['angle'])
    (w,h) = rot['size']
    (cx,cy) = rot['centre']

    # crop
    crop = img.crop((int(l+0.5),int(t+0.5),int(r+0.5),int(b+0.5)))
    # rotate
    crop = crop.rotate(ang, expand=1, resample = Image.BICUBIC)
    # crop again
    dx = (crop.size[0] - w)/2.
    dy = (crop.size[1] - h)/2.
    crop = crop.crop((int(dx+0.5),int(dy+0.5),
            int(crop.size[0]-dx+0.5),int(crop.size[1]-dy+0.5)))

    return crop, (cx,cy)

def AdjustColorBalance(img, cb):
    return ImageEnhance.Color(img).enhance(cb)

def AdjustContrast(img, ct):
    return ImageEnhance.Contrast(img).enhance(ct)

def AdjustBrightness(img, br):
    return ImageEnhance.Brightness(img).enhance(br)

def AdjustSharpness(img, sn):
    return ImageEnhance.Sharpness(img).enhance(sn)

#
# apply filter on the image
# be sure not to change the original image
#
def ApplyFilter(img, sh):
    if sh == 'Blur':
        return img.filter(ImageFilter.BLUR)
    elif sh == 'Contour':
        return img.filter(ImageFilter.CONTOUR)
    elif sh == 'Detail':
        return img.filter(ImageFilter.DETAIL)
    elif sh == 'Edge Enhance':
        return img.filter(ImageFilter.EDGE_ENHANCE)
    elif sh == 'Emboss':
        return img.filter(ImageFilter.EMBOSS)
    elif sh == 'Smooth':
        return img.filter(ImageFilter.SMOOTH)
    elif sh == 'Unsharpen':
        return img.filter(ImageFilter.SHARPEN)
    elif sh == 'Anti-Halftone':
        return img.filter(ImageFilter.GaussianBlur(GB_RADIUS)).filter(
                ImageFilter.UnsharpMask(UM_RADIUS, UM_PERCENT, UM_THOLD))
    else:
        return img.copy()

#
# Draw watermark string
#
def ApplyWatermark(img, wm):
    # check font file
    ttflist = glob.glob(FONT_DIR + '*.ttf')
    if len(ttflist) == 0:
        wx.MessageBox("No font file found in the resource folder.\n" +
                "Copy a font file (*.ttf) into the folder ({}).".format(
                 FONT_DIR))
        return img
    else:
        # font
        fnt = ImageFont.truetype(FONT_DIR + ttflist[0], WATERMARK_PNT)

    # change image format
    img = img.convert(mode='RGBA')
    rw,rh = img.size
    # blank image with enough size
    txt = Image.new('RGBA', (rh,rw), (255,255,255,0))
    # drawing context
    dc = ImageDraw.Draw(txt)
    # draw text with opacity
    dc.text((10,10), wm, font=fnt, fill=(0,0,0,WATERMARK_OPQ))
    # get text size
    txw, txh = dc.textsize(wm, font=fnt)
    # crop
    crop = txt.crop((0,0,txw+20,txh+20))
    # rotate
    rot = crop.rotate(math.degrees(math.tan(rw/float(rh))), expand=1,
        resample = Image.BICUBIC)
    # resize
    txt = rot.resize(img.size, resample = Image.BICUBIC)
    # alpha channel composite
    img = Image.alpha_composite(img,txt)
    # drop alpha channel and return
    return img.convert(mode='RGB')

if __name__ == "__main__":

    if IPTEST is not None:

        if 'find_canny_thresholds' in IPTEST:
            img = Image.open(IMAGE_DIR + '/bgnd_2.png')
            find_canny_thresholds(img)
            print('canny_low:', canny_low, ' canny_high:', canny_high)

        if 'GetRectifiedImage'in IPTEST:
            # Test rectification
            img = Image.open(IMAGE_DIR + '/test_2.png')
            rect, (cx,cy) = GetRectifiedImage(img)
            print('rect:', rect, '(cx,cy)',(cx,cy))

    else:
        print('')
        print('> This is image process utilities for innoscan.py.')
        print('> Run innoscan.py instead.')
        print('')
#--------1---------2---------3---------4---------5---------6---------7---------8

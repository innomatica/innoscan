#!/usr/bin/env python3
#
# Disclaimer
#
#   This program is provided as is without any guarantees or warranty.
#   The author is not responsible for any damage or loses of any kind
#   caused by the use or misuse of the program.
#
# Prerequisites
#
#   python NumPy package: www.numpy.org
#   python PIL package: pillow.readthedocs.io
#   python SANE package: python-sane.readthedocs.io
#   python OpenCV package: www.opencv.org
#   wxpython: wxpython.org
#   PDFtk : www.pdflabs.com/tools/pdftk-the-pdf-toolkit
#
# Bookmarks for vim
#
# SETUP_DIALOG
# CALIBRATION_DIALOG
# IMAGE_PANEL
# IMAGE_BOOK
# MAIN_FRAME
# MAIN_EVENT_HANDLERS
# MAIN_SUPPORT_FUNCTIONS

# generic
import glob
import os
# wx
import wx
import wx.lib.imagebrowser as ib
from wx.lib.mixins.rubberband import RubberBand
# numpy and PIL
import numpy as np
from PIL import Image
# local
from settings import *
import imgprocess as ipc
from scanner import Scanner


#--------1---------2---------3---------4---------5---------6---------7---------8
#
# SETUP_DIALOG
#
class SetupDialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        wx.Dialog.__init__(self, *args, **kwds)
        self.lblText = wx.StaticText(self,-1,"Text")
        self.lblImage = wx.StaticText(self,-1,"Image")
        self.lblMode = wx.StaticText(self,-1,"Scan Mode")
        self.choTxtMode = wx.Choice(self,-1,choices=[])
        self.choImgMode = wx.Choice(self,-1,choices=[])
        self.lblRes = wx.StaticText(self,-1,"Resolution")
        self.choTxtRes = wx.Choice(self,-1,choices=[])
        self.choImgRes = wx.Choice(self,-1,choices=[])
        self.lblSize = wx.StaticText(self,-1,"Scan Size")
        self.choTxtSize = wx.Choice(self,-1,choices=[])
        self.choImgSize = wx.Choice(self,-1,choices=[])
        self.choImgSize.SetMinSize(CTRL_MIN_SIZE)
        self.btnOK = wx.Button(self, wx.ID_OK, "OK")
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Setup")

    def __do_layout(self):
        sizer_x = wx.BoxSizer(wx.VERTICAL)
        sizer_g = wx.GridSizer(6, 3, 4, 4)
        sizer_g.Add((20, 20), 0, wx.EXPAND, 0)
        sizer_g.Add(self.lblText, 0, wx.ALIGN_CENTER, 0)
        sizer_g.Add(self.lblImage, 0, wx.ALIGN_CENTER, 0)
        sizer_g.Add(self.lblMode, 0, wx.ALIGN_CENTER, 0)
        sizer_g.Add(self.choTxtMode, 0, wx.EXPAND, 0)
        sizer_g.Add(self.choImgMode, 0, wx.EXPAND, 0)
        sizer_g.Add(self.lblRes, 0, wx.ALIGN_CENTER, 0)
        sizer_g.Add(self.choTxtRes, 0, wx.EXPAND, 0)
        sizer_g.Add(self.choImgRes, 0, wx.EXPAND, 0)
        sizer_g.Add(self.lblSize, 0, wx.ALIGN_CENTER, 0)
        sizer_g.Add(self.choTxtSize, 0, wx.EXPAND, 0)
        sizer_g.Add(self.choImgSize, 0, wx.EXPAND, 0)
        sizer_g.Add((20, 20), 0, 0, 0)
        sizer_g.Add((20, 20), 0, 0, 0)
        sizer_g.Add((20, 20), 0, 0, 0)
        sizer_g.Add((20, 20), 0, 0, 0)
        sizer_g.Add(self.btnCancel, 0, wx.EXPAND, 0)
        sizer_g.Add(self.btnOK, 0, wx.EXPAND, 0)
        sizer_x.Add(sizer_g, 1, wx.ALL, 8)
        self.SetSizer(sizer_x)
        sizer_x.Fit(self)
        self.Layout()

    def FillChoiceLists(self, lstmode, lstres, lstsize):

        for x in lstmode:
            self.choTxtMode.Append(x)
            self.choImgMode.Append(x)

        for x in lstres:
            self.choTxtRes.Append(str(x) + ' dpi')
            self.choImgRes.Append(str(x) + ' dpi')

        for x in lstsize:
            self.choTxtSize.Append(x)
            self.choImgSize.Append(x)

    def SetSelections(self, txtPrms, imgPrms):

        if txtPrms is None:
            self.choTxtMode.SetSelection(0)
            self.choTxtRes.SetSelection(0)
            self.choTxtSize.SetSelection(0)
        else:
            self.choTxtMode.SetStringSelection(txtPrms['mode'])
            self.choTxtRes.SetStringSelection(str(txtPrms['res']) + ' dpi')
            self.choTxtSize.SetStringSelection(txtPrms['size'])

        if imgPrms is None:
            self.choImgMode.SetSelection(0)
            self.choImgRes.SetSelection(0)
            self.choImgSize.SetSelection(0)
        else:
            self.choImgMode.SetStringSelection(imgPrms['mode'])
            self.choImgRes.SetStringSelection(str(imgPrms['res']) + ' dpi')
            self.choImgSize.SetStringSelection(imgPrms['size'])

    def GetSelections(self):
        return (
            {
                'mode':self.choTxtMode.GetStringSelection(),
                'res':int(self.choTxtRes.GetStringSelection().partition(' ')[0]),
                'size':self.choTxtSize.GetStringSelection()
            },
            {
                'mode':self.choImgMode.GetStringSelection(),
                'res':int(self.choImgRes.GetStringSelection().partition(' ')[0]),
                'size':self.choImgSize.GetStringSelection()
            })


#--------1---------2---------3---------4---------5---------6---------7---------8
#
# CALIBRATION_DIALOG
#
class CalibDialog(wx.Dialog):
    def __init__(self, parent, img, *args, **kwds):
        wx.Dialog.__init__(self, parent, *args, **kwds)

        # calibration target in PIL image format
        self.img = img
        # create undithered image and reference image
        # panel for scanned image
        # panel for reference image

#--------1---------2---------3---------4---------5---------6---------7---------8
#
# IMAGE_PANEL
#
class ImagePanel(wx.Panel):

    def __init__(self, parent, info, *args, **kwds):
        wx.Panel.__init__(self, parent, *args, **kwds)

        # initial values and controls
        self.scale = 1.
        self.r = 0
        self.mode = 'none'
        self.wximg = None
        self.txtCoord = wx.TextCtrl(self, -1, '', style=wx.TE_READONLY)
        self.txtCoord.SetMinSize((160,28))
        self.sttInfo = wx.StaticText(self, -1, info)
        self.wndImage = wx.Window(self, -1, size=INITIAL_PANEL_SIZE)
        self.rband = RubberBand(drawingSurface = self.wndImage)
        self.rband.enabled = False

        # sizer
        sizer_x = wx.BoxSizer(wx.HORIZONTAL)
        sizer_x.Add(self.sttInfo, 1, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 2)
        sizer_x.Add(self.txtCoord, 0, wx.EXPAND|wx.ALL, 2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.wndImage, 1, wx.EXPAND|wx.ALL, 4)
        sizer.Add(sizer_x, 0, wx.EXPAND|wx.ALL, 2)
        self.SetSizer(sizer)

        # message binding
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.wndImage.Bind(wx.EVT_PAINT, self.OnPaint)
        self.wndImage.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

    #
    # from numpy array to wx.image
    #
    def SetNumpyData(self, data):
        if data is None:
            tmp = np.ones((INITIAL_PANEL_SIZE[1],INITIAL_PANEL_SIZE[0],3),
                    dtype=np.uint8) * 127

        elif data.shape[2] != 3:
            # grayscale or monochrome
            tmp = np.zeros((data.shape[0],data.shape[1],3),dtype=np.uint8)
            # the same data for all plane
            tmp[:,:,0] = data[:,:,0]
            tmp[:,:,1] = data[:,:,0]
            tmp[:,:,2] = data[:,:,0]
        else:
            # color
            tmp = data

        # convert to image
        self.wximg = wx.Image(tmp.shape[1],tmp.shape[0])
        self.wximg.SetData(tmp.tostring())
        # update panel
        self.Refresh()

    #
    # from PIL image to wx.image
    #
    def SetPilImage(self, data):
        if data is None:
            self.wximg = wx.Image(INITIAL_PANEL_SIZE[0],INITIAL_PANEL_SIZE[1])
        else:
            self.wximg = wx.Image(data.size[0],data.size[1])
            self.wximg.SetData(data.convert('RGB').tobytes())

        self.Refresh()

    #
    # start rubberband
    #
    def StartRBand(self):
        self.rband.reset()
        self.rband.enabled = True
        self.mode = 'rband'

    #
    # stop rubberband
    #
    def StopRBand(self):

        self.rband.reset()
        self.rband.enabled = False
        self.mode = 'none'

    def CopyRBand(self):
        # get rubberband extent
        ext = self.rband.getCurrentExtent()
        # trivial case
        if ext is None:
            return

        # convert the region into image space
        rect = wx.Rect(int(ext[0]/self.r+.5), int(ext[1]/self.r+.5),
                int((ext[2]-ext[0])/self.r+.5),int((ext[3]-ext[1])/self.r+.5))
        # create bitmap data object
        clipdata = wx.BitmapDataObject()
        crop = self.wximg.GetSubImage(rect)
        clipdata.SetBitmap(wx.Bitmap(crop))
        # copy to the clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipdata)
            wx.TheClipboard.Close()

    #
    # paint event handler
    #
    def OnPaint(self, evt=None):

        if self.wximg is None:
            return

        # use paint dc
        dc = wx.PaintDC(self.wndImage)
        # image size
        ix = self.wximg.GetWidth()
        iy = self.wximg.GetHeight()
        # screen size
        sx = dc.GetSize().GetWidth()
        sy = dc.GetSize().GetHeight()
        # scale factor
        r = min(float(sx)/ix, float(sy)/iy) * self.scale
        # resizing
        img = self.wximg.Scale(int(r * ix), int(r * iy), RESIZE_QUALITY)
        # create a bitmap from the image
        bitmap = wx.Bitmap(img)
        # draw bitmap
        if self.scale == 1:
            dc.DrawBitmap(bitmap,0,0)
        else:
            pos = self.wndImage.ScreenToClient(wx.GetMousePosition())
            dc.DrawBitmap(bitmap,pos[0]*(1-self.scale),pos[1]*(1-self.scale))

        # save the scale factor for later use
        self.r = r

        #evt.Skip()


    def OnMouseEvents(self, evt):

        if self.wximg is None:
            return

        if self.mode == 'rband':
            # pass the mouse event to rubberband class
            evt.Skip()

        elif self.mode == 'zoom':

            if evt.LeftUp():
                # release mouse event
                self.wndImage.ReleaseMouse()
                # return scale factor
                self.scale = 1.
                # return to nomal mode
                self.mode = 'none'
                # redraw
                self.Refresh()
            # refresh image
            elif evt.Dragging():
                # magnified image will be redrawn
                self.Refresh()

        elif self.mode == 'none':
            # show magnifier cursor
            self.SetCursor(wx.Cursor(wx.CURSOR_MAGNIFIER))

            # enter zoom mode
            if evt.LeftDown():
                # capture mouse event
                self.wndImage.CaptureMouse()
                # change scale factor
                self.scale = float(SCREEN_MAG)
                # enters zoom mode
                self.mode = 'zoom'
                # redraw
                self.Refresh()

            # RGB value display
            elif evt.Moving():
                pos = self.wndImage.ScreenToClient(wx.GetMousePosition())
                x = int(pos[0]/self.r+0.5)
                y = int(pos[1]/self.r+0.5)
                # cordinate can be out of the area momentarily
                try:
                    self.txtCoord.SetValue(
                        'R:{:03d}  G:{:03d}  B:{:03d}\t'.format(
                        self.wximg.GetRed(x,y),
                        self.wximg.GetGreen(x,y),
                        self.wximg.GetBlue(x,y)),)
                except:
                    # let us just do nothing
                    pass


#--------1---------2---------3---------4---------5---------6---------7---------8
#
# IMAGE_BOOK
#
class ImageBook(wx.Listbook):

    def __init__(self, parent):
        wx.Listbook.__init__(self, parent, -1, style = wx.LB_LEFT)

        # save parent handle for later use
        self.parent = parent
        # image list - placeholder
        self.imglist = wx.ImageList(THUMBNAIL_SIZE[0],THUMBNAIL_SIZE[1])
        # with a blank bitmap
        self.imglist.Add(wx.Bitmap(THUMBNAIL_SIZE[0],THUMBNAIL_SIZE[1]))
        # default image list
        self.AssignImageList(self.imglist)

        # data
        self.data = []
        # background image
        self.background = None

        # image panel
        # default dummy page but without thumbnail
        self.AddPage(ImagePanel(self, '', style=wx.BORDER_SUNKEN,
                size = INITIAL_PANEL_SIZE), '')

        # message binding
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)

    #
    # delete current selected page
    #
    def Delete(self):
        if len(self.data) == 0:
            return

        idx = self.GetSelection()
        # delete corresponding page however thumbnail remains
        self.DeletePage(idx)
        # and delete data
        self.data.pop(idx)
        # create empty page if all pages are deleted
        if self.GetPageCount() == 0:
            self.AddPage(ImagePanel(self, '', style=wx.BORDER_SUNKEN,
                    size = INITIAL_PANEL_SIZE), '')

    #
    # start rubberband
    #
    def StartRBand(self):
        self.GetPage(self.GetSelection()).StartRBand()

    #
    # stop rubberband
    #
    def StopRBand(self):
        self.GetPage(self.GetSelection()).CopyRBand()
        self.GetPage(self.GetSelection()).StopRBand()

    #
    # page change event handler
    #
    def OnPageChanged(self, evt=None):
        index = self.GetSelection()
        # image setting controls are in the parent frame
        self.parent.PutImgSettings(self.data[index]['settings'])

    #
    # add new data
    #
    def AddData(self, item):
        # process data: note that this is dict so it is referenced not copied
        self.ProcessData(item)
        # add thumbnail to the image list: note that imglist is ever increasing
        self.imglist.Add(item['icon'])
        # save the thumbnail index
        item['tidx'] = self.imglist.GetImageCount() - 1

        # check if this is the first page
        if len(self.data) == 0:
            # delete placeholder page
            self.DeleteAllPages()
            # posiiton of the insertion
            idx = 0

        else:
            # position of insertion
            idx = self.GetSelection() + 1

        # insert item into the list
        self.data.insert(idx, item)
        # insert page into the book
        self.InsertPage(idx, ImagePanel(self, item['info'],
            style=wx.BORDER_SUNKEN, size = INITIAL_PANEL_SIZE),'',
            imageId = item['tidx'])

        # select the page
        self.SetSelection(idx)
        # draw image on the page
        self.GetPage(idx).SetPilImage(item['res'])

    #
    # update image and thumbnail
    #
    def UpdateImage(self, index=None):
        if index is None:
            index = self.GetSelection()
        # reprocess data
        item = self.data[index]
        self.ProcessData(item)
        # replace the thumbnail
        self.imglist.Replace(item['tidx'], item['icon'])
        # replace the image
        self.GetPage(index).SetPilImage(item['res'])

    #
    # process data
    #
    def ProcessData(self, data):
        res = data['src'].copy()
        settings = data['settings']

        wx.BeginBusyCursor()

        # color correction
        if settings['co'] == 'None':
            pass
        # calibration
        elif settings['co'] == 'Calibration':
            res = ipc.ApplyCalibration(res, 'Color')
        # manual
        elif settings['co'] == 'Manual':
            # color blance
            if settings['cb'] != 1.0:
                res = ipc.AdjustColorBalance(res, settings['cb'])
        # white balance
        else:
            res = ipc.AdjustWhiteBalance(res, settings['co'])

        # gamma correction
        if settings['gm'] == 'None':
            pass
        # calibration
        elif settings['gm'] == 'Calibration':
            res = ipc.ApplyCalibration(res, 'Gamma')
        # manual
        elif settings['gm'] == 'Manual':
            # contrast
            if settings['ct'] != 1.0:
                res = ipc.AdjustContrast(res, settings['ct'])
            # brightness
            if settings['br'] != 1.0:
                res = ipc.AdjustBrightness(res, settings['br'])

        # image centering
        if settings['cn'] != 'None':
            # rectify image
            rect, (cx,cy) = ipc.GetRectifiedImage(res)

            if rect is not None:
                # clean image
                res.paste('white',(0,0,res.size[0]-1,res.size[1]-1))

                # find the coodinate for the rectified image
                if settings['cn'] == 'Horizontal':
                    dx = int((res.size[0] - rect.size[0])/2 + 0.5)
                    dy = int(cy - rect.size[1]/2 + 0.5)
                elif settings['cn'] == 'Vertical':
                    dx = int(cx - rect.size[0]/2 + 0.5)
                    dy = int((res.size[1] - rect.size[1])/2 + 0.5)
                else:
                    dx = int((res.size[0] - rect.size[0])/2 + 0.5)
                    dy = int((res.size[1] - rect.size[1])/2 + 0.5)

                # then paste
                res.paste(rect, (dx,dy))

        # sharpen
        if settings['sh'] == 'None':
            pass
        # manual
        elif settings['sh'] == 'Manual':
            # sharpness
            if settings['sn'] != 1.0:
                res = ipc.AdjustSharpness(res, settings['sn'])
        # others
        else:
            res = ipc.ApplyFilter(res, settings['sh'])

        # watermark
        if settings['wm'] != 'None':
            res = ipc.ApplyWatermark(res, settings['wm'])

        # background
        if settings['bk'] != 'None':
            # FIXME size must match
            res = res.convert('RGBA')
            bgnd = self.background.resize(res.size)

            # alpha composition
            res = Image.alpha_composite(res,bgnd)
            # return to RGB mode
            res = res.convert('RGB')

        # finally thumbnail
        wximg = wx.Image(THUMBNAIL_SIZE[0],THUMBNAIL_SIZE[1])
        wximg.SetData(res.resize(THUMBNAIL_SIZE).convert('RGB').tobytes())
        icon = wximg.ConvertToBitmap()

        wx.EndBusyCursor()

        # save it for later use
        data['icon'] = icon
        data['res'] = res

    #
    # update settings for the current data
    #
    def UpdateSettings(self, settings):
        index = self.GetSelection()
        self.data[index]['settings'] = settings
        # it is necessary to update the image
        self.UpdateImage(index)

    #
    # delete all data
    #
    def New(self):
        self.data = []
        self.DeleteAllPages()
        # create empty page
        self.AddPage(ImagePanel(self, '', style=wx.BORDER_SUNKEN,
                size = INITIAL_PANEL_SIZE), '')

    #
    # save data to disk file
    #
    def Save(self, fpath):

        if len(self.data) == 0:
            return

        # divide into file name and extension
        fname,sep,fext = fpath.rpartition('.')


        if len(self.data) == 1:

            # single page pdf
            if fext == 'pdf' or fext == 'PDF':

                if 'dpi' in self.data[0]:
                    self.data[0]['res'].save(fpath,
                            resolution = self.data[0]['dpi'][0])
                else:
                    self.data[0]['res'].save(fpath)

                return True

            # single page jpg
            elif fext == 'jpg' or fext == 'JPG':

                if 'dpi' in self.data[0]:
                    self.data[0]['res'].save(fpath, dpi=self.data[0]['dpi'],
                            quality = JPGQUALITY)
                else:
                    self.data[0]['res'].save(fpath, quality = JPGQUALITY)

                return True

            # single page png
            elif fext == 'png' or fext == 'PNG':

                if 'dpi' in self.data[0]:
                    self.data[0]['res'].save(fpath, dpi = self.data[0]['dpi'],
                            optimize = PNGOPTIMIZ)
                else:
                    self.data[0]['res'].save(fpath,
                            optimize = PNGOPTIMIZ)

                return True

            # single page any image
            else:
                # possibility of unsupported format
                try:
                    self.data[0]['res'].save(fpath)
                except:
                    return False
                else:
                    return True

        else:
            # create list of file names
            flist = [fname + '_{:d}'.format(i+1) + '.' + fext
                    for i in range(len(self.data))]

            # multiple page pdf
            if fext == 'pdf' or fext == 'PDF':

                for idx, x in enumerate(self.data):
                    if 'dpi' in x:
                        x['res'].save(flist[idx], resolution = x['dpi'][0])
                    else:
                        x['res'].save(flist[idx])

                # merge pdf if possible
                cmd = 'pdftk'
                for x in flist:
                    cmd = cmd + ' ' + x

                if os.system(cmd + ' cat output ' + fpath) == 0:
                    # on success, delete individual pdf files
                    for x in flist:
                        os.system('rm ' + x)

                return True

            # multiple jpg files
            elif fext == 'jpg' or fext == 'JPG':

                for idx, x in enumerate(self.data):
                    if 'dpi' in x:
                        x['res'].save(flist[idx], dpi = x['dpi'],
                                quality = JPGQUALITY)
                    else:
                        x['res'].save(flist[idx], quality = JPGQUALITY)

                return True

            # multiple png files
            elif fext == 'png' or fext == 'PNG':

                for idx, x in enumerate(self.data):
                    if 'dpi' in x:
                        x['res'].save(flist[idx], dpi = x['dpi'],
                                optimize = PNGOPTIMIZ)
                    else:
                        x['res'].save(flist[idx], optimize = PNGOPTIMIZ)

                return True

            # possibly unsupported files
            else:
                for idx, x in enumerate(self.data):
                    try:
                        x['res'].save(flist[idx])
                    except:
                        return False

                return True

    #
    # register background image
    #
    def SetBackground(self, img):
        self.background = img

#--------1---------2---------3---------4---------5---------6---------7---------8
#
#  MAIN_FRAME
#
class MyFrame(wx.Frame):

    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)

        # color scheme
        self.cscheme = color_schemes[COLOR_SCHEME]

        # toolbar
        self.toolbar = self.CreateToolBar(
                wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_HORZ_TEXT)

        # toolbar ids
        self.tidNew = wx.NewId()
        self.tidText = wx.NewId()
        self.tidImage = wx.NewId()
        self.tidDelete = wx.NewId()
        self.tidClip = wx.NewId()
        self.tidLoad = wx.NewId()
        self.tidSave = wx.NewId()
        self.tidSetup = wx.NewId()
        self.tidDevice = wx.NewId()
        # choice tool
        self.choDevice = wx.Choice(self.toolbar,self.tidDevice,choices=[])

        # statusbar
        self.status = self.CreateStatusBar()

        # image book
        self.lbkScan = ImageBook(self)

        # side bar
        self.pnlSide = wx.Panel(self, -1)
        # color correction
        self.sttColor = wx.StaticText(self.pnlSide, -1, 'Color Correction')
        self.sttColor.SetMinSize(CTRL_MIN_SIZE)
        #
        self.choColor = wx.Choice(self.pnlSide, -1,
                choices=['None','Calibration','Stretch','Grey World',
                'Retinex', 'Retinex Adjust','Max White','Manual'])
        self.choColor.SetMinSize(CTRL_MIN_SIZE)
        # color balance
        self.sttCbalance = wx.StaticText(self.pnlSide, -1, '\tColor Balance')
        self.spnCbalance = wx.SpinCtrlDouble(self.pnlSide, -1, '',
                min = 0, max = 2, initial = 1,inc = 0.1)
        # gamma correction
        self.sttGamma = wx.StaticText(self.pnlSide, -1, 'Gamma Correction')
        self.choGamma = wx.Choice(self.pnlSide, -1,
                choices=['None', 'Calibration', 'Manual'])
        # contrast
        self.sttContrast = wx.StaticText(self.pnlSide, -1, '\tContrast')
        self.spnContrast = wx.SpinCtrlDouble(self.pnlSide, -1, '',
                min = 0, max = 2, initial = 1,inc = 0.1)
        # brightness
        self.sttBrightness = wx.StaticText(self.pnlSide,-1,'\tBrightness')
        self.spnBrightness = wx.SpinCtrlDouble(self.pnlSide, -1, '',
                min = 0, max = 2, initial = 1,inc = 0.1)
        # image filtering - sharphen
        self.sttSharpen = wx.StaticText(self.pnlSide, -1, 'Sharpen')
        self.choSharpen = wx.Choice(self.pnlSide, -1,
                choices=['None', 'Detail', 'Anti-Halftone', 'Unsharpen',
                    'Manual'])
        # sharpness
        self.sttSharpness = wx.StaticText(self.pnlSide, -1, '\tSharpness')
        self.spnSharpness = wx.SpinCtrlDouble(self.pnlSide, -1, '',
                min = 0, max = 2, initial = 1,inc = 0.1)
        # rectification
        self.sttCentering = wx.StaticText(self.pnlSide, -1, 'Centering')
        self.choCentering = wx.Choice(self.pnlSide, -1,
                choices=['None', 'Horizontal', 'Vertical', 'Both'])
        # watermark
        self.sttWatermark = wx.StaticText(self.pnlSide, -1, 'Watermark')
        self.choWatermark = wx.Choice(self.pnlSide, -1,
                choices=['None', 'CONFIDENTIAL', 'Copyrighted', 'DRAFT',
                'Preview', 'Sample'])
        # background calibration
        self.sttBackground = wx.StaticText(self.pnlSide, -1, 'Background')
        self.choBackground = wx.Choice(self.pnlSide, -1,
                choices=['None', 'Select'])
        # calibration
        self.sttCalibration = wx.StaticText(self.pnlSide, -1, 'Calibration')
        self.btnMacbeth = wx.Button(self.pnlSide, -1, 'Macbeth Chart')

        self.__set_properties()
        self.__do_layout()
        self.__initialize()

        self.status.SetStatusText('Enumerating scanners... Please wait.')
        wx.CallAfter(self.EnumerateDevices)

    def __set_properties(self):

        self.SetTitle(PROGRAM_TITLE)
        self.choColor.SetSelection(0)
        self.sttCbalance.Disable()
        self.spnCbalance.Disable()
        self.choGamma.SetSelection(0)
        self.sttContrast.Disable()
        self.spnContrast.Disable()
        self.sttBrightness.Disable()
        self.spnBrightness.Disable()
        self.choSharpen.SetSelection(0)
        self.sttSharpness.Disable()
        self.spnSharpness.Disable()
        self.choCentering.SetSelection(0)
        self.choWatermark.SetSelection(0)
        self.choBackground.SetSelection(0)
        # FIXME: enable these when done
        self.sttCalibration.Disable()
        self.btnMacbeth.Disable()

    def __do_layout(self):

        # add to the toolbar
        acccol = self.cscheme['accent']
        self.toolbar.AddTool(self.tidNew, 'New',
                self.NewBitmap(acccol[0], ICON_NEW, wx.BITMAP_TYPE_PNG))
        self.toolbar.AddTool(self.tidText, 'Text',
                self.NewBitmap(acccol[1], ICON_TXT, wx.BITMAP_TYPE_PNG))
        self.toolbar.AddTool(self.tidImage, 'Image',
                self.NewBitmap(acccol[2], ICON_IMG, wx.BITMAP_TYPE_PNG))
        self.toolbar.AddTool(self.tidDelete, 'Delete',
                self.NewBitmap(acccol[3], ICON_CUT, wx.BITMAP_TYPE_PNG))
        self.toolbar.AddCheckTool(self.tidClip, 'Copy to Clipboard',
                self.NewBitmap(acccol[4], ICON_CRP, wx.BITMAP_TYPE_PNG))
        self.toolbar.AddTool(self.tidLoad, 'Load Image File',
                self.NewBitmap(acccol[5], ICON_ULD, wx.BITMAP_TYPE_PNG))
        self.toolbar.AddTool(self.tidSave, 'Save',
                self.NewBitmap(acccol[6], ICON_SAV, wx.BITMAP_TYPE_PNG))
        self.toolbar.AddTool(self.tidSetup, 'Setup',
                self.NewBitmap(acccol[7], ICON_SET, wx.BITMAP_TYPE_PNG))
        self.toolbar.AddStretchableSpace()
        self.toolbar.AddControl(self.choDevice)

        sizer_lhs = wx.BoxSizer(wx.VERTICAL)
        sizer_lhs.Add(self.lbkScan, 1, wx.ALL|wx.EXPAND, 4)

        sizer_g = wx.FlexGridSizer(12,2,8,8)

        sizer_g.Add(self.sttColor, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.choColor, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttCbalance, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.spnCbalance, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttGamma, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.choGamma, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttContrast, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.spnContrast, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttBrightness, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.spnBrightness, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttSharpen, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.choSharpen, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttSharpness, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.spnSharpness, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttCentering, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.choCentering, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttWatermark, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.choWatermark, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttBackground, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.choBackground, 0, wx.EXPAND, 0)

        sizer_g.Add(self.sttCalibration, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_g.Add(self.btnMacbeth, 0, wx.EXPAND, 0)
        self.pnlSide.SetSizer(sizer_g)

        sizer_rhs = wx.BoxSizer(wx.VERTICAL)
        sizer_rhs.Add(self.pnlSide, 0, wx.ALL|wx.EXPAND, 4)

        sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        sizer_main.Add(sizer_lhs, 1, wx.EXPAND, 0)
        sizer_main.Add(sizer_rhs, 0, wx.EXPAND, 0)

        self.SetSizer(sizer_main)
        sizer_main.Fit(self)
        # fix current rhs panel size
        sizer_rhs.SetMinSize(sizer_rhs.GetSize())
        # layout
        self.Layout()
        # centering
        self.Center()

    def __initialize(self):
        # set color scheme
        fgnd = self.cscheme['fgnd'][-1]
        bgnd = self.cscheme['bgnd'][0]
        # for main frame
        self.SetBackgroundColour(bgnd)
        self.SetForegroundColour(fgnd)
        # for image book
        self.lbkScan.SetBackgroundColour(bgnd)
        self.lbkScan.SetForegroundColour(fgnd)
        # for side bar
        self.pnlSide.SetBackgroundColour(bgnd)
        self.pnlSide.SetForegroundColour(fgnd)

        # initialize scanner
        self.scanner = Scanner()
        # image book get focus
        self.lbkScan.SetFocus()
        # clear dirty flag
        self.dirty = False
        # default scan parameters
        self.txtScanPrms = {
                'mode':DEFAULT_TXT_MODE,
                'res':DEFAULT_TXT_RES,
                'size':DEFAULT_TXT_SIZE}
        self.imgScanPrms = {
                'mode':DEFAULT_IMG_MODE,
                'res':DEFAULT_IMG_RES,
                'size':DEFAULT_IMG_SIZE}
        # disable controls
        self.EnableControls('Init')

        # MAIN_EVENT_HANDLERS
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        # image settings - color
        self.Bind(wx.EVT_CHOICE, self.OnImgSettings, self.choColor)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnImgSettings, self.spnCbalance)
        # image settings - gamma
        self.Bind(wx.EVT_CHOICE, self.OnImgSettings, self.choGamma)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnImgSettings, self.spnContrast)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnImgSettings, self.spnBrightness)
        # image setting - filtering
        self.Bind(wx.EVT_CHOICE, self.OnImgSettings, self.choSharpen)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnImgSettings, self.spnSharpness)
        # image setting - others
        self.Bind(wx.EVT_CHOICE, self.OnImgSettings, self.choCentering)
        self.Bind(wx.EVT_CHOICE, self.OnImgSettings, self.choWatermark)
        self.Bind(wx.EVT_CHOICE, self.OnImgSettings, self.choBackground)
        # calibration buttons
        self.Bind(wx.EVT_BUTTON, self.OnMacbethScan, self.btnMacbeth)
        # toolbar
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.tidNew)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.tidText)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.tidImage)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.tidClip)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.tidLoad)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.tidDelete)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.tidSave)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.tidSetup)
        self.Bind(wx.EVT_CHOICE, self.OnSelectDevice, id=self.tidDevice)

    #
    # close event handler
    #
    def OnClose(self, evt=None):

        if self.dirty:
            if wx.MessageBox('Data will be lost... Continue?',
                    'Confirm', wx.YES_NO) == wx.NO:
                return

        if self.scanner is not None:
            self.scanner.Close()

        evt.Skip()

    #
    # scan Macbeth chart and open calibration dialog
    #
    def OnMacbethScan(self, evt):
        if self.scanner is None:
            return
        wx.BeginBusyCursor()
        # set scanner settings for calibration scan
        img = self.scanner.ScanImage()
        # get rectified image
        rect, (cx,cy) = ipc.GetRectifiedImage(img)
        # create calibration dialog instance
        dlg = CalibDialog(self, rect)

        if dlg.ShowModal() == wx.ID_OK:
            # save calibration data
            pass

        dlg.Destroy()

        # TODO: return scanner setting
        wx.EndBusyCursor()

    #
    # image settings changed
    #
    def OnImgSettings(self, evt=None):

        # color correction
        if self.choColor.GetStringSelection() == 'Manual':
            self.sttCbalance.Enable()
            self.spnCbalance.Enable()
        else:
            self.sttCbalance.Disable()
            self.spnCbalance.Disable()
        # gamma correction
        if self.choGamma.GetStringSelection() == 'Manual':
            self.sttContrast.Enable()
            self.spnContrast.Enable()
            self.sttBrightness.Enable()
            self.spnBrightness.Enable()
        else:
            self.sttContrast.Disable()
            self.spnContrast.Disable()
            self.sttBrightness.Disable()
            self.spnBrightness.Disable()
        # image filtering
        if self.choSharpen.GetStringSelection() == 'Manual':
            self.sttSharpness.Enable()
            self.spnSharpness.Enable()
        else:
            self.sttSharpness.Disable()
            self.spnSharpness.Disable()

        # background image selection
        if self.choBackground.GetStringSelection() == 'Select':
            dlg = ib.ImageDialog(self, IMAGE_DIR)
            dlg.Centre()

            if dlg.ShowModal() == wx.ID_OK:
                fpath = dlg.GetFile()
                img, res = self.LoadFile(fpath, True)

                if img is not None:
                    # set background image
                    self.lbkScan.SetBackground(img)

                    # insert filename to the choice box
                    fname = fpath.rpartition('/')[2].rpartition('.')[0]
                    if self.choBackground.GetCount() == 2:
                        self.choBackground.Insert(fname,1)
                    else:
                        self.choBackground.SetString(1,fname)
                    self.choBackground.SetSelection(1)

                else:
                    self.status.SetStatusText('Failed to load the image file.')
                    self.choBackground.SetSelection(0)
            else:
                self.choBackground.SetSelection(0)

            dlg.Destroy()

        # update settings for the selected page
        if len(self.lbkScan.data):
            self.lbkScan.UpdateSettings(self.GetImgSettings())

    #
    # new device selected from the choice box
    #
    def OnSelectDevice(self, evt=None):

        for idx, x in enumerate(self.scanner.GetDevList()):

            if x[2] == self.choDevice.GetStringSelection():
                self.status.SetStatusText('Opening ' + x[2])

                wx.BeginBusyCursor()

                # open the device
                if self.scanner.Open(idx):
                    # opened device name
                    self.status.SetStatusText(x[2] + ' is ready')
                    # finally enable buttons
                    self.EnableControls('Normal')

                else:
                    wx.MessageBox('Failed to open the scanner')

                wx.EndBusyCursor()
                # break anyway
                break

    #
    # toolbar handler
    #
    def OnToolClick(self, evt):
        tid = evt.GetId()

        # new file
        if tid == self.tidNew:
            if self.dirty:
                if wx.MessageBox('Data will be lost... Continue?',
                        'Confirm', wx.YES_NO) == wx.NO:
                    return
            self.lbkScan.New()
            self.dirty = False

        # text mode scan
        elif tid == self.tidText:
            self.ScanPage('Text')

        # image mode scan
        elif tid == self.tidImage:
            self.ScanPage('Image')

        # copy to clipboard
        elif tid == self.tidClip:
            if self.toolbar.GetToolState(tid):
                self.EnableControls('RBand')
                self.status.SetStatusText('Select region to copy')
                self.lbkScan.StartRBand()
            else:
                self.status.SetStatusText('Image copied to clipboard')
                self.lbkScan.StopRBand()
                self.EnableControls('Normal')

        # load image file
        elif tid == self.tidLoad:
            dlg = ib.ImageDialog(self, IMAGE_DIR)
            dlg.Centre()

            # image with certain margin around
            if dlg.ShowModal() == wx.ID_OK:

                fpath = dlg.GetFile()
                img, res = self.LoadFile(fpath)

                if img is not None:
                    self.lbkScan.AddData({
                        'src':img,
                        'info':fpath.rpartition('/')[2].rpartition('.')[0],
                        'dpi':(res,res),
                        'settings':self.GetImgSettings()})
                    self.dirty = True
                else:
                    self.status.SetStatusText('Failed to load the image file.')

            dlg.Destroy()

        # delete the page
        elif tid == self.tidDelete:
            self.lbkScan.Delete()

        # save data
        elif tid == self.tidSave:
            self.SaveFile()

        # change default scan mode
        elif tid == self.tidSetup:
            dlg = SetupDialog(self)
            dlg.FillChoiceLists(
                    self.scanner.GetModes(),
                    self.scanner.GetResolutions(),
                    self.scanner.GetScanAreas())
            dlg.SetSelections(self.txtScanPrms, self.imgScanPrms)

            if dlg.ShowModal() == wx.ID_OK:
                (self.txtScanPrms, self.imgScanPrms) = dlg.GetSelections()

            dlg.Destroy()

    # MAIN_SUPPORT_FUNCTIONS
    #
    # scan page
    #
    def ScanPage(self, target='Image'):

        if self.scanner is None:
            return

        if target == 'Text':
            mode = self.txtScanPrms['mode']
            res = self.txtScanPrms['res']
            size = self.txtScanPrms['size']
        elif target == 'Image':
            mode = self.imgScanPrms['mode']
            res = self.imgScanPrms['res']
            size = self.imgScanPrms['size']
        else:
            return
        # setup the scanner first
        self.scanner.SetMode(mode)
        self.scanner.SetScanArea(size)
        self.scanner.SetResolution(res)

        # save PIL image with current scan conditions and image settings
        wx.BeginBusyCursor()
        self.lbkScan.AddData({
            'src':self.scanner.ScanImage(),
            'info':' {:s} - {:d} dpi - {:s} '.format(mode, res, size),
            'dpi':(self.scanner.GetResolution(),self.scanner.GetResolution()),
            'settings':self.GetImgSettings()})
        wx.EndBusyCursor()
        self.dirty = True

    #
    # save data to file(s)
    #
    def SaveFile(self):

        dlg = wx.FileDialog(self, 'Save data','','',
                SAVEFILETYPE, wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        dlg.SetDirectory(IMAGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            if self.lbkScan.Save(dlg.GetPath()) == True:
                self.dirty = False
            else:
                wx.MessageBox('Unsupported file format')

        dlg.Destroy()

    #
    # load image from file
    #
    def LoadFile(self, fpath, background = False):

        try:
            src = Image.open(fpath)
        except:
            return None, None

        if src.width > src.height:
            src = src.rotate(90,expand=1)

        # insert alpha channel with
        if background:
            # convert to RGBA
            img = src.convert("RGBA")
            # extract data
            data = list(img.getdata())
            for idx,pxl in enumerate(data):
                if (pxl[0] > ALPHA_THOLD and pxl[1] > ALPHA_THOLD and
                        pxl[2] > ALPHA_THOLD):
                    # clear alpha channel valu
                    data[idx] = (pxl[0],pxl[1],pxl[2],ALPHA_BGND)
                else:
                    # set alpha channel value
                    data[idx] = (pxl[0],pxl[1],pxl[2],ALPHA_FGND)

            # reassemble
            img.putdata(data)

            return img, None

        else:
            # target resolution
            ppi = self.imgScanPrms['res']
            # target paper size
            scan_area = self.imgScanPrms['size']

            # paper size in inches
            if 'A4' in scan_area:
                paper_inch = (8.27, 11.69)
            elif 'A5' in scan_area:
                paper_inch = (5.83, 8.27)
            elif 'B5' in scan_area:
                paper_inch = (6.9, 9.8)
            elif 'Executive' in scan_area:
                paper_inch = (7.0, 10.0)
            else:
                paper_inch = (8.5, 11.0)

            # paper size in pixels
            paper_pxl = (int(paper_inch[0] * ppi), int(paper_inch[1]*ppi))

            # white background
            img = Image.new('RGB', paper_pxl, (255,255,255))

            # resizing ratio
            ratio = min(paper_pxl[0]/float(src.width),
                    paper_pxl[1]/float(src.height))

            # resize source without changing the aspect ratio
            src = src.resize((int(ratio*src.width),int(ratio*src.height)),
                    resample = Image.ANTIALIAS)

            # compute margin
            side_margin = (img.width - src.width)//2
            top_margin = (img.height - src.height)//2
            # paste the source into the white background
            img.paste(src,(side_margin, top_margin))

        return img, ppi

    #
    # get image settings from the controls
    #
    def GetImgSettings(self):
        return {'co':self.choColor.GetStringSelection(),
                'cb':self.spnCbalance.GetValue(),
                'gm':self.choGamma.GetStringSelection(),
                'ct':self.spnContrast.GetValue(),
                'br':self.spnBrightness.GetValue(),
                'sh':self.choSharpen.GetStringSelection(),
                'sn':self.spnSharpness.GetValue(),
                'cn':self.choCentering.GetStringSelection(),
                'wm':self.choWatermark.GetStringSelection(),
                'bk':self.choBackground.GetStringSelection()}

    #
    # put image settings to the controls
    #
    def PutImgSettings(self, settings):

        self.choColor.SetStringSelection(settings['co'])
        self.spnCbalance.SetValue(settings['cb'])
        self.choGamma.SetStringSelection(settings['gm'])
        self.spnContrast.SetValue(settings['ct'])
        self.spnBrightness.SetValue(settings['br'])
        self.choSharpen.SetStringSelection(settings['sh'])
        self.spnSharpness.SetValue(settings['sn'])
        self.choCentering.SetStringSelection(settings['cn'])
        self.choWatermark.SetStringSelection(settings['wm'])

        if settings['co'] == 'Manual':
            self.spnCbalance.Enable()
        else:
            self.spnCbalance.Disable()

        if settings['gm'] == 'Manual':
            self.spnContrast.Enable()
            self.spnBrightness.Enable()
        else:
            self.spnContrast.Disable()
            self.spnBrightness.Disable()

        if settings['sh'] == 'Manual':
            self.spnSharpness.Enable()
        else:
            self.spnSharpness.Disable()

        if settings['bk'] == 'None':
            self.choBackground.SetSelection(0)
        else:
            self.choBackground.SetSelection(1)

    #
    # enable / disable controls
    #
    def EnableControls(self, mode = 'Normal'):

        if mode == 'Init':
            # disable toolbar
            self.toolbar.Disable()
            # disable sidebar
            self.pnlSide.Disable()

        elif mode == 'Select':
            # enable toolbar
            self.toolbar.Enable()
            # disable sidebar
            self.pnlSide.Disable()

        elif mode == 'Normal':
            # enable toolbar
            self.toolbar.Enable()
            # enable sidebar
            self.pnlSide.Enable()

        elif mode == 'RBand':
            # enable toolbar
            self.toolbar.Enable()
            # disable sidebar
            self.pnlSide.Disable()

    #
    # enumerate scanner devices
    #
    def EnumerateDevices(self):

        # enumerate devices
        wx.BeginBusyCursor()
        devlist = self.scanner.GetDevList()
        wx.EndBusyCursor()

        if len(devlist) == 0:
            wx.MessageBox('No scanner found...')

        else:
            # fill the device choice box with the names
            for x in devlist:
                self.choDevice.Append(x[2])

            if len(devlist) == 1:
                # connect to the first scanner on the list
                self.choDevice.SetSelection(0)
                self.OnSelectDevice()
            else:
                self.status.SetStatusText('Select a scanner.')
                self.EnableControls('Select')

    #
    # create a bitmap from the image file
    #
    def NewBitmap(self, color, fname, ftype):
        img = wx.Image(fname, ftype)
        img.Replace(0,0,0,color[0],color[1],color[2])

        return wx.Bitmap(img)

#--------1---------2---------3---------4---------5---------6---------7---------8
if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(None, -1, "")
    frame.Show()
    app.MainLoop()
#--------1---------2---------3---------4---------5---------6---------7---------8

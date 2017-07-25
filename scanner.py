#!/usr/bin/env python3
#
# This class provides abstraction layer to the python-sane
#


import sane

class Scanner:

    def __init__(self):
        # initialize the sane
        sane.init()
        self.device = None
        self.devlist = None

    #
    # enumeration of sane devices in the syatem
    # this takes time
    #
    def GetDevList(self):
        if self.devlist is None:
            self.devlist = sane.get_devices()

        return self.devlist

    #
    # open a device by index
    #
    def Open(self, idx):

        # out of index
        if idx < 0 or idx >= len(self.devlist):
            self.device = None
            return False

        try:
            self.device = sane.open(self.devlist[idx][0])
        except:
            self.device = None
            return False
        else:
            self.devname = self.devlist[idx][2]
            # retrieve option list
            self.options = self.device.get_options()
            # mode: must be exist in the list
            for item in self.options:
                if item[1] == 'mode':
                    self.modes = item[-1]
            # resolution: must be exist in the list
            for item in self.options:
                if item[1] == 'resolution':
                    self.resolutions = item[-1]
            # scan area:
            self.areas = ['Letter', 'Legal', 'A4', 'A5', 'A6']
            return True

    #
    # device must be closed before opening others
    #
    def Close(self):
        if self.device is not None:
            self.device.close()

    #
    # scan an image from the scanner
    #
    def ScanImage(self):
        if self.device is None:
            return None

        self.device.start()
        return self.device.snap()

    #
    # return device name
    #
    def GetName(self):
        if self.device is None:
            return None
        else:
            return self.devname

    #
    # get list of modes supported by the scanner
    #
    def GetModes(self):
        if self.device is None:
            return None
        else:
            return self.modes

    #
    # get mode currently selected
    #
    def GetMode(self):
        if self.device is None:
            return None
        else:
            return self.device.mode

    #
    # set scan mode
    #
    def SetMode(self, mode):
        if self.device is None:
            return False
        else:
            self.device.mode = mode
            return True

    #
    # get list of scan areas supported by the scanner
    #
    def GetScanAreas(self):
        if self.device is None:
            return None
        else:
            return self.areas

    def GetScanArea(self):
        if self.device is None:
            return None
        else:
            return self.device.area

    def SetScanArea(self, area):
        if self.device is None:
            return False
        else:
            self.device.tl_x = 0
            self.device.tl_y = 0
            if area == 'A4' or area == 'a4':
                self.device.br_x = 210
                self.device.br_y = 297
            elif area == 'A5' or area == 'a5':
                self.device.br_x = 148
                self.device.br_y = 210
            elif area == 'A6' or area == 'a6':
                self.device.br_x = 105
                self.device.br_y = 148
            elif area == 'Legal' or area == 'legal':
                self.device.br_x = 216
                self.device.br_y = 356
            else:
                self.device.br_x = 216
                self.device.br_y = 279
            return True

    def GetResolutions(self):
        if self.device is None:
            return None
        else:
            return self.resolutions

    def GetResolution(self):
        if self.device is None:
            return None
        else:
            return self.device.resolution

    def SetResolution(self, res):
        if self.device is None:
            return None
        else:
            self.device.resolution = res
            return True

    def GetOptions(self):
        if self.device is None:
            return None
        else:
            return self.options

if __name__=='__main__':

    print('Initialization -------------------------------')
    myscanner = Scanner()
    print('DevList: ', myscanner.GetDevList())
    print('Opening the first one on the list', myscanner.Open(0))
    print('Name:', myscanner.GetName())
    print('Modes:', myscanner.GetModes())
    print('Scan Areas:', myscanner.GetScanAreas())
    print('Resolutions:', myscanner.GetResolutions())
    print()
    print('Available Options ----------------------------')
    for item in myscanner.GetOptions():
        print('\t', item[1], item[-1])
    print()
    print('Current Settings -----------------------------')
    print('Current Mode:', myscanner.GetMode())
    print('Current Scan Area:', myscanner.GetScanArea())
    print('Current Resolution:', myscanner.GetResolution())
    print()
    print('New Settings: choose the last settings -------------')
    myscanner.SetMode(myscanner.GetModes()[-1])
    myscanner.SetScanArea(myscanner.GetScanAreas()[-1])
    myscanner.SetResolution(myscanner.GetResolutions()[-1])
    print('New Mode:', myscanner.GetMode())
    print('New Scan Area:', myscanner.GetScanArea())
    print('New Resolution:', myscanner.GetResolution())
    print()
    print('Closing the scanner -------------------------------')
    myscanner.Close()

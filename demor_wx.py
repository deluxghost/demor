# -*- coding: utf-8 -*-
import os

import pythoncom
import wx
import wx.xrc
from win32com.shell import shell

import demor
import tf2dem


class Demor(wx.Frame):

    demo_file = None
    tf = ''

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Demor", pos=wx.DefaultPosition, size=wx.Size(360,240), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        fileDrop = FileDrop(self)
        self.SetDropTarget(fileDrop)
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        FileSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.FileLabel = wx.StaticText(self, wx.ID_ANY, "Demo: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.FileLabel.Wrap(-1)
        FileSizer.Add(self.FileLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.FilePicker = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, "Select Demo", "Demo (*.dem)|*.dem", wx.DefaultPosition, wx.Size(-1,-1), wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST|wx.FLP_OPEN)
        FileSizer.Add(self.FilePicker, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        MainSizer.Add(FileSizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        HostSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HostText = wx.StaticText(self, wx.ID_ANY, "Host: None", wx.DefaultPosition, wx.DefaultSize, 0)
        self.HostText.Wrap(-1)
        HostSizer.Add(self.HostText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        MainSizer.Add(HostSizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        MapSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.MapText = wx.StaticText(self, wx.ID_ANY, "Map: None", wx.DefaultPosition, wx.DefaultSize, 0)
        self.MapText.Wrap(-1)
        MapSizer.Add(self.MapText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        MainSizer.Add(MapSizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        TicksSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.TicksText = wx.StaticText(self, wx.ID_ANY, "Ticks: None", wx.DefaultPosition, wx.DefaultSize, 0)
        self.TicksText.Wrap(-1)
        TicksSizer.Add(self.TicksText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        MainSizer.Add(TicksSizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        ButtonSizer.Add((0, 0), 1, wx.EXPAND, 5)
        self.SaveButton = wx.Button(self, wx.ID_ANY, "Save Replay", wx.DefaultPosition, wx.DefaultSize, 0)
        self.SaveButton.Enable(False)
        ButtonSizer.Add(self.SaveButton, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        MainSizer.Add(ButtonSizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        self.SetSizer(MainSizer)
        self.Layout()
        self.Centre(wx.BOTH)
        self.FilePicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnFileChanged)
        self.SaveButton.Bind(wx.EVT_BUTTON, self.OnSaveReplay)

    def __del__(self):
        pass

    def DemoLoaded(self):
        path = self.FilePicker.GetPath()
        if not os.path.isfile(path):
            self.ClearDemo()
            return False
        try:
            self.demo_file = tf2dem.Demo(path)
            self.SaveButton.Enable(True)
            self.HostText.Label = 'Host: {}'.format(self.demo_file.host_name)
            self.MapText.Label = 'Map: {}'.format(self.demo_file.map_name)
            self.TicksText.Label = 'Ticks: {}'.format(self.demo_file.ticks)
            return True
        except tf2dem.NotDemoError:
            self.ClearDemo()
        except:
            self.ClearDemo()
        return False

    def ClearDemo(self):
        self.demo_file = None
        self.SaveButton.Enable(False)
        self.HostText.Label = 'Host: None'
        self.MapText.Label = 'Map: None'
        self.TicksText.Label = 'Ticks: None'

    def OnFileChanged(self, event):
        self.DemoLoaded()

    def OnSaveReplay(self, event):
        stat = self.DemoLoaded()
        if not stat:
            return
        dlg = wx.TextEntryDialog(self, 'Enter the title of your replay','Replay Title')
        dlg.SetValue(os.path.splitext(self.demo_file.base_name)[0])
        if dlg.ShowModal() != wx.ID_OK:
            return
        title = dlg.GetValue()
        dlg.Destroy()
        stat = self.DemoLoaded()
        if not stat:
            return
        replay_dir = os.path.join(self.tf, r'replay\client\replays')
        if not os.path.exists(replay_dir):
            os.makedirs(replay_dir)
        src = os.path.abspath(self.demo_file.file_name)
        dest = os.path.abspath(os.path.join(replay_dir, self.demo_file.base_name))
        if src.lower() != dest.lower():
            pfo = pythoncom.CoCreateInstance(shell.CLSID_FileOperation, None, pythoncom.CLSCTX_ALL, shell.IID_IFileOperation)
            src_s = shell.SHCreateItemFromParsingName(src, None, shell.IID_IShellItem)
            dest_s = shell.SHCreateItemFromParsingName(replay_dir, None, shell.IID_IShellItem)
            pfo.CopyItem(src_s, dest_s)
            pfo.PerformOperations()
        rid = demor.last_replay(self.tf) + 1
        demor.write_replay(self.tf, rid, self.demo_file, title)
        dlg = wx.MessageDialog(self, 'New replay clip saved.\nLaunch or restart tf2 to check your replay.', 'Success', wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

class FileDrop(wx.FileDropTarget):

    def __init__(self, frame):
        wx.FileDropTarget.__init__(self)
        self.frame = frame

    def OnDropFiles(self, x, y, filePath):
        self.frame.FilePicker.SetPath(filePath[0])
        self.frame.DemoLoaded()
        return True

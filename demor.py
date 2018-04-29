# -*- coding: utf-8 -*-
import glob
import os
import re
import shutil
import sys
import winreg

import wx

import demor_wx
import tf2dem


def steam_path():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam') as handle:
            return winreg.QueryValueEx(handle, 'SteamPath')[0].replace('/', '\\')
    except:
        return None

def game_library(steam_path):
    vdf_pat = re.compile(r'^\s*"\d+"\s*".+"\s*')
    libs = [steam_path]
    libinfo = os.path.join(steam_path, r'steamapps\libraryfolders.vdf')
    try:
        with open(libinfo, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if vdf_pat.match(line):
                    libs.append(line.split()[1].strip('"').replace('\\\\', '\\'))
    except:
        return [steam_path]
    return libs

def find_tf2(libs):
    for lib in libs:
        find_acf = os.path.join(lib, r'steamapps\appmanifest_440.acf')
        if os.path.isfile(find_acf):
            tf_root = os.path.join(lib, r'steamapps\common\Team Fortress 2\tf')
            if os.path.isdir(tf_root):
                return tf_root
    return None

def last_replay(tf):
    file_pat = re.compile(r'replay_\d+\.dmx')
    replay_dir = os.path.join(tf, r'replay\client\replays')
    if not os.path.exists(replay_dir):
        os.makedirs(replay_dir)
    replays = glob.glob(os.path.join(replay_dir, 'replay_*.dmx'))
    replays = list(map(lambda r: os.path.basename(r), replays))
    replays = [r for r in replays if file_pat.match(r)]
    replays = list(map(lambda r: int(r.replace('replay_', '').replace('.dmx', '')), replays))
    replays.append(0)
    return max(replays)

def write_replay(tf, rid, dem, title, overwrite=False):
    replay_dir = os.path.join(tf, r'replay\client\replays')
    if not os.path.exists(replay_dir):
        os.makedirs(replay_dir)
    replay_dmx = os.path.join(replay_dir, 'replay_{}.dmx'.format(rid))
    if not overwrite and os.path.isfile(replay_dmx):
        raise FileExistsError
    dmx = '\n'.join((
        '"replay_{0}"',
        '{{',
        '	"handle"	"{0}"',
        '	"map"	"{1}"',
        '	"complete"	"1"',
        '	"title"	"{2}"',
        '	"recon_filename"	"{3}"',
        '}}'
    )).format(rid, dem.map_name, title, dem.base_name)
    with open(replay_dmx, 'w', encoding='utf-8') as f:
        f.write(dmx)

def copy_dem(tf, dem, overwrite=False):
    replay_dir = os.path.join(tf, r'replay\client\replays')
    if not os.path.exists(replay_dir):
        os.makedirs(replay_dir)
    src = os.path.normpath(dem.file_name)
    dest = os.path.normpath(os.path.join(replay_dir, dem.base_name))
    if src.lower() == dest.lower():
        return
    if not overwrite and os.path.isfile(dest):
        raise FileExistsError
    shutil.copyfile(src, dest)

def cli_main():
    steam = steam_path()
    if not steam:
        print('Cannot find Steam path.')
        steam = input('Input Steam path manualy: ')
        if not os.path.isdir(steam):
            print('Invalid path. Abort.')
            sys.exit(1)
    libs = game_library(steam)
    if not libs:
        print('Cannot find any Steam game library. Abort.')
        sys.exit(1)
    tf = find_tf2(libs)
    if not tf:
        print('Cannot find tf2 directory. Abort.')
        sys.exit(1)
    demo_file = input('Input demo file: ').strip('"')
    if not os.path.isfile(demo_file):
        print('File not found. Abort.')
        sys.exit(1)
    try:
        dem = tf2dem.Demo(demo_file)
    except tf2dem.NotDemoError:
        print('Invalid demo file. Abort.')
        sys.exit(1)
    print('Copying demo...')
    try:
        copy_dem(tf, dem)
    except FileExistsError:
        ow = input('Demo file already exists, overwrite(y/n)? ')
        if ow == 'y' or ow == 'Y':
            print('Still copying...')
            copy_dem(tf, dem, True)
        else:
            sys.exit(0)
    title = input('Replay title: ')
    rid = last_replay(tf) + 1
    write_replay(tf, rid, dem, title)
    print('Done. Launch or restart tf2 to check your replay.')

if __name__ == '__main__':
    if 'cli' in sys.argv[1:]:
        cli_main()
    else:
        app = wx.App(False)
        frame = demor_wx.Demor(None)
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("demor.ico", wx.BITMAP_TYPE_ANY))
        frame.SetIcon(icon)
        frame.Show(True)
        steam = steam_path()
        if not steam:
            dlg = wx.MessageDialog(frame, 'Cannot find Steam path. Abort.', 'Error', wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            sys.exit(1)
        libs = game_library(steam)
        if not libs:
            dlg = wx.MessageDialog(frame, 'Cannot find any Steam game library. Abort.', 'Error', wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            sys.exit(1)
        tf = find_tf2(libs)
        if not tf:
            dlg = wx.MessageDialog(frame, 'Cannot find tf2 directory. Abort.', 'Error', wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            sys.exit(1)
        frame.tf = tf
        app.MainLoop()

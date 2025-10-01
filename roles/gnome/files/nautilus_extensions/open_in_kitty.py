#!/usr/bin/env python3

from gi.repository import Nautilus, GObject
import subprocess


class OpenInKittyMenuProvider(GObject.GObject, Nautilus.MenuProvider):
  def __init__(self):
    pass

  def get_menu_item(self, name, folder):
    item = Nautilus.MenuItem(
        name=f'OpenInKittyExtension::{name}',
        label='Open in Kitty'
    )
    item.connect('activate', self.open_in_kitty, folder)
    return item

  def get_file_items(self, files):
    if len(files) != 1 or not files[0].is_directory():
      return []

    return [self.get_menu_item('file', files[0])]

  def get_background_items(self, folder):
    item = Nautilus.MenuItem(
        name='OpenInKittyExtension::background',
        label='Open in Kitty'
    )
    return [self.get_menu_item('background', folder)]

  def open_in_kitty(self, menu, folder):
    path = folder.get_location().get_path()
    subprocess.Popen(['kitty', path])

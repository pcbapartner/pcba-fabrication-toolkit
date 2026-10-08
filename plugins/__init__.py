"""PCBA Partner Fabrication Toolkit - KiCad action plugin (GPL-3.0-or-later)."""

import os

import pcbnew
import wx

from . import pcbapartner_export as core


class PCBAPartnerToolkit(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "PCBA Partner Fabrication Toolkit"
        self.category = "Fabrication outputs"
        self.description = "Export Gerber/drill ZIP, BOM, CPL and a pre-flight report for PCB assembly"
        self.show_toolbar_button = True
        icon = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.isfile(icon):
            self.icon_file_name = icon

    def Run(self):
        board = pcbnew.GetBoard()
        path = board.GetFileName() if board else ""
        if not path:
            wx.MessageBox("Save the board first.", "PCBA Partner", wx.OK | wx.ICON_WARNING)
            return
        if hasattr(board, "IsModified") and board.IsModified():
            if wx.MessageBox("The board has unsaved changes. Exports use the saved file.\n"
                             "Continue anyway?", "PCBA Partner",
                             wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
                return
        busy = wx.BusyInfo("Exporting assembly package...")
        try:
            res = core.run_export(path)
        except core.ExportError as e:
            del busy
            wx.MessageBox(str(e), "PCBA Partner - export failed", wx.OK | wx.ICON_ERROR)
            return
        del busy

        errors = [m for lvl, m in res["issues"] if lvl == "ERROR"]
        warns = [m for lvl, m in res["issues"] if lvl == "WARN"]
        summary = ("Package written to:\n%s\n\nCopper layers: %d   Placed parts: %d\n"
                   "Errors: %d   Warnings: %d\n\nSee the _preflight.txt file for details.") % (
            res["out_dir"], res["copper_layers"], res["parts"], len(errors), len(warns))
        wx.MessageBox(summary, "PCBA Partner Fabrication Toolkit",
                      wx.OK | (wx.ICON_WARNING if errors or warns else wx.ICON_INFORMATION))
        _open_folder(res["out_dir"])


def _open_folder(path):
    try:
        wx.LaunchDefaultApplication(path)
    except Exception:
        pass


PCBAPartnerToolkit().register()

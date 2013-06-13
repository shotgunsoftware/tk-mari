"""
Copyright (c) 2013 Shotgun Software, Inc
----------------------------------------------------

Custom columns from Shotgun.  Just a stub for future functionality right now.
"""
import hiero.ui

class CustomSpreadsheetColumns(object):
    def numColumns(self):
        """Return the number of custom columns in the spreadsheet view"""
        return 0

    def columnName(self, column):
        """Return the name of a custom column"""
        return ""

    def getData(self, row, column, item):
        """Return the data in a cell"""
        return None

    def setData(self, row, column, item, data):
        """Set the data in a cell"""
        return

    def getTooltip(self, row, column, item):
        """Return the tooltip for a cell"""
        return ""

    def getFont(self, row, column, item):
        """Return the tooltip for a cell"""
        return None

    def getBackground(self, row, column, item):
        """Return the background colour for a cell"""
        return None

    def getForeground(self, row, column, item):
        """Return the text colour for a cell"""
        return None

    def getIcon(self, row, column, item):
        """Return the icon for a cell"""
        return None

    def getSizeHint(self, row, column, item):
        """Return the size hint for a cell"""
        return None

    def paintCell(self, row, column, item, painter, option):
        """
        Paint a custom cell. Return True if the cell was painted, or False to continue
        with the default cell painting.
        """
        return False

    def createEditor(self, row, column, item, view):
        """Create an editing widget for a custom cell"""
        return None

    def setEditorData(self, row, column, item, editor):
        """
        Update the custom editor from the model data. Return True if this was done.
        """
        return False

    def setModelData(self, row, column, item, editor):
        """
        Update the model data from the custom editor. Return True if this was done.
        """
        return False

    def dropMimeData(self, row, column, item, data, items):
        """Handle a drag and drop operation"""
        return None

    def indexChanged(self, index):
        """This method is called when our custom widget changes index."""
        return None

# Register our custom columns
# hiero.ui.customColumn = CustomSpreadsheetColumns()
# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import hiero.core

import tank


class HieroEngine(tank.platform.Engine):
    """
    Engine for Hiero
    """
    
    # define the different areas where menu events can occur
    (HIERO_BIN_AREA, HIERO_SPREADSHEET_AREA, HIERO_TIMELINE_AREA) = range(3)
    
    def init_engine(self):

        # tracking where a menu click took place.
        self._last_clicked_selection = []
        self._last_clicked_area = None
        
        self.log_debug("%s: Initializing..." % self)


    def get_menu_selection(self):
        """
        Returns the list of hiero objects selected in the most recent menu click.
        This list may contain items of various types. To see exactly what is being 
        returned by which methods, turn on debug logging - this will print out details
        of what is going on.
        
        Examples of types that are being returned are:
        
        Selecting a project in the bin view:
        http://docs.thefoundry.co.uk/hiero/10/hieropythondevguide/api/api_core.html#hiero.core.Bin
        
        Selecting an item in a bin view:
        http://docs.thefoundry.co.uk/hiero/10/hieropythondevguide/api/api_core.html#hiero.core.BinItem
        
        Selecting a track:
        http://docs.thefoundry.co.uk/hiero/10/hieropythondevguide/api/api_core.html#hiero.core.TrackItem
        """
        return self._last_clicked_selection
        
    def get_menu_category(self):
        """
        Returns the UI area where the last menu click took place.
        
        Returns one of the following constants:
        
        - HieroEngine.HIERO_BIN_AREA
        - HieroEngine.HIERO_SPREADSHEET_AREA
        - HieroEngine.HIERO_TIMELINE_AREA
        - None for unknown or undefined
        """
        return self._last_clicked_area
    
    def post_app_init(self):
        # create menus
        tk_hiero = self.import_module("tk_hiero")
        self._menu_generator = tk_hiero.MenuGenerator(self)
        self._menu_generator.create_menu()

        def set_project_root(event):
            """Ensure any new projects get the project root or default startup 
            projects get the project root set
            """ 
            for p in hiero.core.projects():
                if not p.projectRoot():
                    self.log_debug("Setting projectRoot on %s to: %s" % (p.name(), self.tank.project_path))
                    p.setProjectRoot(self.tank.project_path)
        hiero.core.events.registerInterest('kAfterNewProjectCreated', set_project_root)

    def destroy_engine(self):
        self.log_debug("%s: Destroying..." % self)
        self._menu_generator.destroy_menu()

    # Logging
    ############################################################################
    def log_debug(self, msg):
        if self.get_setting("debug_logging", False):
            # ensure the debug log channel is on
            # we do this lazily to reduce amount of noise from hiero
            hiero.core.log.setLogLevel(hiero.core.log.kDebug)
            hiero.core.log.debug("Shotgun: %s" % msg)

    def log_info(self, msg):
        # ensure the debug log channel is on
        # we do this lazily to reduce amount of noise from hiero
        hiero.core.log.info("Shotgun: %s" % msg)

    def log_warning(self, msg):
        hiero.core.log.info("Shotgun Warning: %s" % msg)

    def log_error(self, msg):
        hiero.core.log.error("Shotgun: %s" % msg)

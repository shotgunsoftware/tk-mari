"""
Copyright (c) 2013 Shotgun Software, Inc
----------------------------------------------------
"""
import hiero.core

import tank


class HieroEngine(tank.platform.Engine):
    """
    Engine for Hiero
    """
    
    # define the different areas where menu events can occur
    (HIERO_BIN_AREA, HIERO_SPREADSHEET_AREA, HIERO_TIMELINE_AREA) = range(3)
    
    def init_engine(self):
        if self.get_setting("debug_logging", False):
            hiero.core.log.setLogLevel(hiero.core.log.kDebug)

        # tracking where a menu click took place.
        self._last_clicked_selection = []
        self._last_clicked_area = None
        
        self.log_debug("%s: Initializing..." % self)


    def get_selected_items(self):
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
        
    def get_area_for_menu_click(self):
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

    def destroy_engine(self):
        self.log_debug("%s: Destroying..." % self)
        self._menu_generator.destroy_menu()

    # Logging
    ############################################################################
    def log_debug(self, msg):
        hiero.core.log.debug("Sgtk: %s" % msg)

    def log_info(self, msg):
        hiero.core.log.info("Shotgun: %s" % msg)

    def log_warning(self, msg):
        hiero.core.log.info("Shotgun Warning: %s" % msg)

    def log_error(self, msg):
        hiero.core.log.error("Shotgun: %s" % msg)

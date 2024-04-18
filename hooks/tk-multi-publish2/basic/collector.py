# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import glob
import mari
import os
import sgtk
import tempfile
import uuid

HookBaseClass = sgtk.get_hook_baseclass()


class MariSessionCollector(HookBaseClass):
    """
    Collector that operates on the mari session. Should inherit from the basic
    collector hook.
    """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this collector expects to receive
        through the settings parameter in the process_current_session and
        process_file methods.

        A dictionary on the following form::

            {
                "Settings Name": {
                    "type": "settings_type",
                    "default": "default_value",
                    "description": "One line description of the setting"
            }

        The type string should be one of the data types that toolkit accepts as
        part of its environment configuration.
        """

        # return base class settings as there are is no Work Template at the moment for Mari
        return super(MariSessionCollector, self).settings or {}

    def process_current_session(self, settings, parent_item):
        """
        Analyzes the current session open in Mari and parents a subtree of
        items under the parent_item passed in.

        :param dict settings: Configured settings for this collector
        :param parent_item: Root item instance
        """

        if not mari.projects.current():
            self.logger.warning(
                "You must be in an open Mari project. No items collected!"
            )
            return

        layers_icon_path = os.path.join(
            self.disk_location, os.pardir, "icons", "mari_layer.png"
        )
        thumbnail = self._extract_mari_thumbnail()

        item_name = "All channels flattened"
        all_channels_flattened = parent_item.create_item(
            "mari.texture", "Texture folder", item_name
        )
        all_channels_flattened.thumbnail_enabled = True
        all_channels_flattened.set_icon_from_path(layers_icon_path)
        all_channels_flattened.set_thumbnail_from_path(thumbnail)
        all_channels_flattened.context_change_allowed = True

    def _extract_mari_thumbnail(self):
        """
        Render a thumbnail for the current canvas in Mari

        :returns:   The path to the thumbnail on disk
        """
        if not mari.projects.current():
            return

        canvas = mari.canvases.current()
        if not canvas:
            return

        # calculate the maximum size to capture:
        MAX_THUMB_SIZE = 512
        sz = canvas.size()
        thumb_width = sz.width()
        thumb_height = sz.height()
        max_sz = max(thumb_width, sz.height())

        if max_sz > MAX_THUMB_SIZE:
            scale = min(float(MAX_THUMB_SIZE) / float(max_sz), 1.0)
            thumb_width = max(min(int(thumb_width * scale), thumb_width), 1)
            thumb_height = max(min(int(thumb_height * scale), thumb_height), 1)

        # disable the HUD:
        hud_enabled = canvas.getDisplayProperty("HUD/RenderHud")
        if hud_enabled:
            # Note - this doesn't seem to work when capturing an image!
            canvas.setDisplayProperty("HUD/RenderHud", False)

        # render the thumbnail:
        thumb = None
        try:
            thumb = self._capture(canvas, thumb_width, thumb_height)
        except Exception:
            pass

        # reset the HUD
        if hud_enabled:
            canvas.setDisplayProperty("HUD/RenderHud", True)

        if thumb:
            # save the thumbnail
            jpg_thumb_path = os.path.join(
                tempfile.gettempdir(), "sgtk_thumb_%s.jpg" % uuid.uuid4().hex
            )
            thumb.save(jpg_thumb_path)
        else:
            jpg_thumb_path = None

        return jpg_thumb_path

    def _capture(self, canvas, thumb_width, thumb_height):
        """
        Generate a screenshot from the given canvas.
        """
        thumb = None

        # The capture method was introduced to deprecate captureImage in 4.6,
        # so use it if available. We could have use the inspect module here to
        # differentiate between the signatures with and without arguments
        # for capture, but the module can't read the parameters from C Python
        # methods.

        # In Mari 4.6.4+ we can capture with width and height passed in
        try:
            return canvas.capture(thumb_width, thumb_height)
        except Exception:
            pass
        else:
            return thumb

        # In some earlier versions, we need to call scale after capture
        try:
            image = canvas.capture()
            if image:
                image = image.scaled(thumb_width, thumb_height)
            return image
        except Exception:
            pass

        # Finally in older versions of Mari, capture is not even an option, so call
        # captureImage
        return canvas.captureImage(thumb_width, thumb_height)

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

from tank import TankError
from tank import TemplatePath
from tank.templatekey import (IntegerKey, SequenceKey, StringKey)

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

        # grab any base class settings
        collector_settings = super(MariSessionCollector, self).settings or {}

        # settings specific to this collector
        mari_session_settings = {
            "Work Template": {
                "type": "template",
                "default": None,
                "description": "Template path for artist work files. Should "
                               "correspond to a template defined in "
                               "templates.yml. If configured, is made available"
                               "to publish plugins via the collected item's "
                               "properties. ",
            },
        }

        # update the base settings with these settings
        collector_settings.update(mari_session_settings)

        return collector_settings

    def process_current_session(self, settings, parent_item):
        """
        Analyzes the current session open in Mari and parents a subtree of
        items under the parent_item passed in.

        :param dict settings: Configured settings for this collector
        :param parent_item: Root item instance
        """

        # create an item representing the current mari session
        channel_item, layer_item = self.collect_current_mari_session(settings, parent_item)

        self._collect_files(settings, channel_item, layer_item)

    def collect_current_mari_session(self, settings, parent_item):
        """
        Creates an item that represents the current mari session.

        :param dict settings: Configured settings for this collector
        :param parent_item: Parent Item instance
        :returns: Items of type mari.channels and mari.layers
        """

        if not mari.projects.current():
            self.logger.warning("You must be in an open Mari project to be able to publish!")

        publisher = self.parent

        # create the channel item for the publish hierarchy
        channel_item = parent_item.create_item(
            "mari.channels",
            "Publish flattened channels",
            "Texture Channels",
        )
        # get the icon path to display for this item
        icon_path = os.path.join(
            self.disk_location,
            os.pardir,
            "icons",
            "mari_channel_publish.png"
        )
        channel_item.set_icon_from_path(icon_path)

        # create the layer item for the publish hierarchy
        layer_item = parent_item.create_item(
            "mari.layers",
            "Publish individual layers for channels",
            "Texture Channel Layers",
        )
        # get the icon path to display for this item
        icon_path = os.path.join(
            self.disk_location,
            os.pardir,
            "icons",
            "mari_layer_publish.png"
        )
        layer_item.set_icon_from_path(icon_path)

        # if a work file template is defined, add it to the item properties so
        # that it can be used by attached publish plugins
        work_template_setting = settings.get("Work Template")
        if work_template_setting:

            work_template = publisher.engine.get_template_by_name(
                work_template_setting.value)

            # store the template on the item for use by publish plugins. we
            # can't evaluate the fields here because there's no guarantee the
            # current session path won't change once the item has been created.
            # the attached publish plugins will need to resolve the fields at
            # execution time.
            channel_item.properties["work_template"] = work_template
            layer_item.properties["work_template"] = work_template
            self.logger.debug("Work file template defined for Mari collection.")

        return channel_item, layer_item

    def _collect_files(self, settings, channel_item, layer_item):
        """
        Collect texture files to be published
        :param dict settings: Configured settings for this collector
        :param channel_item:   Parent Item instance for channels
        :param layer_item:   Parent item instance for layers
        """

        # check that we are currently inside a project:
        if not mari.projects.current():
            raise TankError("You must be in an open Mari project to be able to publish!")

        publisher = self.parent

        icon_path = os.path.join(
            self.disk_location,
            os.pardir,
            "icons",
            "texture.png"
        )

        # Look for all layers for all channels on all geometry.  Create items for both
        # the flattened channel as well as the individual layers
        for geo in mari.geo.list():
            geo_name = geo.name()
            
            for channel in geo.channelList():
                channel_name = channel.name()

                # find all publishable layers:
                publishable_layers = self._find_publishable_layers_r(channel.layerList())
                if not publishable_layers:
                    # no layers to publish!
                    continue

                # add item for whole flattened channel:
                item_name = "%s, %s" % (geo.name(), channel.name())
                item = channel_item.create_item(
                    "mari.texture",
                    "Channel",
                    item_name
                )
                item.set_icon_from_path(icon_path)
                item.thumbnail_enabled = True
                
                item.properties["geo_publish_name"] = geo_name
                item.properties["channel_publish_name"] = channel_name
                item.set_thumbnail_from_path(self._extract_mari_thumbnail())

                # add item for each publishable layer:
                found_layer_names = set()
                for layer in publishable_layers:
                    
                    # for now, duplicate layer names aren't allowed!
                    layer_name = layer.name()
                    if layer_name in found_layer_names:
                        # we might want to handle this one day...
                        pass
                    found_layer_names.add(layer_name)

                    item_name = "%s, %s (%s)" % (geo.name(), channel.name(), layer_name)
                    item = layer_item.create_item(
                        "mari.texture",
                        "Layer",
                        item_name
                    )
                    item.set_icon_from_path(icon_path)
                    item.set_thumbnail_from_path(self._extract_mari_thumbnail())

                    item.properties["geo_publish_name"] = geo_name
                    item.properties["channel_publish_name"] = channel_name
                    item.properties["layer_publish_name"] = layer_name

    def _find_publishable_layers_r(self, layers):
        """
        Find all publishable layers within the specified list of layers.  This will return
        all layers that are either paintable or procedural and traverse any layer groups
        to find all grouped publishable layers
        :param layers:  The list of layers to inspect
        :returns:       A list of all publishable layers
        """
        publishable = []
        for layer in layers:
            # Note, only paintable or procedural layers are exportable from Mari - all
            # other layer types are only used within Mari.
            if layer.isPaintableLayer() or layer.isProceduralLayer():
                # these are the only types of layers that are publishable
                publishable.append(layer)
            elif layer.isGroupLayer():
                # recurse over all layers in the group looking for exportable layers:
                grouped_layers = self._find_publishable_layers_r(layer.layerStack().layerList())
                publishable.extend(grouped_layers or [])
    
        return publishable

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
            scale = min(float(MAX_THUMB_SIZE)/float(max_sz), 1.0)
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
            thumb = canvas.captureImage(thumb_width, thumb_height)
        except:
            pass
        
        # reset the HUD
        if hud_enabled:
            canvas.setDisplayProperty("HUD/RenderHud", True)
        
        if thumb:
            # save the thumbnail
            jpg_thumb_path = os.path.join(tempfile.gettempdir(), "sgtk_thumb_%s.jpg" % uuid.uuid4().hex)
            thumb.save(jpg_thumb_path)
        
        return jpg_thumb_path

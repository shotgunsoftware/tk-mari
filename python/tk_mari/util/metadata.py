# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import mari

PROJECT_METADATA_INFO = {
    "project_id":{"display_name":"Shotgun Project Id", "visible":False},
    "entity_type":{"display_name":"Shotgun Entity Type", "visible":False, "default_value":""},
    "entity_id":{"display_name":"Shotgun Entity Id", "visible":False},
    "step_id":{"display_name":"Shotgun Step Id", "visible":False},
    "task_id":{"display_name":"Shotgun Task Id", "visible":False}
}

GEO_METADATA_INFO = {
    "project_id":{"display_name":"Shotgun Project Id", "visible":False},
    "project":{"display_name":"Shotgun Project", "visible":True, "default_value":""},
    "entity_type":{"display_name":"Shotgun Entity Type", "visible":False, "default_value":""},
    "entity_id":{"display_name":"Shotgun Entity Id", "visible":False},
    "entity":{"display_name":"Shotgun Entity", "visible":True, "default_value":""},
    "task_id":{"display_name":"Shotgun Task Id", "visible":False},
    "task":{"display_name":"Shotgun Task", "visible":True, "default_value":""}
}

GEO_VERSION_METADATA_INFO = {
    "path":{"display_name":"Shotgun Project Id", "visible":True, "default_value":""},
    "publish_id":{"display_name":"Shotgun Project", "visible":True},
    "version":{"display_name":"Shotgun Entity Type", "visible":True}
}

def set_project_metadata(mari_project, ctx):
    """
    Set the Toolkit metadata on a geo so that we can track where it came from
    """
    metadata = {}
    metadata["project_id"] = ctx.project["id"]
    if ctx.entity:
        metadata["entity_type"] = ctx.entity["type"]
        metadata["entity_id"] = ctx.entity["id"]
    if ctx.step:
        metadata["step_id"] = ctx.step["id"]
    if ctx.task:
        metadata["task_id"] = ctx.task["id"]
        
    __set_metadata(mari_project, metadata, PROJECT_METADATA_INFO)

def get_project_metadata(mari_project):
    """
    """
    return __get_metadata(mari_project, PROJECT_METADATA_INFO)

def set_geo_metadata(geo, project, entity, task):
    """
    Set the Toolkit metadata on a geo so that we can track where it came from
    """
    metadata_info = GEO_METADATA_INFO.copy()
    
    # define the metadata we want to store:
    metadata = {}
    if project:
        metadata["project_id"] = project["id"]
        metadata["project"] = project.get("name")
    if entity:
        metadata_info["entity"]["display_name"] = "Shotgun %s" % entity.get("type") or "Entity"
        metadata["entity_type"] = entity["type"]
        metadata["entity_id"] = entity["id"]
        metadata["entity"] = entity.get("name")
    if task:
        metadata["task_id"] = task["id"]
        metadata["task"] = task["name"] 
    
    __set_metadata(geo, metadata, metadata_info)

def get_geo_metadata(geo):
    """
    """
    return __get_metadata(geo, GEO_METADATA_INFO)    

def set_geo_version_metadata(geo_version, path, publish_id, version):
    """
    Set the Toolkit metadata on a geo so that we can track where it came from
    """
    # define the metadata we want to store:
    metadata = {"path":path, "publish_id":publish_id,"version":version}
    
    __set_metadata(geo_version, metadata, GEO_VERSION_METADATA_INFO)

def get_geo_version_metadata(geo_version):
    """
    """
    return __get_metadata(geo_version, GEO_VERSION_METADATA_INFO)     

def __set_metadata(obj, metadata, md_details):
    """
    """
    for name, details in md_details.iteritems():
        value = metadata.get(name, details.get("default_value"))
        if value == None:
            continue

        md_name = "tk_%s" % name
        
        obj.setMetadata(md_name, value)
        if "display_name" in details:
            obj.setMetadataDisplayName(md_name, details["display_name"])
            
        flags = obj.METADATA_SAVED
        visible = details.get("visible", True)
        if visible:
            flags |= obj.METADATA_VISIBLE
        obj.setMetadataFlags(md_name, flags)

def __get_metadata(obj, md_details):
    """
    """
    metadata = {}
    for name, _ in md_details.iteritems():
        md_name = "tk_%s" % name
        if obj.hasMetadata(md_name):
            metadata[name] = obj.metadata(md_name)
    return metadata
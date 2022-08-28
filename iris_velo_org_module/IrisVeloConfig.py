#!/usr/bin/env python3
#
#
#  IRIS velo Source Code
#  Copyright (C) 2022 - Stephan Mikiss
#  stephan.mikiss@gmail.com
#  Created by Stephan Mikiss - 2022-08-27
#
#  License Lesser GNU GPL v3.0

module_name = "IrisVeloCreateOrg"
module_description = "Provides an interface between IRIS and Velociraptor to create new organizations in Velociraptor"
interface_version = 1.1
module_version = 1.1

pipeline_support = False
pipeline_info = {}


module_configuration = [
    {
        "param_name": "velo_api_config",
        "param_human_name": "velo API config file",
        "param_description": "Specify the full path to the API config file (yaml) to be used by pyvelociraptor. This must be accessible from the DFIR-IRIS container",
        "default": None,
        "mandatory": True,
        "type": "string"
    },
    {
        "param_name": "velo_org_admin_users",
        "param_human_name": "Enterprise Administrators",
        "param_description": "Specify already existing usernames that should be added as administrators to all orgs in Velociraptor created via this module. Use ',' (comma) as seperator only!",
        "default": None,
        "mandatory": False,
        "type": "string"
    },
    {
        "param_name": "velo_org_investigator_users",
        "param_human_name": "Enterprise Investigators",
        "param_description": "Specify already existing usernames that should be added as Investigator to all orgs in Velociraptor created via this module. Use ',' (comma) as seperator only!",
        "default": None,
        "mandatory": False,
        "type": "string"
    },
    {
        "param_name": "velo_org_analyst_users",
        "param_human_name": "Enterprise Analyst",
        "param_description": "Specify already existing usernames that should be added as Analyst to all orgs in Velociraptor created via this module. Use ',' (comma) as seperator only!",
        "default": None,
        "mandatory": False,
        "type": "string"
    },
    {
        "param_name": "velo_org_reader_users",
        "param_human_name": "Enterprise Reader",
        "param_description": "Specify already existing usernames that should be added as Reader to all orgs in Velociraptor created via this module. Use ',' (comma) as seperator only!",
        "default": None,
        "mandatory": False,
        "type": "string"
    },
    {
        "param_name": "velo_on_postload_case_create",
        "param_human_name": "Triggers automatically on case creation",
        "param_description": "Set to True to automatically create a new organization in Velociraptor each time a case is created",
        "default": True,
        "mandatory": True,
        "type": "bool",
        "section": "Triggers"
    }
    
]
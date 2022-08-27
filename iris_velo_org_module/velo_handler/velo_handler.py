#!/usr/bin/env python3
#
#
#  IRIS velo Source Code
#  Copyright (C) 2022 - Stephan Mikiss
#  stephan.mikiss@gmail.com
#  Created by Stephan Mikiss - 2022-08-27
#
#  License Lesser GNU GPL v3.0


import traceback
from jinja2 import Template

import iris_interface.IrisInterfaceStatus as InterfaceStatus
from app.datamgmt.manage.manage_attribute_db import add_tab_attribute_field

import argparse
import json
import grpc
import time
import yaml

import pyvelociraptor
from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc

class VeloHandler(object):
    def __init__(self, mod_config, logger):
        self.mod_config = mod_config
        self.log = logger
        self.config = pyvelociraptor.LoadConfigFile(self.mod_config.get('velo_api_config'))

    def run_query(self, query, query_name):
        # Fill in the SSL params from the api_client config file. You can get such a file:
        # velociraptor --config server.config.yaml config api_client > api_client.conf.yaml
        self.log.info('[run_query func] was entered.')

        creds = grpc.ssl_channel_credentials(
            root_certificates=self.config["ca_certificate"].encode("utf8"),
            private_key=self.config["client_private_key"].encode("utf8"),
            certificate_chain=self.config["client_cert"].encode("utf8"))

        self.log.info('[run_query func] creds were loaded from config file.')

        # This option is required to connect to the grpc server by IP - we
        # use self signed certs.
        options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)

        # The first step is to open a gRPC channel to the server..
        with grpc.secure_channel(self.config["api_connection_string"],
                                creds, options) as channel:
            stub = api_pb2_grpc.APIStub(channel)

            # The request consists of one or more VQL queries. Note that
            # you can collect artifacts by simply naming them using the
            # "Artifact" plugin.
            request = api_pb2.VQLCollectorArgs(
                max_wait=1,
                max_row=100,
                Query=[api_pb2.VQLRequest(
                    Name=query_name,
                    VQL=query,
                )]
            )

            # This will block as responses are streamed from the
            # server. If the query is an event query we will run this loop
            # forever.
            for response in stub.Query(request):
                if response.Response:
                    # Each response represents a list of rows. The columns
                    # are provided in their own field as an array, to
                    # ensure column order is preserved if required. If you
                    # dont care about column order just ignore the Columns
                    # field. Note that although JSON does not specify the
                    # order of keys in a dict Velociraptor always
                    # maintains this order so an alternative to the
                    # Columns field is to use a JSON parser that preserves
                    # field ordering.

                    # print("Columns %s:" % response.Columns)

                    # The actual payload is a list of dicts. Each dict has
                    # column names as keys and arbitrary (possibly nested)
                    # values.
                    package = json.loads(response.Response)
                    self.log.info(f"[run(query)]JSON Response: {package}")

                elif response.log:
                    # Query execution logs are sent in their own messages.
                    self.log.info("%s: %s" % (time.ctime(response.timestamp / 1000000), response.log))

    def handle_new_case(self, case):
        """
        Handles a new case and creates a new org in Velociraptor

        :param case: Case instance
        :return: IIStatus
        """

        self.log.info(f'[Handle_New_Case]Starting org_create function for {case.client.name} with OrgID {case.client.client_id} for ticket {case.soc_id}')
        
        # Get info about available attributes of the object
        #for attr in dir(case):
        #    self.log.info("[Handle_New_Case]Received data: case.%s = %r" % (attr, getattr(case, attr)))

        #for attr in dir(case.client):
        #    self.log.info("[Handle_New_Case]Received data: case.client.%s = %r" % (attr, getattr(case.client, attr)))


        # Add Organization
        query_name = f"IRIS-VELO-ORG-{case.client.name}"
        query = f"SELECT org_create(name='{case.client.name}', org_id='{case.client.client_id}') FROM scope()"
        self.run_query(query, query_name)

        # Add Reader
        if self.mod_config.get('velo_org_reader_users'):
            userlist = self.mod_config.get('velo_org_reader_users').replace(' ','')
            userlist = userlist.split(',')

            if not "" in userlist:
                self.log.info(f"Adding userlist from config: {userlist}")
                
                for user in userlist:
                    query_name = f"IRIS-VELO-ORG-{case.client.client_id}-READER-ASSIGN-USER-{user}"
                    query = f"SELECT user_grant(user='{user}', roles='reader', orgs='{case.client.client_id}') FROM scope()"
                    
                    self.run_query(query, query_name) 

        # Add Analysts
        if self.mod_config.get('velo_org_analyst_users'):
            userlist = self.mod_config.get('velo_org_analyst_users').replace(' ','')
            userlist = userlist.split(',')

            if not "" in userlist:
                self.log.info(f"Adding userlist from config: {userlist}")
                
                for user in userlist:
                    query_name = f"IRIS-VELO-ORG-{case.client.client_id}-ANALYST-ASSIGN-USER-{user}"
                    query = f"SELECT user_grant(user='{user}', roles='analyst', orgs='{case.client.client_id}') FROM scope()"
                    
                    self.run_query(query, query_name) 

        # Add Investigators
        if self.mod_config.get('velo_org_investigator_users'):
            userlist = self.mod_config.get('velo_org_investigator_users').replace(' ','')
            userlist = userlist.split(',')

            if not "" in userlist:
                self.log.info(f"Adding userlist from config: {userlist}")
                
                for user in userlist:
                    query_name = f"IRIS-VELO-ORG-{case.client.client_id}-INVESTIGATOR-ASSIGN-USER-{user}"
                    query = f"SELECT user_grant(user='{user}', roles='investigator', orgs='{case.client.client_id}') FROM scope()"
                    
                    self.run_query(query, query_name)   

        # Add Admins 
        if self.mod_config.get('velo_org_admin_users'):
            userlist = self.mod_config.get('velo_org_admin_users').replace(' ','')
            userlist = userlist.split(',')

            if not "" in userlist:
                self.log.info(f"Adding userlist from config: {userlist}")
                
                for user in userlist:
                    query_name = f"IRIS-VELO-ORG-{case.client.client_id}-ADMIN-ASSIGN-USER-{user}"
                    query = f"SELECT user_grant(user='{user}', roles='administrator', orgs='{case.client.client_id}') FROM scope()"
                    
                    self.run_query(query, query_name)

        return InterfaceStatus.I2Success()

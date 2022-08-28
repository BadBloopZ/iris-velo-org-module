#!/usr/bin/env python3
#
#
#  IRIS velo Source Code
#  Copyright (C) 2022 - Stephan Mikiss
#  stephan.mikiss@gmail.com
#  Created by Stephan Mikiss - 2022-08-27
#
#  add_config_to_datastore is based on ds_store_file_b64 from here https://github.com/dfir-iris/iris-web/blob/fdf4271d0300c30a2cb104f587c410794a6ba59f/source/app/schema/marshables.py
#
#  run_query is based on run from here https://github.com/Velocidex/pyvelociraptor/blob/master/pyvelociraptor/client_example.py
#
#  License Lesser GNU GPL v3.0


#import traceback
#from jinja2 import Template

import iris_interface.IrisInterfaceStatus as InterfaceStatus
# Imports for datastore handling
import app
from app import db
from app.datamgmt.datastore.datastore_db import datastore_get_root
from app.datamgmt.datastore.datastore_db import datastore_get_standard_path
from app.models import DataStoreFile
from app.util import stream_sha256sum
#import marshmallow
import datetime

#import argparse
import json
import grpc
import time
#import yaml

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
        self.log.debug('[Handle_New_Case] [run_query func] was entered.')

        creds = grpc.ssl_channel_credentials(
            root_certificates=self.config["ca_certificate"].encode("utf8"),
            private_key=self.config["client_private_key"].encode("utf8"),
            certificate_chain=self.config["client_cert"].encode("utf8"))

        self.log.debug('[Handle_New_Case] [run_query func] creds were loaded from config file.')

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
                    self.log.debug(f"[Handle_New_Case] JSON Response: {package}")

                elif response.log:
                    # Query execution logs are sent in their own messages.
                    self.log.debug("[Handle_New_Case] %s: %s" % (time.ctime(response.timestamp / 1000000), response.log))

            return package
            

    def add_config_to_datastore(self, case, velo_config):

        velo_config_enc = velo_config.encode()
        
        self.log.debug(f'[Handle_New_Case][Add_Config_To_Datastore] was entered')
        file_hash = stream_sha256sum(velo_config_enc)
        self.log.debug(f'[Handle_New_Case] [Add_Config_To_Datastore] Created SHA265 hash of configuration content: {file_hash}')
        
        dsp = datastore_get_root(case.__dict__.get("case_id"))
        if not dsp:
            return response_error('Invalid path node for this case')
        self.log.debug(f'[Handle_New_Case] [Add_Config_To_Datastore] Node_Id of root node of the case is: {dsp.path_id}')

        # Get info about available attributes of the object
        # for attr in dir(dsp):
        #     self.log.info("[Add_Config_To_Datastore] datastore_get_root returns data: dsp.%s = %r" % (attr, getattr(dsp, attr)))
            
        dsf = DataStoreFile()
        dsf.file_original_name = f"client.{case.client_id}.config.yaml"
        dsf.file_description = f"Velociraptor client config for {case.client.name}."
        dsf.file_tags = "Velociraptor"
        dsf.file_password = ""
        dsf.file_is_ioc = False
        dsf.file_is_evidence = False
        dsf.file_case_id = case.__dict__.get("case_id")
        dsf.file_date_added = datetime.datetime.now()
        dsf.added_by_user_id = case.user_id
        dsf.file_local_name = 'tmp_config'
        dsf.file_parent_id = dsp.path_id
        dsf.file_sha256 = file_hash

        db.session.add(dsf)
        db.session.commit()

        dsf.file_local_name = datastore_get_standard_path(dsf, case.__dict__.get("case_id")).as_posix()
        db.session.commit()
        
        with open(dsf.file_local_name, 'wb') as fout:
            fout.write(velo_config_enc)

        setattr(self, 'file_local_path', str(dsf.file_local_name))

        # return dsf, exists

        

    def handle_new_case(self, case):
        """
        Handles a new case and creates a new org in Velociraptor

        :param case: Case instance
        :return: IIStatus
        """

        self.log.info(f'[Handle_New_Case]Starting org_create function for {case.client.name} with OrgID {case.client.client_id} for ticket {case.soc_id}')
        
        # Get all available keys in the dict:
        # self.log.info("[Handle_New_Case]Received data: case keys: %s" % (case.__dict__.keys()))
        # case keys: dict_keys(['_sa_instance_state', 'close_date', 'description', 'soc_id', 'custom_attributes', 'client_id', 'open_date', 'user_id', 'name', 'case_id', 'client'])

        # Get info about available attributes of the object
        # for attr in dir(case):
        #     self.log.info("[Handle_New_Case]Received data: case.%s = %r" % (attr, getattr(case, attr)))

        # Available fields for 'case':
        # case.client = <Client 2>
        # case.client_id = 2
        # case.close_date = None
        # case.custom_attributes = OrderedDict()
        # case.description = '1111'
        # case.metadata = MetaData()
        # case.name = '#19 - check case hook fields 1'
        # case.open_date = datetime.date(2022, 8, 28)
        # case.soc_id = '11'
        # case.user = 1 - administrator
        # case.user_id = 1

        # for attr in dir(case.client):
        #     self.log.info("[Handle_New_Case]Received data: case.client.%s = %r" % (attr, getattr(case.client, attr)))

        # Available fields for case.client
        # case.client.client_id = 2
        # case.client.custom_attributes = OrderedDict()
        # case.client.metadata = MetaData()
        # case.client.name = 'Iris First New Customer GmbH'


        # Add Organization
        query_name = f"IRIS-VELO-ORG-{case.client.name}"
        query = f"SELECT org_create(name='{case.client.name}', org_id='{case.client.client_id}') FROM scope()"
        response = self.run_query(query, query_name)

        for key,value in response[0].items():
            if value is not None:
                self.log.info(f"[Handle_New_Case] Organization newly created! Proceeding with user role assignment!")
                # Add Reader
                if self.mod_config.get('velo_org_reader_users'):
                    userlist = self.mod_config.get('velo_org_reader_users').replace(' ','')
                    userlist = userlist.split(',')

                    if "" not in userlist:
                        self.log.debug(f"[Handle_New_Case] Adding userlist from config: {userlist}")

                        for user in userlist:
                            query_name = f"IRIS-VELO-ORG-{case.client.name}-READER-ASSIGN-USER-{user}"
                            query = f"SELECT user_grant(user='{user}', roles='reader', orgs='{case.client.client_id}') FROM scope()"

                            self.run_query(query, query_name) 

                # Add Analysts
                if self.mod_config.get('velo_org_analyst_users'):
                    userlist = self.mod_config.get('velo_org_analyst_users').replace(' ','')
                    userlist = userlist.split(',')

                    if "" not in userlist:
                        self.log.debug(f"[Handle_New_Case] Adding userlist from config: {userlist}")

                        for user in userlist:
                            query_name = f"IRIS-VELO-ORG-{case.client.name}-ANALYST-ASSIGN-USER-{user}"
                            query = f"SELECT user_grant(user='{user}', roles='analyst', orgs='{case.client.client_id}') FROM scope()"

                            self.run_query(query, query_name) 

                # Add Investigators
                if self.mod_config.get('velo_org_investigator_users'):
                    userlist = self.mod_config.get('velo_org_investigator_users').replace(' ','')
                    userlist = userlist.split(',')

                    if "" not in userlist:
                        self.log.debug(f"[Handle_New_Case] Adding userlist from config: {userlist}")

                        for user in userlist:
                            query_name = f"IRIS-VELO-ORG-{case.client.name}-INVESTIGATOR-ASSIGN-USER-{user}"
                            query = f"SELECT user_grant(user='{user}', roles='investigator', orgs='{case.client.client_id}') FROM scope()"

                            self.run_query(query, query_name)   

                # Add Admins 
                if self.mod_config.get('velo_org_admin_users'):
                    userlist = self.mod_config.get('velo_org_admin_users').replace(' ','')
                    userlist = userlist.split(',')

                    if "" not in userlist:
                        self.log.debug(f"[Handle_New_Case] Adding userlist from config: {userlist}")

                        for user in userlist:
                            query_name = f"IRIS-VELO-ORG-{case.client.name}-ADMIN-ASSIGN-USER-{user}"
                            query = f"SELECT user_grant(user='{user}', roles='administrator', orgs='{case.client.client_id}') FROM scope()"

                            self.run_query(query, query_name)

            else:
                self.log.info(f"[Handle_New_Case] Organization already existed! Skipping user role assignment!")


        # get client config from Velo
        self.log.info(f"[Handle_New_Case] Upload client config to datastore.")
        query_name = f"IRIS-VELO-ORG-{case.client.name}-GET-CLIENT-CONFIG"
        query = f"SELECT _client_config FROM orgs() WHERE OrgId='{case.client.client_id}'"
        client_config_json = self.run_query(query, query_name)

        if not client_config_json:
            self.log.error(f"Error while retrieving the client config for {case.client.name}")
            return InterfaceStatus.I2Error()

        client_config = client_config_json[0]['_client_config']
        self.log.debug(f"[Handle_New_Case] {client_config}")

        # store client config in datastore
        self.add_config_to_datastore(case, client_config)
        
        self.log.info(f'[Handle_New_Case] Completed creation of a new organization for {case.client.name} with OrgID {case.client.client_id} for ticket {case.soc_id}')
        
        return InterfaceStatus.I2Success()
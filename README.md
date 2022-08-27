# DFIR-IRIS Module 'Create Orgs in Velociraptor' `iris-velo-org-module`

`iris-velo-org-module` is a IRIS processor module created with https://github.com/dfir-iris/iris-skeleton-module. It hooks on created cases and adds the client of the case as new organization in Velociraptor. Furthermore, it can grant existing users in Velociraptor access to the case. If an organization already exists, it won't get recreated. However, the users will be added nevertheless.

[Velociraptor](https://github.com/Velocidex/velociraptor) is a tool for collecting host based state information using The Velociraptor Query Language (VQL) queries.
[DFIR-IRIS](https://github.com/dfir-iris/iris-web) is an Incident Response Investigation System to collect information about a case and act as documentation platform.

# How to run the module:
## Prerequisites
1. Run Velociraptor >= **0.6.6-rc1 Linux Build All Arches #1579**. Refer to [Velociraptors Readme](https://github.com/Velocidex/velociraptor#getting-the-latest-version) to get the current executable after the fix #1579 *Fixed crash in api_client command*.
2. Create API config and user in Velociraptor with Administrator and API permissions:
```
./velociraptor --config server.config.yaml config api_client --name iris-modules --role investigator,api api.config.yaml
```
3. Mount the api.config.yaml file in DFIR-IRIS 
docker-compose for both **Worker and Web-App**
4. Make sure that the Worker container can establish connections to Velociraptor API. Hint: Verify in the server.config.yaml that Velociraptor publishes the API to the required interface.

## Install release
1. Download the release *.whl to your DFIR-IRIS server
2. Copy the wheel to worker and app container of iris (Pay attention to the file name!)
```
sudo docker cp dist/iris_velo-org_module-1.0.0-py3-none-any.whl iris-web_worker_1:/iriswebapp/dependencies/
sudo docker cp dist/iris_velo-org_module-1.0.0-py3-none-any.whl iris-web_app_1:/iriswebapp/dependencies/
```
3. Force a reinstall of the module on the worker and app container of iris
```
sudo docker exec -it iris-web_worker_1 /bin/sh -c "pip3 install dependencies/iris_velo-org_module-1.0.0-py3-none-any.whl --force-reinstall"
sudo docker exec -it iris-web_app_1 /bin/sh -c "pip3 install dependencies/iris_velo-org_module-1.0.0-py3-none-any.whl --force-reinstall"
```
4. Restart the worker & app container
```
sudo docker restart iris-web_worker_1
sudo docker restart iris-web_app_1
```
5. Add the module via Advanced -> Modules -> Add Module -> Module name 'iris_velo_org_module'
6. Configure the module.

## Build from source
### Automatically
Run the *buildnpush2iris.sh* script. If you run docker as root, then run the script as root as well.

### Manually
1. Build the wheel from the module root directory that contains the setup.py
```
python3.9 setup.py bdist_wheel
```
2. Copy the wheel to worker and app container of iris
```
sudo docker cp dist/iris_velo-org_module-0.1.0-py3-none-any.whl iris-web_worker_1:/iriswebapp/dependencies/
sudo docker cp dist/iris_velo-org_module-0.1.0-py3-none-any.whl iris-web_app_1:/iriswebapp/dependencies/
```
3. Force a reinstall of the module on the worker and app container of iris
```
sudo docker exec -it iris-web_worker_1 /bin/sh -c "pip3 install dependencies/iris_velo-org_module-0.1.0-py3-none-any.whl --force-reinstall"
sudo docker exec -it iris-web_app_1 /bin/sh -c "pip3 install dependencies/iris_velo-org_module-0.1.0-py3-none-any.whl --force-reinstall"
```
4. Restart the worker & app container
```
sudo docker restart iris-web_worker_1
sudo docker restart iris-web_app_1
```


# Copyright

Copyright 2022, Stephan Mikiss under the License Lesser GNU GPL v3.0

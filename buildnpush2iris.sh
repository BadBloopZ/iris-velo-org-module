#!/bin/bash
echo "[BUILDnPUSH2IRIS] Starting the build and push process.."
SEARCH_DIR='./dist'
get_recent_file () {
    FILE=$(ls -Art1 ${SEARCH_DIR} | tail -n 1)
    if [ ! -f ${FILE} ]; then
        SEARCH_DIR="${SEARCH_DIR}/${FILE}"
        get_recent_file
    fi
    echo $FILE
    exit
}

python3.9 setup.py bdist_wheel

latest=$(get_recent_file)
module=${latest#"./dist/"}

echo "[BUILDnPUSH2IRIS] Found latest module file: $latest"
echo "[BUILDnPUSH2IRIS] Copy module file to docker containers.."
#echo "[BUILDnPUSH2IRIS] docker cp $latest iris-web_worker_1:/iriswebapp/dependencies/$module"
docker cp $latest iris-web_worker_1:/iriswebapp/dependencies/$module
#echo "[BUILDnPUSH2IRIS] docker cp $latest iris-web_app_1:/iriswebapp/dependencies/$module"
docker cp $latest iris-web_app_1:/iriswebapp/dependencies/$module
echo "[BUILDnPUSH2IRIS] Installing module in docker containers.."
#echo "[BUILDnPUSH2IRIS] docker exec -it iris-web_worker_1 /bin/sh -c \"pip3 install dependencies/$module --force-reinstall\""
docker exec -it iris-web_worker_1 /bin/sh -c "pip3 install dependencies/$module --force-reinstall"
#echo "[BUILDnPUSH2IRIS] docker exec -it iris-web_app_1 /bin/sh -c \"pip3 install dependencies/$module --force-reinstall\""
docker exec -it iris-web_app_1 /bin/sh -c "pip3 install dependencies/$module --force-reinstall"
echo "[BUILDnPUSH2IRIS] Restarting worker container.."
docker restart iris-web_worker_1
echo "[BUILDnPUSH2IRIS] Completed!"

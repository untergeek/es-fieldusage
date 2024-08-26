#!/bin/bash

# Source the common.bash file from the same path as the script
source $(dirname "$0")/common.bash

echo

# Stop and remove the docker container
RUNNING=$(docker ps -f name=${NAME} | grep -v NAMES | awk '{print $NF}')
EXISTS=$(docker ps -af name=${NAME} | grep -v NAMES | awk '{print $NF}')
if [ "${RUNNING}" == "${NAME}" ]; then
  echo "Stopping container ${NAME}..."
  echo "$(docker stop ${NAME}) stopped."
fi
if [ "${EXISTS}" == "${NAME}" ]; then
  echo "Removing container ${NAME}..."
  echo "$(docker rm -f ${NAME}) deleted."
fi

# Delete Docker network
docker network rm -f ${NAME}-net > /dev/null 2>&1

# Delete .env file and curl config file
echo "Deleting remaining files and directories"
rm -rf ${REPOLOCAL}
rm -f ${ENVCFG}
rm -f ${CURLCFG}
rm -f ${PROJECT_ROOT}/http_ca.crt

echo "Cleanup complete."

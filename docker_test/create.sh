#!/bin/bash


# Source the common.bash file from the same path as the script
source $(dirname "$0")/common.bash

echo

# Test to see if we were passed a VERSION
if [ "x${1}" == "x" ]; then
  echo "Error! No Elasticsearch version provided."
  echo "VERSION must be in Semver format, e.g. X.Y.Z, 8.6.0"
  echo "USAGE: ${0} VERSION"
  exit 1
fi

# Set the version
VERSION=${1}

######################################
### Setup snapshot repository path ###
######################################

# Nuke it from orbit, just to be sure
rm -rf ${REPOLOCAL}
mkdir -p ${REPOLOCAL}

#####################
### Run Container ###
#####################

docker network rm -f ${NAME}-net > /dev/null 2>&1
docker network create ${NAME}-net > /dev/null 2>&1

# Start the container
echo "Starting container \"${NAME}\" from ${IMAGE}:${VERSION}"
echo -en "Container ID: "
docker run -q -d -it --name ${NAME} --network ${NAME}-net -m ${MEMORY} \
  -p ${LOCAL_PORT}:${DOCKER_PORT} \
  -v ${REPOLOCAL}:${REPODOCKER} \
  -e "discovery.type=single-node" \
  -e "cluster.name=local-cluster" \
  -e "node.name=local-node" \
  -e "xpack.monitoring.templates.enabled=false" \
  -e "xpack.searchable.snapshot.shared_cache.size=50M" \
  -e "path.repo=${REPODOCKER}" \
${IMAGE}:${VERSION}

# Set the URL
URL=https://${URL_HOST}:${LOCAL_PORT}

# Add TESTPATH to ${ENVCFG}, creating it or overwriting it
echo "export CA_CRT=${PROJECT_ROOT}/http_ca.crt" >> ${ENVCFG}
echo "export TEST_PATH=${TESTPATH}" >> ${ENVCFG}
echo "export TEST_ES_SERVER=${URL}" >> ${ENVCFG}
echo "export TEST_ES_REPO=${REPONAME}" >> ${ENVCFG}

# Write some ESCLIENT_ environment variables to the .env file  
echo "export ESCLIENT_CA_CERTS=${CACRT}" >> ${ENVCFG}
echo "export ESCLIENT_HOSTS=${URL}" >> ${ENVCFG}

# Set up the curl config file, first line creates a new file, all others append
echo "-o /dev/null" > ${CURLCFG}
echo "-s" >> ${CURLCFG}
echo '-w "%{http_code}\n"' >> ${CURLCFG}

# Do the xpack_fork function, passing the container name and the .env file path
xpack_fork "${NAME}" "${ENVCFG}"

# Did we get a bad return code?
if [ $? -eq 1 ]; then

  # That's an error, and we need to exit
  echo "ERROR! Unable to get/reset elastic user password. Unable to continue. Exiting..."
  exit 1
fi

# We expect a 200 HTTP rsponse
EXPECTED=200

# Set the NODE var
NODE="${NAME} instance"

# Start with an empty value
ACTUAL=0

# Initialize loop counter
COUNTER=0

# Loop until we get our 200 code
echo
while [ "${ACTUAL}" != "${EXPECTED}" ] && [ ${COUNTER} -lt ${LIMIT} ]; do

  # Get our actual response
  ACTUAL=$(curl -K ${CURLCFG} ${URL})

  # Report what we received
  echo -en "\rHTTP status code for ${NODE} is: ${ACTUAL}"

  # If we got what we expected, we're great!
  if [ "${ACTUAL}" == "${EXPECTED}" ]; then
    echo " --- ${NODE} is ready!"

  else
    # Otherwise sleep and try again 
    sleep 1
    ((++COUNTER))
  fi

done
# End while loop

# If we still don't have what we expected, we hit the LIMIT
if [ "${ACTUAL}" != "${EXPECTED}" ]; then
  
  echo "Unable to connect to ${URL} in ${LIMIT} seconds. Unable to continue. Exiting..." 
  exit 1

fi

# Initialize trial license
echo
response=$(curl -s \
  --cacert ${CACRT} -u "${ESUSR}:${ESPWD}" \
  -XPOST "${URL}/_license/start_trial?acknowledge=true")

expected='{"acknowledged":true,"trial_was_started":true,"type":"trial"}'
if [ "$response" != "$expected" ]; then
  echo "ERROR! Unable to start trial license!"
else
  echo -n "Trial license started and acknowledged. "
fi

# Set up snapshot repository. The following will create a JSON file suitable for use with
# curl -d @filename

rm -f ${REPOJSON}  

# Build a pretty JSON object defining the repository settings
echo    '{'                    >> $REPOJSON
echo    '  "type": "fs",'      >> $REPOJSON
echo    '  "settings": {'      >> $REPOJSON
echo -n '    "location": "'    >> $REPOJSON
echo -n "${REPODOCKER}"        >> $REPOJSON
echo    '"'                    >> $REPOJSON
echo    '  }'                  >> $REPOJSON
echo    '}'                    >> $REPOJSON

# Create snapshot repository
response=$(curl -s \
  --cacert ${CACRT} -u "${ESUSR}:${ESPWD}" \
  -H 'Content-Type: application/json' \
  -XPOST "${URL}/_snapshot/${REPONAME}?verify=false" \
  --json \@${REPOJSON})

expected='{"acknowledged":true}'
if [ "$response" != "$expected" ]; then
  echo "ERROR! Unable to create snapshot repository"
else
  echo "Snapshot repository \"${REPONAME}\" created."
  rm -f ${REPOJSON}
fi


##################
### Wrap it up ###
##################

echo
echo "${NAME} container is up using image elasticsearch:${VERSION}"
echo "Ready to test!"
echo

if [ "$EXECPATH" == "$PROJECT_ROOT" ]; then
  echo "Environment variables are in .env"
elif [ "$EXECPATH" == "$SCRIPTPATH" ]; then
  echo "\$PWD is $SCRIPTPATH."
  echo "Environment variables are in ../.env"
else
  echo "Environment variables are in ${PROJECT_ROOT}/.env"
fi

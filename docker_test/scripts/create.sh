#!/bin/bash

IMAGE=es_fieldusage_test
RUNNAME=es_fieldusage_test8
LOCAL_PORT=9200
URL=http://127.0.0.1:${LOCAL_PORT}

if [ "x$1" == "x" ]; then
  echo "Error! No Elasticsearch version provided."
  echo "VERSION must be in Semver format, e.g. X.Y.Z, 8.6.0"
  echo "USAGE: $0 VERSION"
  exit 1
fi

VERSION=$1

# Save original execution path
EXECPATH=$(pwd)

# Extract the path for the script
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Navigate to the script, regardless of whether we were there
cd $SCRIPTPATH

# Go up one directory
cd ..

# Find out what the last part of this directory is called
UPONE=$(pwd | awk -F\/ '{print $NF}')

# Check if the image has been built. If not, build it.
if [[ "$(docker images -q ${IMAGE}:${VERSION} 2> /dev/null)" == "" ]]; then
  echo "Docker image ${IMAGE}:${VERSION} not found. Building from Dockerfile..."
  cd $SCRIPTPATH
  # Create a Dockerfile from the template
  cat Dockerfile.tmpl | sed -e "s/ES_VERSION/${VERSION}/" > Dockerfile
  docker build . -t ${IMAGE}:${VERSION}
fi

### Launch the containers (plural, in 8.x)
echo -en "\rStarting ${RUNNAME} container... "
docker run -d --name ${RUNNAME} -p ${LOCAL_PORT}:9200 \
-e "discovery.type=single-node" \
-e "cluster.name=local-cluster" \
-e "node.name=local" \
-e "xpack.monitoring.templates.enabled=false" \
-e "path.repo=/media" \
-e "xpack.security.enabled=false" \
${IMAGE}:${VERSION}

### Check to make sure the ES instances are up and running
echo
echo "Waiting for Elasticsearch instance to become available..."
echo
EXPECTED=200
NODE="${RUNNAME} instance"
ACTUAL=0
while [ $ACTUAL -ne $EXPECTED ]; do
  ACTUAL=$(curl -o /dev/null -s -w "%{http_code}\n" $URL)
  echo -en "\rHTTP status code for $NODE is: $ACTUAL"
  if [ $EXPECTED -eq $ACTUAL ]; then
    echo " --- $NODE is ready!"
  fi
  sleep 1
done

# Done
echo
echo "Creation complete. ${RUNNAME} container is up using image ${IMAGE}:${VERSION}"

echo
echo "Ready to test!"

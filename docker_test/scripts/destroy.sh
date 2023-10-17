#!/bin/bash

# Stop and remove the docker container
docker stop es_fieldusage_test8
docker rm es_fieldusage_test8

### Now begins the Dockerfile cleanup phase

# Save original execution path
EXECPATH=$(pwd)

# Extract the path for the script
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Navigate to the script, regardless of whether we were there
cd $SCRIPTPATH

# Remove the created Dockerfile
rm -f Dockerfile

echo "Cleanup complete."


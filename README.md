# es-fieldusage

[![PyPI - Version](https://img.shields.io/pypi/v/es-fieldusage.svg)](https://pypi.org/project/es-fieldusage)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/es-fieldusage.svg)](https://pypi.org/project/es-fieldusage)

-----

**Table of Contents**

- [es-fieldusage](#es-fieldusage)
  - [Installation](#installation)
  - [Description](#description)
    - [Top-level help output](#top-level-help-output)
    - [Command: `stdout` help output](#command-stdout-help-output)
    - [Command `file` help output](#command-file-help-output)
    - [Command `show-indices` help output](#command-show-indices-help-output)
  - [Docker usage](#docker-usage)
    - [Docker build](#docker-build)
    - [Docker run](#docker-run)
  - [License](#license)

## Installation

```console
pip install es-fieldusage
```

## Description

Determine which fields are being used, how much, for a given index.

### Top-level help output
```
$ es-fieldusage --help

Usage: es-fieldusage [OPTIONS] COMMAND [ARGS]...

  Elasticsearch Index Field Usage Reporting Tool

  Sum all field query/request access for one or more indices using the Elastic Field Usage API (https://ela.st/usagestats)

  Generate a report at the command-line with the stdout command for all indices in INDEX_PATTERN:

  $ es-fieldusage stdout INDEX_PATTERN

  To avoid errors, be sure to encapsulate wildcards in single-quotes:

  $ es-fieldusage stdout 'index-*'

Options:
  --config PATH                   Path to configuration file.
  --hosts TEXT                    Elasticsearch URL to connect to.
  --cloud_id TEXT                 Elastic Cloud instance id
  --api_token TEXT                The base64 encoded API Key token
  --id TEXT                       API Key "id" value
  --api_key TEXT                  API Key "api_key" value
  --username TEXT                 Elasticsearch username
  --password TEXT                 Elasticsearch password
  --request_timeout FLOAT         Request timeout in seconds
  --verify_certs / --no-verify_certs
                                  Verify SSL/TLS certificate(s)
  --ca_certs TEXT                 Path to CA certificate file or directory
  --client_cert TEXT              Path to client certificate file
  --client_key TEXT               Path to client key file
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --logfile TEXT                  Log file
  --logformat [default|ecs]       Log output format
  --blacklist TEXT                Named entities will not be logged
  -v, --version                   Show the version and exit.
  -h, --help                      Show this message and exit.

Commands:
  show-all-options  Show all configuration options
  stdout            Output field usage information to the console

  Learn more at https://github.com/untergeek/es-fieldusage
```

### Command: `stdout` help output

```
$ es-fieldusage stdout --help
Usage: es-fieldusage stdout [OPTIONS] SEARCH_PATTERN

  Display field usage information on the console for SEARCH_PATTERN

  $ es-fieldusage stdout [OPTIONS] SEARCH_PATTERN

Options:
  --show-report / --hide-report   Show a summary report  [default: show-report]
  --show-headers / --hide-headers
                                  Show block headers for un|accessed fields  [default: show-headers]
  --show-accessed / --hide-accessed
                                  Show accessed fields  [default: hide-accessed]
  --show-unaccessed / --hide-unaccessed
                                  Show unaccessed fields  [default: hide-unaccessed]
  --show-counts / --hide-counts   Show field access counts  [default: hide-counts]
  --delimiter TEXT                Value delimiter if access counts are shown  [default: ,]
  -h, --help                      Show this message and exit.

  Learn more at https://github.com/untergeek/es-fieldusage
  ```

### Command `file` help output

```
$ es-fieldusage file --help
Usage: es-fieldusage file [OPTIONS] SEARCH_PATTERN

  Write field usage information to file for SEARCH_PATTERN

  $ es-fieldusage file [OPTIONS] SEARCH_PATTERN

Options:
  --show-report / --hide-report   Show a summary report  [default: show-report]
  --show-headers / --hide-headers
                                  Show block headers for un|accessed fields  [default: show-headers]
  --show-accessed / --hide-accessed
                                  Show accessed fields  [default: hide-accessed]
  --show-unaccessed / --hide-unaccessed
                                  Show unaccessed fields  [default: hide-unaccessed]
  --show-counts / --hide-counts   Show field access counts  [default: hide-counts]
  --per_index                     Create one file per index found
  --delimiter TEXT                Value delimiter if access counts are shown  [default: ,]
  -h, --help                      Show this message and exit.

  Learn more at https://github.com/untergeek/es-fieldusage
```

### Command `show-indices` help output

```
$ es-fieldusage show-indices --help
Usage: es-fieldusage show-indices SEARCH_PATTERN

  Show indices on the console matching SEARCH_PATTERN

  $ es-fieldusage show_indices SEARCH_PATTERN

  This is included as a way to ensure you are seeing the indices you expect before using the file or stdout commands.

Options:
  -h, --help  Show this message and exit.

  Learn more at https://github.com/untergeek/es-fieldusage
```

## Docker usage

### Docker build

From the path which contains `Dockerfile`:

```
$ ./docker build . -t reponame/es-fieldusage:x.y.z
```

e.g.

```
docker build . -t untergeek/es-fieldusage:1.0.0
```

You can also build for x86_64 and arm64 if you have the appropriate buildx image setup:

```
docker buildx build --platform linux/amd64,linux/arm64 -t untergeek/es-fieldusage:1.0.0 --push .
```

### Docker run

**Example:**

```
docker run -t --rm --name es-fieldusage -v /path/to/configfile/:/.esfieldusage -v $(pwd)/:/fileoutput untergeek/es-fieldusage:1.0.0 --config /.esfieldusage/config.yml show-indices 'index-*'
```

**Explanation:**

  * The `-t` flag indicates that you are interacting with a terminal application
  * `--rm` deletes the created Docker image after the run. Omitting this will result in a lot of created images that run once. Using `--name` will prevent this collision if `--rm` is omitted by reminding you that there is already an image with the same name.
  * `--name` is the name of the image to create. This is optional.
  * `-v` sets up volumes. `/path/to/configfile/` is the local file path to where you have a YAML configuration file, if you choose to use one. The `:/.esfieldusage` portion of the volume map is the directory where that configuration file is expected in the Docker image. The second volume mapping is `$(pwd):/fileoutput`. `/fileoutput` is the dedicated file path on the Docker image where output from the [file](#command-file-help-output) command will be written. By using `$(pwd)` it will map your present working directory so the files will appear there. Otherwise you can map another path here.
  * `untergeek/es-fieldusage:1.0.0` is the `repository/image:version` to run.
  * `--config /.esfieldusage/config.yml`, as stated previously, if you intend to use a YAML configuration file, the path needs to be mapped as a volume, and then accessed this way. The filename should match whatever you actually have, and not necessarily `config.yml`
  * `show-indices 'index-*'` Everything after here is available as regular options and commands for es-fieldusage.

## License

`es-fieldusage` is distributed under the terms of the [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0) license.

# Covalent Docker Guide

To get started contributing to Covalent, you should fork this repository for your own development. (Learn more about [how to fork a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo).)

Clone your fork locally:

```shell
git clone https://github.com/my-github/covalent
```

where `my-github` is your personal GitHub account.

## Building Image

```shell
docker build . -t covalent
```

## Running Image

Before runnning the docker container ensure that you know which port the dispatcher is running in by checking the configuration file located at `~/.config/covalent/covalent.conf` or `$COVALENT_CONFIG_DIR/covalent.conf`.

If the port in the config is `48008`, the following would be used to run the unified docker container

```shell
docker run -d -p 48008:8080 covalent:latest
```

To acquire shell access to the container you can run the following:

```shell
docker exec -it $(docker container ls  | grep 'covalent:latest' | awk '{print $1}') /bin/bash
```
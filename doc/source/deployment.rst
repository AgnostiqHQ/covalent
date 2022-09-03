****************
Deployment Guide
****************

Covalent natively operates a server on the same machine as the client. In order to improve availability, resilience, and performance, users may choose to serve Covalent on a remote machine instead. This page describes a variety of methods in which users may choose to self-host Covalent on the cloud or on premises.

Deployment with Docker
######################

Covalent can be run using Docker Engine or on a container-based orchestration service such as Amazon ECS, Azure Container Instances, or Google Cloud Run. Covalent is distributed as a Docker image hosted at::

    https://gallery.ecr.aws/covalent/covalent

To pull this image locally, install Docker and run::

    docker pull public.ecr.aws/covalent/covalent:latest

and run it using::

    docker run -it -p 8080:8080 -d public.ecr.aws/covalent/covalent:latest

Alternatively, this image can be supplied to run on one of the managed container services and provide support for multiple users.

Note that this image can be built using the Dockerfile supplied with the source code. It uses a multi-stage build to minimize the final image size. The first stage installs Covalent and its dependencies::

    FROM python:3.8-slim-bullseye AS build

    RUN apt-get update \
      && apt-get install -y --no-install-recommends rsync wget \
      && rm -rf /var/lib/apt/lists/*

    RUN python -m venv --copies /covalent/.venv \
      && . /covalent/.venv/bin/activate \
      && pip install --upgrade pip \
      && pip install covalent

Python is installed using a virtual environment which is copied to the second stage::

    FROM python:3.8-slim-bullseye AS prod

    COPY --from=build /usr/bin/rsync /usr/bin/rsync
    COPY --from=build /usr/lib/x86_64-linux-gnu/libpopt.so.0 /usr/lib/x86_64-linux-gnu/libpopt.so.0

    COPY --from=build /usr/bin/wget /usr/bin/wget
    COPY --from=build /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0
    COPY --from=build /usr/lib/x86_64-linux-gnu/libpsl.so.5 /usr/lib/x86_64-linux-gnu/libpsl.so.5

    COPY --from=build /covalent/.venv/ /covalent/.venv

It is also important to set the following when running Covalent in a Docker container::

    ENV COVALENT_SERVER_IFACE_ANY=1
    ENV PATH=/covalent/.venv/bin:$PATH

The first variable exposes the server on all interfaces rather than just the local loopback ``127.0.0.1`` within the container. The second ensures the virtual environment will be used by the Covalent server.

Finally, start Covalent on a particular port::

    CMD covalent start --ignore-migrations --port 8080 && bash

Since the server runs as a daemon process, the trailing ``&& bash`` prevents the container from exiting.

Users coming with their own containers may choose to install Covalent as an extension. This is possible by replacing the ``FROM`` values with the user's container name. Note that if the base operating system differs from the recommended platform, Covalent may experience unexpected behavior. For a full list of supported platforms, refer to the Compatibility Matrix.

Deployment on AWS
#################

A popular method to serve Covalent is on AWS. Customers use AWS for its intuitive interface, pay-as-you-go billing, and high availability.  This guide describes how the Covalent server together with a Kubernetes compute backend may be deployed to AWS. Note that running this deployment will incur charges in the user's AWS account. Users are responsible for all charges incurred as a result of deploying Covalent on AWS.

Covalent Server on EC2
**********************

Gathering Requirements
----------------------

Configuring the Deployment
--------------------------

Server Deployment
-----------------

Validating the Deployment
-------------------------

Configuring the Client
----------------------

Hello, Covalent Server
----------------------

Backup and Recovery
-------------------

Security
--------

Troubleshooting
---------------


Kubernetes Backend on EKS
*************************

Gathering Requirements
----------------------

Configuring the Deployment
--------------------------

Cluster Deployment
------------------

Validating the Deployment
-------------------------

Configuring Covalent
--------------------

Using the Cluster with the Server
---------------------------------

Security
--------

Troubleshooting
---------------

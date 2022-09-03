****************
Deployment Guide
****************

Covalent natively operates a server on the same machine as the client. In order to improve availability, resilience, and performance, users may choose to serve Covalent on a remote machine instead. This page describes a variety of methods in which users may choose to self-host Covalent on the cloud or on premises.

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

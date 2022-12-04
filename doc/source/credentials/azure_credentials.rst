.. _azure_credentials:

#################################
Managing Azure Cloud Credentials
#################################

In order to use the Azure Batch executor, it needs to be configured with all the permissions necessary to create and manage the relevant Azure Batch resources. This can be done by creating an Azure Active Directory application and service principal, and then granting the service principal the necessary permissions.

Authentication with Service Principals
***************************************

An overview of the steps required to authenticate with service principals can be found `here <https://learn.microsoft.com/en-us/azure/batch/batch-aad-auth#use-a-service-principal>`_.

When creating a service principal, you chose the type of authentication that it uses: password or certificate-based. This can be be done using the `portal <https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal>`_ or using Azure powershell as discussed in the sections below.

Password-based authentication
=============================

Follow the `instructions <https://learn.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest#password-based-authentication>`_ to create a service principal with password-based authentication. The password is provided in the :code:`password` key in the output when creating the service principal.

.. warning:: The password needs to be copied and can't be retrieved later. If you lose it, the credentials will need to be `reset <https://learn.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest#6-reset-credentials>`_.

Certificate-based authentication
================================

For certificate-based authentication, you can either use an appropriately formatted existing certificate or create a new one when creating the service principal. Detailed instructions on can be found `here <https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest#Certificate-based-authentication>`_.

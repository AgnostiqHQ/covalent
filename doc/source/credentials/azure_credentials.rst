.. _azure_credentials:

#################################
Managing Azure Cloud Credentials
#################################

In order to use the Azure executors, it needs to be configured with all the permissions necessary to create and manage the relevant Azure resources. This can be done by creating a service principal, and then granting the service principal the necessary permissions.

Authentication with Service Principals
***************************************

When creating a service principal, you choose the type of authentication that it uses: password or certificate-based. This can be be done using the `portal <https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal>`_ or using Azure powershell as discussed in the sections below.

Password-based authentication
=============================

Follow the `instructions <https://learn.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest#password-based-authentication>`_ to create a service principal with password-based authentication. The password is provided in the :code:`password` key in the output when creating the service principal.

.. warning:: The password needs to be copied and can't be retrieved later. If you lose it, the credentials will need to be `reset <https://learn.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest#6-reset-credentials>`_.

In order to login with the password use the following command :

.. code-block:: bash

    az login --service-principal -u <client_id> -p <password> --tenant <tenant_id>

.. note:: The :code:`<client_id>` is the :code:`appId` in the output when creating the service principal.

Certificate-based authentication
================================

For certificate-based authentication, you can either use an appropriately formatted existing certificate or create a new one when creating the service principal. Detailed instructions on can be found `here <https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest#certificate-based-authentication>`_.

Similar to password-based authentication, you can login using the certificate by running:

.. code-block:: bash

    az login --service-principal -u <client_id> -p <certificate_path> --tenant <tenant_id>

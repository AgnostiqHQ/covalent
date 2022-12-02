.. _azure_credentials:

#################################
Managing Azure Cloud Credentials
#################################

Note: If you're looking to use the Azure Batch executor while authenticating with a service principal, that service principal should have been configured with all the permissions necessary to create and manage Azure Batch resources. For more information, see `Azure Batch Service Principal Permissions <https://docs.microsoft.com/en-us/azure/batch/batch-service-principal-auth#permissions-required-for-azure-batch>`__.


Authentication with Service Principals
***************************************

App ID, client-secret based authentication
===========================================

Sign in with service principles: Reference: https://learn.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli#4-sign-in-using-a-service-principal

Certificate-based authentication
================================

Sign in with certificate: Reference: https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest#sign-in-with-a-certificate

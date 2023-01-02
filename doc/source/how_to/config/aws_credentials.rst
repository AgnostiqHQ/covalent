.. _aws_credentials:

##############################
Managing AWS Cloud Credentials
##############################

AWS plugins assume the existence of a credentials file or environment variables in order to communicate with AWS services. This data must be available on the Covalent server. **Using root credentials or long-lived credentials provided via an IAM user is strongly discouraged.**

Following are several acceptable ways to manage AWS credentials on a Covalent server.

Periodic Manual Login
*********************

The simplest way to generate and store AWS credentials is to use the `AWS IAM Identity Center <https://aws.amazon.com/iam/identity-center>`_. User accounts should be administered via IAM Identity Center with multi-factor authentication (MFA) enabled. You can request short-lived access keys on the browser-based login portal. The default session duration is one hour; this can be increased to up to 12 hours.

With this solution, you must re-authenticate before the credentials expire or Covalent will fail to connect to AWS backend services. Credentials can be provided in a credentials file, or in the environment variables :code:`AWS_ACCESS_KEY_ID`, :code:`AWS_SECRET_ACCESS_KEY`, and :code:`AWS_SESSION_TOKEN`. If you are new to AWS Cloud, this is a quick way to get started. It is also a good solution if your workflows don't take long to run.

IAM Roles Anywhere
******************

If you host a persistent Covalent server outside of AWS, consider using the newly introduced `AWS IAM Roles Anywhere <https://docs.aws.amazon.com/rolesanywhere/latest/userguide/credential-helper.html>`_. This enables servers to authenticate to AWS using X.509 certificates. Best practices dictate that certificates always be issued by a private certificate authority (CA), although this can be expensive when using AWS Certificate Manager.

If you own a domain, you can instead choose to generate a trust anchor using `EFF’s Certbot <https://certbot.eff.org/>`_ with autorenewal. This process creates four files: the signing certificate :code:`cert.pem`, the certificate bundle :code:`fullchain.pem`, the intermediate chain :code:`chain.pem`, and the private key :code:`privkey.pem`.

Next, configure IAM Roles Anywhere with a trust anchor and a profile. Follow the instructions in IAM Roles Anywhere to create a trust anchor using an external certificate bundle. Note that there are three certificates in :code:`fullchain.pem`; only the final one is needed for the certificate bundle used by AWS. A custom role :code:`CovalentAWSPluginsRole` may be created for use with IAM Roles Anywhere which has trust relationships with the policies required by the various AWS plugins. An example is shown below which grants access to backends required by plugins and also restricts access based on the X.509 certificate’s common name:

.. code-block:: json

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "TrustRelationship",
                "Effect": "Allow",
                "Principal": {
                    "Service": "rolesanywhere.amazonaws.com"
                },
                "Action": [
                    "sts:AssumeRole",
                    "sts:SetSourceIdentity",
                    "sts:TagSession"
                ],
                "Condition": {
                    "StringEquals": {
                        "aws:PrincipalTag/x509Subject/CN": "mydomain.net"
                    }
                }
            }
        ]
    }

The policies attached to this role are :code:`CovalentBatchExecutorPolicy`, :code:`CovalentBraketJobsExecutionPolicy`, :code:`CovalentFargateExecutorPolicy`, and :code:`CovalentLambdaExecutorPolicy`.

The profile created in the IAM Roles Anywhere console, called :code:`CovalentPluginsUser`, uses the :code:`CovalentAWSPluginsRole` together with an inline policy which further restricts access based on the IP address of the Covalent server:

.. code-block:: json

    {
        "Version":"2012-10-17",
        "Statement":[
            {
                "Effect":"Deny",
                "Action":"*",
                "Resource":"*",
                "Condition": {
                    "NotIpAddress": {
                        "aws:SourceIp": "xxx.yyy.zzz.aaa/32"
                    },
                    "Bool": {
                        "aws:ViaAWSService": "false"
                    }
                }
            }
        ]
    }

Together, these restrictions mean that only requests from a server at the correct address and with the correct certificate are able to both assume the role and perform actions in the AWS account.

The final step involves setting up the Covalent server to retrieve short-lived credentials using the X.509 certificate and private key.  First download the appropriate AWS Signing Helper `here <https://docs.aws.amazon.com/rolesanywhere/latest/userguide/credential-helper.html>`_ Download the :code:`aws_signing_helper` binary, make it executable, and install it somewhere on the :code:`PATH`. Add the following to the file :code:`~/.aws/config`:

.. code-block:: toml

    [profile default]
        credential_process = aws_signing_helper credential-process \
          --certificate /path/to/cert.pem \
          --private-key /path/to/privkey.pem \
          --intermediates /path/to/chain.pem
          --trust-anchor-arn arn:aws:rolesanywhere:<region>:<account>:trust-anchor/<id> \
          --profile-arn arn:aws:rolesanywhere:<region>:<account>:profile/<id> \
          --role-arn arn:aws:iam::<account>:role/CovalentAWSPluginsRole \
          --endpoint rolesanywhere.<region>.amazonaws.com \
          --region <region>

Validate the role by calling the STS service using the AWS CLI:

.. code-block:: bash

    $ aws sts get-caller-identity
    {
        "UserId": "<key>:<value>",
        "Account": "<redacted>",
        "Arn": "arn:aws:sts::<account>:assumed-role/CovalentAWSPluginsRole/<id>"
    }

To summarize, in this solution, Covalent only needs the path of the AWS Config file, which can be set using the environment variable :code:`AWS_CONFIG_FILE`.  A profile name may also be needed depending on your previous credentials configuration.

IAM Roles on AWS
****************

The third scenario involves an even slightly more sophisticated setup, albeit with simpler authentication.  If you plan to use Covalent for heavy workloads with multiple users, you may want to self-host Covalent on AWS.  If the Covalent server is self-hosted on AWS [*link to self-hosted deployment guide*], the server can authenticate using an instance profile. During deployment, a role is created called :code:`CovalentServiceRole`. Attached to this role are the four policies :code:`CovalentBatchExecutorPolicy`, :code:`CovalentBraketJobsExecutionPolicy`, :code:`CovalentFargateExecutorPolicy`, and :code:`CovalentLambdaExecutorPolicy`.  No additional authentication is required, and no credentials file or environment variables are needed to interact with AWS backends via the plugins.

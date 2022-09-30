Managing Cloud Credentials
##########################

AWS plugins assume the existence of a credentials file or environment variables in order to communicate with AWS services.  This data lives on the Covalent server.  There are several best practices users should consider when managing AWS credentials on the Covalent server.  **Using root credentials or long-lived credentials provided via an IAM user are strongly discouraged.**

Periodic Manual Login
*********************

The simplest method to generate and store AWS credentials is via the `AWS IAM Identity Center <https://aws.amazon.com/iam/identity-center>`_.  User accounts should be administered via IAM Identity Center with MFA enabled.  Users may request short-lived access keys via the browser-based login portal.  The default session duration is one hour, although this may be increased to up to 12 hours.  With this solution, users need to re-authenticate before credentials expire or else Covalent will fail to connect to AWS backend services.  Credentials may be provided in the form of the credentials file, or as environment variables :code:`AWS_ACCESS_KEY_ID`, :code:`AWS_SECRET_ACCESS_KEY`, and :code:`AWS_SESSION_TOKEN`.  For users just getting started or with short workflows, this solution is ideal.

IAM Roles Anywhere
******************

Users hosting a persistent Covalent server outside of AWS should consider a more secure and stable solution with the newly introduced `AWS IAM Roles Anywhere <https://docs.aws.amazon.com/rolesanywhere/latest/userguide/credential-helper.html>`_.  This allows servers to authenticate to AWS using X.509 certificates issued by a trusted certificate authority (CA).  Best practices are that certificates are always issued by a private CA, although this can be expensive when using AWS Certificate Manager.  Users who own a domain may choose to generate a trust anchor using `EFF’s Certbot <https://certbot.eff.org/>`_ with autorenewal.  This process creates four files:  the signing certificate :code:`cert.pem`, the certificate bundle :code:`fullchain.pem`, the intermediate chain :code:`chain.pem`, and the private key :code:`privkey.pem`.

Next, configure IAM Roles Anywhere with a trust anchor and a profile. Follow the instructions in the IAM Roles Anywhere to create a trust anchor using an external certificate bundle. Note that there are three certificates in :code:`fullchain.pem`; only the final one is needed for the certificate bundle used by AWS.  A custom role :code:`CovalentAWSPluginsRole` may be created for use with IAM Roles Anywhere which has trust relationships with the policies required by the various AWS plugins.  An example is shown below which grants access to backends required by plugins and also restricts access based on the X.509 certificate’s common name:

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

Together, these restrictions mean that only requests from a server at the correct address and with the correct certificate will be able to both assume the role and perform actions in the AWS account.

The final step involves setting up the Covalent server to retrieve short-lived credentials using the X.509 certificate and private key.  First `download <https://docs.aws.amazon.com/rolesanywhere/latest/userguide/credential-helper.html>`_ the :code:`aws_signing_helper` binary, make it executable, and install it somewhere on the :code:`PATH`. Modify the file :code:`~/.aws/config` file with the following:

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

Validate the role is properly assumed by calling the STS service using the AWS CLI:

.. code-block:: bash

    $ aws sts get-caller-identity
    {
        "UserId": "<key>:<value>",
        "Account": "<redacted>",
        "Arn": "arn:aws:sts::<account>:assumed-role/CovalentAWSPluginsRole/<id>"
    }

To summarize, in this solution, Covalent will only need the path of the AWS Config file, which can be set using the environment variable :code:`AWS_CONFIG_FILE`.  A profile name may also be needed depending on the user’s previous credentials configuration.

IAM Roles on AWS
****************

The third scenario involves an even slightly more sophisticated setup, albeit with simpler authentication.  Users anticipating to use Covalent for heavier workloads for with multiple users may choose to self-host Covalent on AWS.  If the Covalent server itself is self-hosted on AWS [*link to self-hosted deployment guide*], the server can authenticate using an instance profile.  During deployment, a role is created called :code:`CovalentServiceRole`. Attached to this role are the four policies :code:`CovalentBatchExecutorPolicy`, :code:`CovalentBraketJobsExecutionPolicy`, :code:`CovalentFargateExecutorPolicy`, and :code:`CovalentLambdaExecutorPolicy`.  Therefore, no additional authentication is required, and no credentials file or environment variable is needed to interact with AWS backends via the plugins.

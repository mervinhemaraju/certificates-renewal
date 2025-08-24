import os
import logging
import oci
from kink import di
from functools import wraps
from dopplersdk import DopplerSDK
from slack_sdk import WebClient
from functions import extract_secret


def main_injection(func):
    # Generates an OCI config
    def __generate_oci_config(secret, oci_secrets_name, oci_account, oci_region):
        #  Retrieve account info from secrets
        user_id = extract_secret(
            secret=secret,
            project=oci_secrets_name,
            key=f"OCI_{oci_account}_USER_OCID",
        )
        tenancy_id = extract_secret(
            secret=secret,
            project=oci_secrets_name,
            key=f"OCI_{oci_account}_TENANCY_OCID",
        )
        key_content = extract_secret(
            secret=secret,
            project=oci_secrets_name,
            key="OCI_API_KEY_PRIVATE",
        )
        fingerprint = extract_secret(
            secret=secret,
            project=oci_secrets_name,
            key="OCI_API_FINGERPRINT",
        )

        # Return the config
        return {
            "user": user_id,
            "key_content": key_content,
            "fingerprint": fingerprint,
            "tenancy": tenancy_id,
            "region": oci_region,
        }

    # DI Wrapper
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Set logging
        logging.getLogger().setLevel(logging.INFO)

        # Retrieve OS variables
        DOPPLER_MAIN_TOKEN = os.environ["DOPPLER_MAIN_TOKEN"]

        # Set variables
        APPS_SECRETS_NAME = "apps-creds"
        OCI_SECRETS_NAME = "cloud-oci-creds"
        OCI_ACCOUNT_NAME = "HELIOS"
        OCI_REGION = "af-johannesburg-1"

        # Initialize doppler
        doppler = DopplerSDK()
        doppler.set_access_token(DOPPLER_MAIN_TOKEN)

        # Generate the OCI config
        config = __generate_oci_config(
            oci_secrets_name=OCI_SECRETS_NAME,
            oci_account=OCI_ACCOUNT_NAME,
            oci_region=OCI_REGION,
            secret=doppler.secrets,
        )

        # Validate oci config
        oci.config.validate_config(config)

        # Initialize the slack sdk
        di["slack_wc"] = WebClient(
            token=extract_secret(
                secret=doppler.secrets,
                project=APPS_SECRETS_NAME,
                key="SLACK_BOT_MAIN_TOKEN",
            )
        )

        # Set DI Injections
        # > injections
        di["owner_email"] = "mervinhemaraju16@gmail.com"
        di["working_directory"] = "/tmp/renewdirectory"
        di["bucket_certificate_name"] = "certificates"
        di["bucket_certificate_directory_live"] = (
            "live/san-mervinhemaraju-com-plagueworks-org"
        )
        di["bucket_certificate_directory_backup"] = (
            "backup/san-mervinhemaraju-com-plagueworks-org"
        )
        di["load_balancer_name"] = "web"
        di["certificate_files"] = [
            "cert.pem",
            "chain.pem",
            "fullchain.pem",
            "privkey.pem",
        ]

        # > secrets injections
        di["secrets"] = doppler.secrets

        # > oci injections
        di["oci_region"] = OCI_REGION
        di["compartment_id"] = extract_secret(
            secret=doppler.secrets,
            project=OCI_SECRETS_NAME,
            key=f"OCI_{OCI_ACCOUNT_NAME.upper()}_COMPARTMENT_PRODUCTION_ID",
        )
        di["oci_bucket_client"] = oci.object_storage.ObjectStorageClient(config)
        di["oci_lb_client"] = oci.load_balancer.LoadBalancerClient(config)
        di["oci_lb_composite_client"] = (
            oci.load_balancer.LoadBalancerClientCompositeOperations(
                client=di["oci_lb_client"]
            )
        )

        # > Slack
        di["slack_certificates_channel"] = "#certificates"

        func(*args, **kwargs)

    return wrapper

import os
import logging
from functools import wraps
from kink import di
from dopplersdk import DopplerSDK
# from slack_sdk import WebClient


def main_injection(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        
        # Define the OCI global config
        SECRETS_CLOUD_IAC_TOKEN = os.environ["SECRETS_CLOUD_IAC_MAIN_TOKEN"]

        # Initialize the OCI signer
        # signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

        # # Initialize the OCI clients
        # oci_bucket_client = oci.object_storage.ObjectStorageClient(config=OCI_CONFIG, signer=signer)
        # oci_lb_client = oci.load_balancer.LoadBalancerClient(config=OCI_CONFIG, signer=signer)

        # Initialize the Doppler client
        doppler_cloud_iac = DopplerSDK()
        doppler_cloud_iac.set_access_token(SECRETS_CLOUD_IAC_TOKEN)

        # * Pass data to DI
        di["secrets"] = doppler_cloud_iac.secrets
        # di['local_root_folder'] = '/etc/letsencrypt/live/'
        # di['files_to_save'] = ['cert.pem', 'chain.pem', 'fullchain.pem', 'privkey.pem']
        # di['oci_bucket_client'] = oci_bucket_client
        # di['oci_lb_client'] = oci_lb_client
        # di['namespace_name'] = oci_bucket_client.get_namespace().data
        # di['compartment_id'] = doppler_cloud_iac.secrets.get(
        #         project=SECRETS_CIM_PROJECT_NAME,
        #         config=SECRETS_CIM_CONFIG,
        #         name="OCI_POSEIDON_COMPARTMENT_PRODUCTION_ID",
        #     ).value["raw"]

        # di["slack_wc"] = WebClient(
        #     token=doppler_cloud_iac.secrets.get(
        #         project=SECRETS_CIM_PROJECT_NAME,
        #         config=SECRETS_CIM_CONFIG,
        #         name=SECRETS_CIM_SLACK_BOT_MAIN_TOKEN,
        #     ).value["raw"]
        # )
        # di["slack_channel_main"] = "#certificates"
        # di["slack_channel_errors"] = "#alerts"

        # Log message
        logging.info("DI intialized sucessfully.")

        # Return the function with DI
        return func(*args, **kwargs)

    return wrapper

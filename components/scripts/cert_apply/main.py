import os 
import logging
import oci
from kink import di
from core.di import main_injection
from core.oci_config import generate_cross_config, generate_local_config_and_signer
from core.functions import get_available_domain_names
from utils.secrets_extraction import extract_secret
# from core.functions import certificates_exists, sync_certificate, post_to_slack
# from utils.slack_blocks import block_success, block_error

# Intialize the logger
logging.basicConfig(level=logging.INFO)

# The main function
@main_injection
def main():

    # Add in a try catch to catch any errors
    try:

        # Logging the start of the script
        logging.info("Starting the certificate apply script")

        # Get a local oci config for Poseidon account (if running from Instance)
        oci_local_config, oci_signer = generate_local_config_and_signer()

        # Get cross oci config for Helios account
        oci_helios_config = generate_cross_config(
            account_name="helios",
            region="af-johannesburg-1",
        )

        # Instantiate the buckets client
        oci_bucket_client = oci.object_storage.ObjectStorageClient(
            config=oci_local_config, signer=oci_signer
        )

        # Get the available domain names
        available_domain_names = get_available_domain_names(
            oci_bucket_client=oci_bucket_client,
        )

        # Log the available domain names
        logging.info(f"Available domain names: {available_domain_names}")

        # Instantiate the load balancer client
        oci_lb_client = oci.load_balancer.LoadBalancerClient(config=oci_helios_config)

        # Get the helios compartment id
        helios_compartment_id = extract_secret(
            name="OCI_HELIOS_COMPARTMENT_PRODUCTION_ID"
        )

        # Get all load balancers in the compartment
        load_balancers = oci_lb_client.list_load_balancers(
            compartment_id=helios_compartment_id
        ).data

        # Get the load balancer called web
        load_balancer = [lb for lb in load_balancers if lb.display_name == "web"]

        # ! If the load balancer is not found, raise an exception
        if(len(load_balancer) == 0):
            raise Exception("No load balancer found with the name web")
        
        # Since this is a dict, get all the keys
        load_balancer_certificates_keys = [cert for cert in load_balancer[0].certificates]

        # Log the certificates attached to the LB
        logging.info(f"Certificates attached to the load balancer: {load_balancer_certificates_keys}")

        # Logging the end of the script
        logging.info("Certificate apply script completed successfully.")

    except Exception as e:
        # Log the error
        logging.error(f"An error occurred in the main script: {e}")

        # Post to slack
        # returned_slack_response = post_to_slack(blocks=block_error(e), channel=di['slack_channel_errors'],)

        # Logging the slack response
        # logging.info(f"Slack response: {returned_slack_response}")








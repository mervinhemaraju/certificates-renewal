import os
import oci
import logging
from kink import di
from functools import wraps


def main_injection(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        
        # Define the OCI global config
        OCI_CONFIG = {'region': 'uk-london-1'}

        # Initialize the OCI signer
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

        # Initialize the OCI object storage client
        oci_bucket_client = oci.object_storage.ObjectStorageClient(config=OCI_CONFIG, signer=signer)

        # * Pass data to DI
        di['oci_bucket_client'] = oci_bucket_client

        # Log message
        logging.info("DI intialized sucessfully.")

        # Return the function with DI
        return func(*args, **kwargs)

    return wrapper

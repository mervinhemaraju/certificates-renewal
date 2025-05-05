import os 
import logging
from kink import di
from di import main_injection
from functions import certificates_exists, sync_certificate

# Intialize the logger
logging.basicConfig(level=logging.INFO)

# def get_compartment_id():
#     metadata_url = "http://169.254.169.254/opc/v1/instance/"
#     response = requests.get(metadata_url, timeout=5)
#     instance_metadata = response.json()
#     return instance_metadata['compartmentId']

@main_injection
def main():

    # Logging the start of the script
    logging.info("Starting the certificate synchronization script")

    # Retrieve the available domains in the local_root_folder
    available_local_domains = [d for d in os.listdir(di['local_root_folder']) if os.path.isdir(os.path.join(di['local_root_folder'], d))]

    # Logging the available domains
    logging.info(f"Available local domains scanned: {available_local_domains}")

    # Iterate over the available domains
    for domain in available_local_domains:

        # Logging the domain
        logging.info(f"Processing domain: {domain}")

        # Check if all required files exist for the domain
        cert_present = certificates_exists(
            domain=domain,
        )

        # If the certificates do not exist, skip the domain
        if not cert_present:
            logging.error(f"Certificates do not exist for domain {domain}. Skipping...")
            continue

        # If the certificates exist, log the information
        logging.info(f"Certificates exist for domain {domain}. Proceeding with synchronization...")

        # Iterate over files to save
        for file_name in di['files_to_save'] :
            
            # Synchronize the certificate
            sync_certificate(
                domain=domain,
                file_name=file_name,
            )
        
    # Logging the end of the script
    logging.info("Certificate synchronization script completed successfully.")





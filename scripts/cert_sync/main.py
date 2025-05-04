import requests
import os 
import logging
from kink import di
from di import main_injection

# Intialize the logger
logging.basicConfig(level=logging.INFO)

def get_compartment_id():
    metadata_url = "http://169.254.169.254/opc/v1/instance/"
    response = requests.get(metadata_url, timeout=5)
    instance_metadata = response.json()
    return instance_metadata['compartmentId']

@main_injection
def main():

    # Logging the start of the script
    logging.info("Starting the certificate synchronization script")


    # TODO: Move to a config file / DI
    local_root_folder = '/etc/letsencrypt/live/'
    files_to_save = ['cert.pem', 'chain.pem', 'fullchain.pem', 'privkey.pem']

    # Check if the directory exists
    if not os.path.exists(local_root_folder):
        logging.error(f"Error: Directory {local_root_folder} does not exist")
        return

    # Retrieve the available domains in the local_root_folder
    available_local_domains = [d for d in os.listdir(local_root_folder) if os.path.isdir(os.path.join(local_root_folder, d))]

    # Logging the available domains
    logging.info(f"Available local domains scanned: {available_local_domains}")

    # Get the namespace name
    # namespace_name = di['oci_bucket_client'].get_namespace().data

    # Iterate over the available domains
    for domain in available_local_domains:

        # Logging the domain
        logging.info(f"Processing domain: {domain}")

        # Get the current stored files in the bucket
        list_objects_response = di['oci_bucket_client'].list_objects(
            namespace_name=di['namespace_name'],
            bucket_name="certificates",
            prefix=f"latest/{domain}/",
            delimiter='/'  
        )

        # Get the objects in a list
        remote_objects = list_objects_response.data.objects
        remote_object_names = [obj.name for obj in remote_objects]

        # Logging the remote objects
        logging.info(f"Remote objects obtained for domain {domain}: {remote_object_names}")

        # Iterate over files to save
        for file_name in files_to_save:

            # Build the remote location path
            remote_location_latest = f"latest/{domain}/{file_name}"
        
            # Get the full path to the certificate file
            cert_file_path = os.path.join(local_root_folder, domain, file_name)

            # Check if file exists
            if not os.path.exists(cert_file_path):
                logging.error(f"Certificate file not found for domain {domain}")
                continue
            
            # Read the certificate file
            with open(cert_file_path, 'rb') as cert_file:
                cert_content = cert_file.read()

            
            if remote_location_latest in remote_object_names:

                # Get the current stored file in the bucket
                remote_content = di['oci_bucket_client'].get_object(
                    namespace_name=di['namespace_name'],
                    bucket_name="certificates",
                    object_name=remote_location_latest
                ).data.content
            
                # TODO(Make sure to only do this for certain files)
                if(cert_content != remote_content):
                    logging.info(f"Certificate file {file_name} for domain {domain} is not up to date.")
                    
                    # Move the remove content to dumps
                    di['oci_bucket_client'].put_object(
                            namespace_name=di['namespace_name'],
                            bucket_name="certificates",
                            object_name=f"dumps/{domain}/{file_name}",
                            put_object_body=remote_content,
                            content_type='application/x-pem-file'
                        )

                    # Upload the new certificate        
                    di['oci_bucket_client'].put_object(
                            namespace_name=di['namespace_name'],
                            bucket_name="certificates",
                            object_name=remote_location_latest,
                            put_object_body=cert_content,
                            content_type='application/x-pem-file'
                        )    
                else:
                    logging.info(f"Certificate file {file_name} for domain {domain} is up to date.")
            else:
                logging.info(f"Certificate file {file_name} for domain {domain} does not exist in the bucket. Uploading it now.")
                
                # Upload the new certificate
                di['oci_bucket_client'].put_object(
                    namespace_name=di['namespace_name'],
                    bucket_name="certificates",
                    object_name=remote_location_latest,
                    put_object_body=cert_content,
                    content_type='application/x-pem-file'
                )
        
    # Logging the end of the script
    logging.info("Certificate synchronization script completed successfully.")





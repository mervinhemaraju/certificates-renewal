import oci
import os 
import logging
from kink import di
from di import main_injection

# Intialize the logger
logging.basicConfig(level=logging.INFO)

@main_injection
def main():
    # TODO: Move to a config file / DI
    compartment_id = ''
    remote_root_folder = ''
    local_root_folder = '/etc/letsencrypt/live/'
    files_to_save = ['fullchain.pem', 'privkey.pem']

    # Check if the directory exists
    if not os.path.exists(local_root_folder):
        print(f"Error: Directory {local_root_folder} does not exist")
        return

    # Retrieve the available domains in the local_root_folder
    available_local_domains = [d for d in os.listdir(local_root_folder) if os.path.isdir(os.path.join(local_root_folder, d))]

    # Get the namespace name
    namespace_name = di['oci_bucket_client'].get_namespace().data

    # Iterate over the available domains
    for domain in available_local_domains:

        # Iterate over files to save
        for file_name in files_to_save:
        
            # Get the full path to the certificate file
            cert_file_path = os.path.join(local_root_folder, domain, file_name)

            # Check if file exists
            if not os.path.exists(cert_file_path):
                logging.error(f"Certificate file not found for domain {domain}")
                continue
            
            # Read the certificate file
            with open(cert_file_path, 'rb') as cert_file:
                cert_content = cert_file.read()
                print(f"Read {len(cert_content)} bytes from {cert_file_path}")

            remote_directory = di['oci_bucket_client'].put_object(
                    namespace_name=namespace_name,
                    bucket_name="certificates",
                    object_name=f"{domain}/{file_name}",
                    put_object_body=cert_content,
                    content_type='application/x-pem-file'
                )
    

    # List objects in the bucket
    list_objects_response = di['oci_bucket_client'].list_objects(
        namespace_name=namespace_name,
        bucket_name="certificates",
        prefix="lb.mervinhemaraju.com/",
        delimiter='/'  
    )
    
    print(f"List objects response: {list_objects_response.data}")




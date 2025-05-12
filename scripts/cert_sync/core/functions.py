import os
import oci
import logging
from kink import di

def post_to_slack(blocks, thread_ts=None, channel=None):
    response = di["slack_wc"].chat_postMessage(
        channel=di["slack_channel_main"] if channel is None else channel,
        text="============",
        attachments=blocks,
        thread_ts=thread_ts,
    )
    return response, response["ts"]

def certificates_exists(domain: str) -> bool:

    """Check if the certificates exist in the local directory."""
    local_root_folder = di['local_root_folder']
    files_to_save = di['files_to_save']

    # Check if the local root folder exists
    if not os.path.exists(local_root_folder):
        logging.error(f"The local root folder '{local_root_folder}' does not exist.")
        return False

    # Check if all required files exist
    for file_name in files_to_save:
        file_path = os.path.join(local_root_folder, domain, file_name)
        if not os.path.exists(file_path):
            logging.error(f"The certificate file '{file_path}' does not exist.")
            return False

    # Return True if all files exist
    return True

def sync_certificate(domain: str, file_name: str) -> None:
    """Synchronize a single certificate file with the remote bucket."""

    # Get the local root folder and files to save
    remote_location_latest = f"latest/{domain}/{file_name}"
    remote_location_dumps = f"dumps/{domain}/{file_name}"
    cert_file_path = os.path.join(di['local_root_folder'], domain, file_name)
    
    # Read local certificate
    with open(cert_file_path, 'rb') as cert_file:
        cert_local_content = cert_file.read()

    try:
        
        # Check if file exists in bucket
        cert_remote_content = di['oci_bucket_client'].get_object(
            namespace_name=di['namespace_name'],
            bucket_name="certificates",
            object_name=remote_location_latest
        ).data.content

        # Compare contents
        if cert_local_content != cert_remote_content:
            logging.info(f"Updating certificate: {file_name} for {domain}")
            
            # Backup existing certificate
            di['oci_bucket_client'].put_object(
                namespace_name=di['namespace_name'],
                bucket_name="certificates",
                object_name=remote_location_dumps,
                put_object_body=cert_remote_content,
                content_type='application/x-pem-file'
            )
            
            # Upload new certificate
            di['oci_bucket_client'].put_object(
                namespace_name=di['namespace_name'],
                bucket_name="certificates",
                object_name=remote_location_latest,
                put_object_body=cert_local_content,
                content_type='application/x-pem-file'
            )

            # Log that the certificate was updated
            logging.info(f"Certificate has been updated: {file_name} for {domain}")

        else:

            # Log that the certificate is up to date
            logging.info(f"Certificate is up to date: {file_name} for {domain}")

    except oci.exceptions.ServiceError as se:

        if(se.status == 404):
            # Log error that file doesn't exist
            logging.info(f"Uploading new certificate: {file_name} for {domain}")

            # Upload new certificate to the bucket
            di['oci_bucket_client'].put_object(
                namespace_name=di['namespace_name'],
                bucket_name="certificates",
                object_name=remote_location_latest,
                put_object_body=cert_local_content,
                content_type='application/x-pem-file'
            )
        else:
            # Log other errors
            logging.error(f"Service error occurred while uploading {file_name} for {domain}: {se.code} - {se.message}")

    except Exception as e:
        # Log other errors
        logging.error(f"An error occurred while uploading {file_name} for {domain}: {str(e)}")
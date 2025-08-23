import oci
import logging
from pathlib import Path
from kink import di
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend


def extract_secret(secret, project, key):
    return secret.get(
        project=project,
        config="prd",
        name=key,
    ).value["raw"]


def load_cloudflare_ini_file():
    # Get the cloudflare token
    cloudflare_token = extract_secret(
        secret=di["secrets"], project="apps-creds", key="CLOUDFLARE_TERRAFORM_TOKEN"
    )

    # Create the cloudflare.ini file
    with open(di["cloudflare_ini_file"], "w") as f:
        f.write(f"dns_cloudflare_api_token = {cloudflare_token}\n")


def check_certificate_expiry(certificate: bytes, days_before_expiration: int = 30):
    """
    Check if certificate exists and needs renewal
    """

    try:
        # Parse certificate
        cert = x509.load_pem_x509_certificate(certificate, default_backend())

        # Calculate days until expiry
        expiry_date = cert.not_valid_after
        days_remaining = (expiry_date - datetime.now()).days

        print(
            f"Current certificate expires on {expiry_date}. Days remaining: {days_remaining}"
        )

        # Check if renewal is needed
        needs_renewal = days_remaining <= days_before_expiration

        return needs_renewal, days_remaining

    except Exception as e:
        print(f"Error checking certificate: {str(e)}")
        return True, 0


def oci_download_object(
    namespace_name: str,
    bucket_name: str,
    object_name: str,
) -> bytes:
    logging.info(f"Downloading object: {object_name} from bucket: {bucket_name}")

    # Download the object
    get_object_response = di["oci_bucket_client"].get_object(
        namespace_name=namespace_name, bucket_name=bucket_name, object_name=object_name
    )

    # Get the content
    object_content = get_object_response.data.content

    logging.info(f"Successfully downloaded {object_name} ({len(object_content)} bytes)")

    return object_content


def oci_upload_object(
    namespace_name: str,
    bucket_name: str,
    object_name: str,
    object_content: bytes,
    content_type: str = "application/octet-stream",
) -> None:
    logging.info(f"Uploading object: {object_name} to bucket: {bucket_name}")

    # Upload the object
    di["oci_bucket_client"].put_object(
        namespace_name=namespace_name,
        bucket_name=bucket_name,
        object_name=object_name,
        put_object_body=object_content,
        content_type=content_type,
    )

    logging.info(f"Successfully uploaded {object_name}")


def oci_get_load_balancer_details():
    # Query the load balancers
    load_balancers_response = (
        di["oci_lb_client"]
        .list_load_balancers(
            compartment_id=di["compartment_id"],
            display_name=di["load_balancer_name"],
        )
        .data
    )

    # Check if load balancer exists
    if len(load_balancers_response) < 1:
        raise Exception(
            f"The load balancer {di['load_balancer_name']} cannot be found."
        )

    # Get the load balancer id
    lb_id = load_balancers_response[0].id

    # Get the ssl listener names
    ssl_listeners = [
        config
        for _, config in load_balancers_response[0].listeners.items()
        if config.ssl_configuration is not None
    ]

    # Return the load balancer id
    return lb_id, ssl_listeners


def oci_create_lb_certificate(lb_id: str, cert: str, ca: str, prinvkey: str):
    # Generate a name for the certificate
    name = (
        f"san-mervinhemaraju.com-plagueworks.org-{datetime.now().strftime('%Y.%m.%d')}"
    )

    # Create the certificate and wait for state
    response = di["oci_lb_composite_client"].create_certificate_and_wait_for_state(
        load_balancer_id=lb_id,
        create_certificate_details=oci.load_balancer.models.CreateCertificateDetails(
            certificate_name=name,
            ca_certificate=ca,
            public_certificate=cert,
            private_key=prinvkey,
        ),
        wait_for_states=["SUCCEEDED", "FAILED"],
        waiter_kwargs={
            "max_interval_seconds": 7,
            "max_wait_seconds": 100,
        },
    )

    # Log info
    logging.info(f"Response for creating certificate -> {response.data}")

    # Check if the work request failed
    if response.data.lifecycle_state != "SUCCEEDED":
        error_messages = [error.message for error in response.data.error_details]
        raise Exception(f"Certificate creation failed: {', '.join(error_messages)}")

    # Log the info
    logging.info(f"Certificate '{name}' created successfully")

    # Return the certificate name
    return name


def oci_update_ssl_listeners(
    listeners: list[str], load_balancer_id: str, certificate_name: str
):
    # Iterate through each listeners
    for listener in listeners:
        # Update the listener
        response = di["oci_lb_composite_client"].update_listener_and_wait_for_state(
            load_balancer_id=load_balancer_id,
            listener_name=listener.name,
            update_listener_details=oci.load_balancer.models.UpdateListenerDetails(
                default_backend_set_name=listener.default_backend_set_name,
                port=listener.port,
                protocol=listener.protocol,
                ssl_configuration=oci.load_balancer.models.SSLConfigurationDetails(
                    certificate_name=certificate_name,
                    verify_depth=listener.ssl_configuration.verify_depth,
                    # protocols=["TLSv1.2", "TLSv1.3"],
                    protocols=listener.ssl_configuration.protocols,
                    server_order_preference=listener.ssl_configuration.server_order_preference,
                    has_session_resumption=listener.ssl_configuration.has_session_resumption,
                    cipher_suite_name=listener.ssl_configuration.cipher_suite_name,
                    verify_peer_certificate=listener.ssl_configuration.verify_peer_certificate,
                ),
            ),
            wait_for_states=["SUCCEEDED", "FAILED"],
            waiter_kwargs={
                "max_interval_seconds": 7,
                "max_wait_seconds": 100,
            },
        )

        # Log info
        logging.info(f"Response for updating listener {listener.name} -> {response}")

        # Check if the work request failed
        if response.data.lifecycle_state == "FAILED":
            error_messages = [error.message for error in response.data.error_details]
            raise Exception(
                f"Listener '{listener.name}' update failed: {', '.join(error_messages)}"
            )

    # Log info
    logging.info(
        f"Listeners updated successfully with certificate '{certificate_name}'"
    )


def oci_backup_certificates(
    namespace_name: str,
    bucket_certificate_live_path: str,
    bucket_certificate_backup_path: str,
):
    """
    Backup certificates from live path to backup path via local working directory.
    Downloads all files from live path, saves them locally, then uploads to backup path.
    """

    local_backup_path = Path(di["working_directory"]) / bucket_certificate_backup_path

    # Create the local backup directory
    local_backup_path.mkdir(parents=True, exist_ok=True)

    logging.info(
        f"Starting certificate backup from {bucket_certificate_live_path} to {bucket_certificate_backup_path}"
    )

    # Step 1: Download all certificate files from live path to local directory
    for cert_file in di["certificate_files"]:
        live_object_path = f"{bucket_certificate_live_path}/{cert_file}"
        local_file_path = local_backup_path / cert_file

        logging.info(f"Downloading {live_object_path} to {local_file_path}")

        # Download the certificate file
        cert_content = oci_download_object(
            namespace_name=namespace_name,
            bucket_name=di["bucket_certificate_name"],
            object_name=live_object_path,
        )

        # Save to local file
        local_file_path.write_bytes(cert_content)

        logging.info(f"Successfully downloaded and saved {cert_file}")

    # Step 2: Upload all files from local directory to backup path
    for cert_file in di["certificate_files"]:
        local_file_path = local_backup_path / cert_file
        backup_object_path = f"{bucket_certificate_backup_path}/{cert_file}"

        logging.info(f"Uploading {local_file_path} to {backup_object_path}")

        # Read the local file content
        cert_content = local_file_path.read_bytes()

        # Upload to backup location
        oci_upload_object(
            namespace_name=namespace_name,
            bucket_name=di["bucket_certificate_name"],
            object_name=backup_object_path,
            object_content=cert_content,
            content_type="application/x-pem-file",
        )

        logging.info(f"Successfully uploaded {cert_file} to backup location")

    logging.info(
        f"Certificate backup completed successfully to {bucket_certificate_backup_path}"
    )

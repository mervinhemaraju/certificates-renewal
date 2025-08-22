import logging
from kink import di
from pathlib import Path
from certbot._internal import main as certbot_main
from functions import (
    load_cloudflare_ini_file,
    check_certificate_expiry,
    oci_download_object,
    oci_upload_object,
    oci_get_load_balancer_details,
    oci_create_lb_certificate,
    oci_update_ssl_listeners,
    oci_backup_certificates,
)
from di import main_injection


# WORKING_DIRECTORY = "/tmp"  # Activate when using lambda
WORKING_DIRECTORY = "tmp"
CLOUDFLARE_INI_FILE = f"{WORKING_DIRECTORY}/cloudflare.ini"
LOCAL_CERTIFICATE_DIRECTORY = f"{WORKING_DIRECTORY}/live/mervinhemaraju.com"
BUCKET_CERTIFICATE_NAME = "certificates"
BUCKET_CERTIFICATE_DIRECTORY_LIVE = "live/san-mervinhemaraju-com-plagueworks-org"
BUCKET_CERTIFICATE_DIRECTORY_BACKUP = "live/san-mervinhemaraju-com-plagueworks-org"
LOAD_BALANCER_NAME = "web"


@main_injection
def main(event, context):
    # Log script starting
    logging.info(f"Certificate renew starting with event: {event}")
    logging.info(f"Certificate renew starting with context: {context}")

    # Retrieve event contents
    force_renew = event.get("force_renew", False)

    # Log ingo
    logging.info(f"Force renew is set to -> {force_renew}")

    # Load the cloudflare ini file
    load_cloudflare_ini_file(cloudflare_ini_file_path=CLOUDFLARE_INI_FILE)

    # Get the OCI namespace
    oci_namespace = di["oci_bucket_client"].get_namespace().data

    # Get certificate from bucket
    get_certificates_response = oci_download_object(
        namespace_name=oci_namespace,
        bucket_name=BUCKET_CERTIFICATE_NAME,
        object_name=f"{BUCKET_CERTIFICATE_DIRECTORY_LIVE}/cert.pem",
    )

    # (
    #     di["oci_bucket_client"]
    #     .get_object(
    #         namespace_name=oci_namespace,
    #         bucket_name=BUCKET_CERTIFICATE_NAME,
    #         object_name=f"{BUCKET_CERTIFICATE_DIRECTORY_LIVE}/cert.pem",
    #     )
    #     .data
    # )

    # If certificate doesn't exist, raise error
    if get_certificates_response.status_code != 200:
        raise Exception(
            f"Cannot find the certificate file in -> {BUCKET_CERTIFICATE_DIRECTORY_LIVE}"
        )

    # Get the certificate content
    certificate_content = get_certificates_response.content

    # Check whether the certificate is expiring
    needs_renewal, days_remaining = check_certificate_expiry(
        certificate=certificate_content
    )

    # Log info
    logging.info(f"Needs renewwal: {needs_renewal}")
    logging.info(f"Certificate expires in {days_remaining} days. Renewing...")

    # Check if renewal is needed or force_renew is set
    if needs_renewal or force_renew:
        # certbot_args = [
        #     "certonly",
        #     "--non-interactive",
        #     "--agree-tos",
        #     "--email",
        #     EMAIL,
        #     "--dns-cloudflare",
        #     "--dns-cloudflare-credentials",
        #     CLOUDFLARE_INI_FILE,
        #     "--dns-cloudflare-propagation-seconds",
        #     "30",
        #     "--preferred-challenges",
        #     "dns-01",
        #     "-d",
        #     "*.mervinhemaraju.com",
        #     "-d",
        #     "*.plagueworks.org",
        #     "--config-dir",
        #     WORKING_DIRECTORY,
        #     "--work-dir",
        #     WORKING_DIRECTORY,
        #     "--logs-dir",
        #     WORKING_DIRECTORY,
        #     # '--force-renewal'  # Force renewal even if cert is valid
        # ]

        # # Run certbot
        # result = certbot_main.main(certbot_args)

        # print(result)

        # Load the generated certificates
        local_cert_content = Path(
            f"{LOCAL_CERTIFICATE_DIRECTORY}/cert.pem",
        ).read_text()
        local_chain_content = Path(
            f"{LOCAL_CERTIFICATE_DIRECTORY}/chain.pem",
        ).read_text()
        local_fullchain_content = Path(
            f"{LOCAL_CERTIFICATE_DIRECTORY}/fullchain.pem",
        ).read_text()
        local_privkey_content = Path(
            f"{LOCAL_CERTIFICATE_DIRECTORY}/privkey.pem",
        ).read_text()

        # Backup the currennt live certificates in the bucket
        oci_backup_certificates(
            namespace_name=oci_namespace,
            bucket_name=BUCKET_CERTIFICATE_NAME,
            bucket_certificate_live_path=BUCKET_CERTIFICATE_DIRECTORY_LIVE,
            working_directory_path=WORKING_DIRECTORY,
        )
        return
        # TODO(Add new certificates to bucket)

        # Get the load balacner id
        load_balancer_id, ssl_listeners = oci_get_load_balancer_details(
            load_balancer_name=LOAD_BALANCER_NAME
        )

        # Log information
        logging.info(f"Load balancer ID is -> {load_balancer_id}")
        logging.info(f"SSL listeners obtained are -> {ssl_listeners}")

        # Create the certificate in the load balancer
        certificate_name = oci_create_lb_certificate(
            lb_id=load_balancer_id,
            cert=local_cert_content,
            ca=local_chain_content,
            prinvkey=local_privkey_content,
        )

        # For all ssl listeners, update the configuration
        oci_update_ssl_listeners(
            listeners=ssl_listeners,
            load_balancer_id=load_balancer_id,
            certificate_name=certificate_name,
        )

        # TODO(Cleanup)

        # with open(CERT_FILE, "r") as cert_file:
        # new_cert = cert_file.read()

        # Check whether the certificate is expiring
        # needs_renewal, days_remaining = check_certificate_expiry(
        #     certificate=local_cert_content.encode()
        # )

        # # Log info
        # logging.info(f"New cert needs renewal: {needs_renewal}")

        # logging.info(f"New certificate expires in {days_remaining} days.")

    logging.info("End of script")
    # TODO(Add slack notifications)

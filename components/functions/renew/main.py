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


@main_injection
def main(event, context):
    # Add main try except
    # to catch all errors inside the app
    try:
        # Log script starting
        logging.info(f"Certificate renew starting with event: {event}")
        logging.info(f"Certificate renew starting with context: {context}")

        # Retrieve event contents
        debug = event.get("debug", False)
        force_renew = event.get("force_renew", False)

        # ! If this is a debug, re-write the working
        if debug:
            di["working_directory"] = "/" + di["working_directory"]

        # Set working directory dependent vars here
        di["cloudflare_ini_file"] = f"{di['working_directory']}/cloudflare.ini"
        di["local_certificate_directory"] = (
            f"{di['working_directory']}/live/mervinhemaraju.com"
        )

        # Log info
        logging.info(f"Working directory is set to {di['working_directory']}")
        logging.info(f"Force renew is set to -> {force_renew}")

        # Load the cloudflare ini file
        load_cloudflare_ini_file()

        # Get the OCI namespace
        oci_namespace = di["oci_bucket_client"].get_namespace().data

        # Get certificate from bucket
        certificate_content = oci_download_object(
            namespace_name=oci_namespace,
            bucket_name=di["bucket_certificate_name"],
            object_name=f"{di['bucket_certificate_directory_live']}/cert.pem",
        )

        # Check whether the certificate is expiring
        needs_renewal, days_remaining = check_certificate_expiry(
            certificate=certificate_content
        )

        # Log info
        logging.info(f"Needs renewwal: {needs_renewal}")
        logging.info(f"Certificate expires in {days_remaining} days. Renewing...")

        # Check if renewal is needed or force_renew is set
        if needs_renewal or force_renew:
            # TODO(Reactivate when done)
            certbot_args = [
                "certonly",
                "--non-interactive",
                "--agree-tos",
                "--email",
                di["owner_email"],
                "--dns-cloudflare",
                "--dns-cloudflare-credentials",
                di["cloudflare_ini_file"],
                "--dns-cloudflare-propagation-seconds",
                "30",
                "--preferred-challenges",
                "dns-01",
                "-d",
                "*.mervinhemaraju.com",
                "-d",
                "*.plagueworks.org",
                "--config-dir",
                di["working_directory"],
                "--work-dir",
                di["working_directory"],
                "--logs-dir",
                di["working_directory"],
                # '--force-renewal'  # Force renewal even if cert is valid
            ]

            # Run the certbot command
            result = certbot_main.main(certbot_args)

            # Log info
            logging.info(result)

            # Load the generated certificates in a map as below:
            # {
            #   "cert.pem": "<CONTENT>"
            #   "chain.pem": "<CONTENT>"
            #   "fullchain.pem": "<CONTENT>"
            #   "privkey.pem": "<CONTENT>"
            # }
            local_certificate_contents = {
                cert_name: Path(
                    f"{di['local_certificate_directory']}/{cert_name}",
                ).read_text()
                for cert_name in di["certificate_files"]
            }

            # Backup the currennt live certificates in the bucket
            oci_backup_certificates(
                namespace_name=oci_namespace,
                bucket_certificate_live_path=di["bucket_certificate_directory_live"],
                bucket_certificate_backup_path=di[
                    "bucket_certificate_directory_backup"
                ],
            )

            # Upload the new certificates to the bucket
            for cert_name, cert_content in local_certificate_contents.items():
                # Construct remote file name
                remote_cert_file_name = (
                    f"{di['bucket_certificate_directory_live']}/{cert_name}"
                )

                # Upload the file to the bucket
                oci_upload_object(
                    namespace_name=oci_namespace,
                    bucket_name=di["bucket_certificate_name"],
                    object_name=remote_cert_file_name,
                    object_content=cert_content,
                )

            # Get the load balancer id
            load_balancer_id, ssl_listeners = oci_get_load_balancer_details()

            # Log information
            logging.info(f"Load balancer ID is -> {load_balancer_id}")
            logging.info(f"SSL listeners obtained are -> {ssl_listeners}")

            # Create the certificate in the load balancer
            certificate_name = oci_create_lb_certificate(
                lb_id=load_balancer_id,
                cert=local_certificate_contents["cert.pem"],
                ca=local_certificate_contents["chain.pem"],
                prinvkey=local_certificate_contents["privkey.pem"],
            )

            # For all ssl listeners, update the configuration
            oci_update_ssl_listeners(
                listeners=ssl_listeners,
                load_balancer_id=load_balancer_id,
                certificate_name=certificate_name,
            )

            # TODO(Cleanup files)

            # TODO(Check renew date on the new cert and print)

        # Log info
        logging.info("Renew script has successfully completed.")
        # TODO(Add slack notifications)

    except Exception as e:
        # Log error message
        logging.error("Fatal error occurred in script:")
        logging.error(str(e))

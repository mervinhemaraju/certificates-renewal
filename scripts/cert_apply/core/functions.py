

def get_available_domain_names(oci_bucket_client, prefix="latest/", delimiter="/"):
    """
    Get the available domain names from the OCI bucket.
    """

    # List objects in the latest folder
    list_objects = oci_bucket_client.list_objects(
        namespace_name=oci_bucket_client.get_namespace().data,
        bucket_name="certificates",
        prefix=prefix,
        delimiter=delimiter
    )
    
    # Retrieve the domain names present and return them
    return [prefix.replace('latest/', '').strip('/') for prefix in list_objects.data.prefixes]
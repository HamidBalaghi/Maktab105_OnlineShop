import os
import uuid


def get_image_upload_path(instance, filename):
    # Extracting brand and product names
    brand = instance.product.brand
    product_name = instance.product.name
    # Removing special characters and spaces from brand and product names for a clean filename
    clean_brand = ''.join(e for e in brand if e.isalnum())
    clean_product_name = ''.join(e for e in product_name if e.isalnum())
    # Getting the file extension
    ext = filename.split('.')[-1]
    # Generating UUID4 filename
    uuid_filename = f"{uuid.uuid4().hex}.{ext}"
    # Constructing the upload path
    return os.path.join('products', clean_brand, clean_product_name, uuid_filename)

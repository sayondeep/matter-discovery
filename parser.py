def parse_hex(hex_string):
    # Ensure the hex string is in the correct format and length
    if len(hex_string) != 16:
        raise ValueError("Hex string must be exactly 16 characters long")

    # Convert the hex string into bytes
    byte_data = bytes.fromhex(hex_string)

    # Extract values according to the structure
    op_code = byte_data[0]

    # Advertisement version and Discriminator
    ad_version_discriminator = (byte_data[1] | (byte_data[2] << 8))
    advertisement_version = ad_version_discriminator & 0xF000
    discriminator = ad_version_discriminator & 0x0FFF
    # Vendor ID and Product ID
    vendor_id = (byte_data[3] | (byte_data[4] << 8))
    product_id = (byte_data[5] | (byte_data[6] << 8))

    # Additional Data Flag and Using Extended Announcement Flag
    additional_data_flag = (byte_data[7] & 0x01) >> 0
    using_extended_announcement_flag = (byte_data[7] & 0x02) >> 1

    # Reserved bits
    reserved_bits = (byte_data[7] & 0xFC) >> 2

    return {
        "Matter BLE OpCode": hex(op_code),
        "Advertisement version": hex(advertisement_version),
        "Discriminator": hex(discriminator),
        "Vendor ID": hex(vendor_id),
        "Product ID": hex(product_id),
        "Additional Data Flag": additional_data_flag,
        "Using Extended Announcement Flag": using_extended_announcement_flag,
        "Reserved bits": hex(reserved_bits)
    }

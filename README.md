## Matter-Discovery
Discover matter commissionable devices over ble.
## Python tool to discover commissionable matter devices over Ble

Generates and parses Manual Pairing Code and QR Code

#### example usage:
-   Discover

```
python3 discover.py MT:U9VJ0OMV172PX813210   
```

-   Parse

```
python3 setup_payload.py parse MT:U9VJ0OMV172PX813210
python3 setup_payload.py parse 34970112332
```

-   Generate

```
python3 setup_payload.py generate --help
python3 setup_payload.py generate -d 3840 -p 20202021
python3 setup_payload.py generate -d 3840 -p 20202021 --vendor-id 65521 --product-id 32768 -cf 0 -dm 2
```

For more details please refer Matter Specification

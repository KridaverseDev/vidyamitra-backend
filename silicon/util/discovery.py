# Copyright 2021 Pants project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).


DEV_PORTS = {"silicon._microservices.admin": 8000}


def get_dev_port(service: str) -> int:
    try:
        return DEV_PORTS[service]
    except KeyError:
        raise ValueError(f"No dev port found for service {service}")

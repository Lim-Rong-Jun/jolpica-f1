import os

import requests


def is_ec2_linux() -> bool:
    """Detect if we are running on an EC2 Linux Instance
    See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/identify_ec2_instances.html
    """
    if os.path.isfile("/sys/hypervisor/uuid"):
        with open("/sys/hypervisor/uuid") as f:
            uuid = f.read()
            return uuid.startswith("ec2")
    return False


def get_ec2_token() -> str:
    """Set the autorization token to live for 6 hours (maximum)"""
    headers = {
        "X-aws-ec2-metadata-token-ttl-seconds": "21600",
    }
    response = requests.put("http://169.254.169.254/latest/api/token", headers=headers, timeout=60)
    return response.text


def get_linux_ec2_private_ip() -> None | str:
    """Get the private IP Address of the machine if running on an EC2 linux server.
    See https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
    """

    if not is_ec2_linux():
        return None
    try:
        token = get_ec2_token()
        headers = {
            "X-aws-ec2-metadata-token": f"{token}",
        }
        response = requests.get("http://169.254.169.254/latest/meta-data/local-ipv4", headers=headers, timeout=60)
        return response.text
    except Exception:
        return None
    finally:
        if response:
            response.close()
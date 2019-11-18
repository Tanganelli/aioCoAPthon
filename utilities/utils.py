import random
import string

from typing import Tuple, List, Optional

__author__ = 'Giacomo Tanganelli'


def byte_len(number: int) -> int:
    """
    Get the number of byte needed to encode the int passed.

    :param number: the int to be converted
    :return: the number of bits needed to encode the int passed.
    """
    length = 0
    while number:
        number >>= 1
        length += 1
    if length > 0:
        if length % 8 != 0:
            length = int(length / 8) + 1
        else:
            length = int(length / 8)
    return length


def parse_blockwise(value: int) -> Tuple[int, int, int]:
    """
    Parse Blockwise option.

    :param value: option value
    :return: num, m, size
    """

    length = byte_len(value)
    if length == 1:
        num = value & 0xF0
        num >>= 4
        m = value & 0x08
        m >>= 3
        size = value & 0x07
    elif length == 2:
        num = value & 0xFFF0
        num >>= 4
        m = value & 0x0008
        m >>= 3
        size = value & 0x0007
    else:
        num = value & 0xFFFFF0
        num >>= 4
        m = value & 0x000008
        m >>= 3
        size = value & 0x000007
    return num, int(m), pow(2, (size + 4))


def str_append_hash(*args):
    """ Convert each argument to a lower case string, appended, then hash """
    ret_hash = ""
    for i in args:
        ret_hash += str(i).lower()

    return hash(ret_hash)


class Tree(object):
    def __init__(self):
        self.tree = {}

    def dump(self):
        """
        Get all the paths registered in the server.

        :return: registered resources.
        """
        return sorted(list(self.tree.keys()))

    def get_ascending(self, path: str) -> List["Resource"]:
        ret = []
        for key, value in self.tree.items():
            if path.startswith(key):
                ret.append(value)

        return ret

    def __getitem__(self, item):
        return self.tree[item]

    def __setitem__(self, key, value):
        self.tree[key] = value

    def __delitem__(self, key):
        del self.tree[key]


def parse_uri_query(q: str) -> Optional[Tuple[str, str]]:
    tmp = q.split("=")
    if len(tmp) == 2:
        return tmp[0], tmp[1]
    return None


def generate_random_hex(size):
    return ''.join(chr(random.randint(0, 255)) for _ in range(size))


def generate_random_str(size):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for _ in range(size))


class CoAPPayload(object):
    def __init__(self, payload: bytes = None):
        self._payload = payload

    def __str__(self):
        if self._payload is None:
            return ""
        try:
            return self._payload.decode("utf-8")
        except UnicodeDecodeError:
            import base64
            return base64.b64encode(self._payload)

    def __add__(self, other):
        if isinstance(other, str):
            other = other.encode("utf-8")
        self._payload += other
        return self._payload

    def __radd__(self, other):
        if other is None:
            other = ""
        if isinstance(other, str):
            other = other.encode("utf-8")
        self._payload = other + self._payload
        return self._payload

    def __len__(self):
        if self._payload is None:
            return 0
        return len(self._payload)

    def __getitem__(self, item):
        if self._payload is None:
            return ""
        return self._payload[item]

    def decode(self, encoding="utf-8") -> str:
        if self._payload is not None:
            return self._payload.decode(encoding)
        else:
            return ""

    @property
    def raw(self) -> bytes:
        return self._payload

    def __eq__(self, other):
        return self._payload == other.raw

    @property
    def payload(self):
        """
        Get the payload of the resource

        :return: the payload.
        """
        return self._payload

    @payload.setter
    def payload(self, p: bytes):
        """
        Set the payload of the resource.

        :param p: the new payload
        """
        if isinstance(p, str):
            p = p.encode("utf-8")
        self._payload = p


def usage():  # pragma: no cover
    print("server.py -i <ip address> -p <port>")


def parse_arguments(argv):
    import getopt
    import sys
    ip = "0.0.0.0"
    port = 5683
    try:

        opts, args = getopt.getopt(argv, "hi:p:", ["ip=", "port="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-p", "--port"):
            port = int(arg)

    return ip, port

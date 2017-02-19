import logging
import socket
import sys
import netifaces

from GUI import MainWindow


def setup_logging(debug=False):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)
    logging.getLogger('zeroconf').setLevel(log_level)


def get_ip_address(logger=None):
    try:
        gw = netifaces.gateways()['default'][netifaces.AF_INET]
    except KeyError:
        gw = netifaces.gateways()[netifaces.AF_INET][0]
    gw_ip = '.'.join(gw[0].split('.')[:3])
    gw_iface = gw[1]
    addrs = netifaces.ifaddresses(gw_iface)
    addr = addrs[netifaces.AF_INET][0]
    ip = addr['addr']

    if logger is not None:
        logger.info("ip: " + ip + " interface: " + gw_iface)
    return ip, gw_iface


if __name__ == "__main__":
    debug_mode = False
    if len(sys.argv) > 1:
        debug_mode = sys.argv[1:] == ['--debug']
    setup_logging(debug_mode)
    logger = logging.getLogger(__name__)

    local_ip, interface = get_ip_address(logger)

    main_window = MainWindow(ip=local_ip)
    main_window.mainloop()

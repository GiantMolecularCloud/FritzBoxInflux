"""
FritzBox to InfluxDB

author: Nico Krieger (GiantMolecularCloud)

This script uses environment variables for authentification and settings:
FB_IP           IP address of the FritzBox
FB_PORT         port to use for the connection
FB_USER         FritzBox user to use for the connection
FB_PASSWD       password for FritzBox user FB_USER
FB_ID           name of the InfluxDB database to use
FB_DSL          is the FritzBox connected via DSL?
INFLUX_IP       IP address of the machine InfluxDB is running on
INFLUX_PORT     port to connect to InfluxDB
INFLUX_USER     user to access the InfluxDB database
INFLUX_PASSWD   password to access the InfluxDB database
SAMPLE_TIME     time to wait before getting the next sample
"""

import logging
import os
import time

from influxdb import InfluxDBClient

from .fritzbox_data import FritzBoxData
from .io import write_database

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")

# read in environment variables, set some defaults if env vars are not defined
FB_ID = os.getenv("FB_ID") or "FritzBox"
INFLUX_IP = os.getenv("INFLUX_IP", "127.0.0.1")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", 8086))
INFLUX_USER = os.getenv("INFLUX_USER", "root")
INFLUX_PASSWD = os.getenv("INFLUX_PASSWD", "root")
SAMPLE_TIME = int(os.getenv("SAMPLE_TIME", 60))


def main(argv: list[str] | None = None) -> None:
    log.info("Starting FritzBox to InfluxDB data logger.")
    fb = FritzBoxData()
    fb.connect()

    # The first read always misses some information.
    # Unknown why that happens. Performing a dummy read.
    fb.read_data()

    # connect to InfluxDB
    client = InfluxDBClient(host=INFLUX_IP, port=INFLUX_PORT, username=INFLUX_USER, password=INFLUX_PASSWD)
    log.info("Connected to InfluxDB.")

    # create new database if necessary
    if FB_ID not in [db["name"] for db in client.get_list_database()]:
        client.create_database(FB_ID)
        log.info(f"Created new InfluxDB database '{FB_ID}'.")

    # select current database
    client.switch_database(FB_ID)
    log.info(f"Using InfluxDB database '{FB_ID}'.")

    # continuously read data and write to InfluxDB
    try:
        while True:

            try:
                write_database(client=client, data=fb.get_influx_data())
            except Exception as e:
                print(e)
            finally:
                time.sleep(SAMPLE_TIME)

    except KeyboardInterrupt:
        log.error("Program stopped by keyboard interrupt [CTRL_C] by user.")


if __name__ == "__main__":
    main()

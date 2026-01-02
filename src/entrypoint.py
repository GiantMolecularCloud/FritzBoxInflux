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

import os
import time
from datetime import datetime

from influxdb import InfluxDBClient

from .fritzbox_data import FritzBoxData
from .io import write_database


# read in environment variables, set some defaults if env vars are not defined
FB_IP         = os.getenv('FB_IP') or '192.168.178.1'
FB_PORT       = os.getenv('FB_PORT') or '49000'
FB_USER       = os.getenv('FB_USER')
FB_PASSWD     = os.getenv('FB_PASSWD')
FB_ID         = os.getenv('FB_ID') or 'FritzBox'
FB_DSL        = bool(os.getenv('FB_DSL')) or True
INFLUX_IP     = os.getenv('INFLUX_IP') or '127.0.0.1'
INFLUX_PORT   = int(os.getenv('INFLUX_PORT') or 8086)
INFLUX_USER   = os.getenv('INFLUX_USER') or 'root'
INFLUX_PASSWD = os.getenv('INFLUX_PASSWD') or 'root'
SAMPLE_TIME   = int(os.getenv('SAMPLE_TIME') or 60)



def main(argv: list[str] | None = None) -> None:
    FB = FritzBoxData()
    FB.connect()

    # The first read always misses some information. 
    # Unknown why that happens. Performing a dummy read.
    FB.read_data()

    # connect to InfluxDB
    client = InfluxDBClient(
        host     = INFLUX_IP,
        port     = INFLUX_PORT,
        username = INFLUX_USER,
        password = INFLUX_PASSWD
    )

    # create new database if necessary
    if not FB_ID in [db['name'] for db in client.get_list_database()]:
        client.create_database(FB_ID)

    # select current database
    client.switch_database(FB_ID)

    # continuously read data and write to InfluxDB
    try:
        while True:

            try:
                write_database(
                    client = client,
                    data   = FB.get_influx_data()
                )
            except Exception as e:
                print(e)
            finally:
                time.sleep(SAMPLE_TIME)

    except KeyboardInterrupt:
        print (datetime.now(), "  Program stopped by keyboard interrupt [CTRL_C] by user. ")

import logging

import influxdb.exceptions as inexc
from influxdb import InfluxDBClient


log = logging.getLogger(__name__)

def write_database(client: InfluxDBClient, data: list[dict]) -> None:
    """
    Writes a given data record to the database and prints unexpected results.
    Copy/paste from my homeclimate code.
    """
    try:
        iresponse = client.write_points(data)
        if not iresponse:
            log.error("Sending data to database failed. Response: ", iresponse)
        else:
            log.debug("Data successfully written to database.")
    except inexc.InfluxDBServerError as e:
        log.error("Sending data to database failed due to timeout.", e)
        pass
    except Exception as e:
        log.error("Encountered unknown error.", e)
        pass

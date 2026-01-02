import influxdb.exceptions as inexc


def write_database(client, data):
    """
    Writes a given data record to the database and prints unexpected results.
    Copy/paste from my homeclimate code.
    """
    from datetime import datetime

    try:
        iresponse  = client.write_points(data)
        if not iresponse:
            print("Sending data to database failed. Response: ", iresponse)
    except inexc.InfluxDBServerError as e:
        print(datetime.utcnow().isoformat(), "  Sending data to database failed due to timeout.\n", e)
        pass
    except Exception as e:
        print(datetime.utcnow().isoformat(), "  Encountered unknown error.\n", e)
        pass

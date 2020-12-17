![FritzBoxInflux](https://github.com/GiantMolecularCloud/FritzBoxInflux/blob/main/FritzBoxInflux.png "FritzBoxInflux")

# FritzBoxInflux

A simple python app to query a FritzBox through fritzconnection and send the interesting results to InfluxDB.

Tested on a FritzBox 7490 with FritzOS 7.12, might crash on other models and/or firmware versions.

## Docker

The image is available on [Docker Hub](https://hub.docker.com/r/giantmolecularcloud/fritzboxinflux).
Note that it will likely get taken down in the future under Docker's policy to take down images that are not regularly accessed.

Build it yourself:
```
docker build --tag fritzboxinflux:latest .
docker run --init --env-file env-sample fritzboxinflux
```


### Environment variables

The FritzBox and InfluxDB instance can be selected through the following environment variables.
If not given, defaults are assumed.

`FB_IP`
IP address of the FritzBox to query. Default if not specified: 192.168.178.1

`FB_PORT`
Port used to query the FritzBox. Default if not specified: 49000

`FB_USER` and `FB_PASSWD`
FritzBox user and password to authentificate. No default! Must be set.

`FB_ID`
Name given to the InfluxDB database. Default if not specified: FritzBox
If no such database is present, it will be created.

`FB_DSL`
Is the connection a DSL connection? Default if not specified: True
For DSL connections, further metrics can be queried.

`INFLUX_IP`
IP address of the InfluxDB instance to connect to. Default if not specified: 127.0.0.1
Must be set since InfluxDB is not running in this container.

`INFLUX_PORT`
Port on which InfluxDB is running. Default if not specified: 8086

`INFLUX_USER` and `INFLUX_PASSWD`
Credentials for the InfluxDB database. Default if not specified: root:root

`SAMPLE_TIME`
Wait time in between queries in seconds. Default if not specified: 60


## Example dashboard

An example for a Grafana dasboard to show the most relevant FritzBox metrics could look like this.
The code for this dashboard is in ![https://github.com/GiantMolecularCloud/FritzBoxInflux/blob/main/dashboard.json](dashboard.json)

![Grafana dashboard](https://github.com/GiantMolecularCloud/FritzBoxInflux/blob/main/dashboard.png "Grafana dashboard")


## Logo

The logo was created in a very simple way in Pixelmator ([FritzBoxInflux.pxd](https://github.com/GiantMolecularCloud/FritzBoxInflux/tree/main/FritzBoxInflux.pxd)). Feel free to make something nicer (without violating potentially protected shapes and color combinations).

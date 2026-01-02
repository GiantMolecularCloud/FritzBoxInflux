from datetime import datetime

from fritzconnection import FritzConnection


class FritzBoxData:
    """
    Wrapper class to connect to a FritzBox, read out values and format them in InfluxDB format.
    """

    def __init__(self):
        """
        Get environment variables or use defaults if env not set.
        Connect to FritzBox using FritzConnection.
        """
        import os
        self.ip          = os.getenv('FB_IP') or '192.168.178.1'
        self.port        = os.getenv('FB_PORT') or '49000'
        self.user        = os.getenv('FB_USER')
        self.passwd      = os.getenv('FB_PASSWD')
        self.id          = os.getenv('FB_ID') or 'FritzBox'
        self.is_dsl      = os.getenv('FB_DSL') or True
        self.timeout     = 10.0
        self.data        = {}
        self.selected_data = {}
        self.influx_data = None
        self.fritzbox    = None


    def connect(self):
        """
        Connect to the FritzBox using FritzConnection.
        """
        self.fritzbox = FritzConnection(address  = self.ip,
                                        port     = self.port,
                                        user     = self.user,
                                        password = self.passwd,
                                        timeout  = self.timeout
                                        # use_tls  = True
                                       )


    def _read_data(self, module, action):
        """
        Helper function to read data from the FritzBox using the module/action syntax of FritzConnection.
        """
        try:
            answer = self.fritzbox.call_action(module, action)
        except:
            answer = {}
        return answer


    def _count_hosts(self):
        """
        Modified from TelegrafFritzBox
        """
        import itertools

        hostsKnown = 0
        hostsActive = 0
        lanHostsActive = 0
        wlanHostsActive = 0
        lanHosts = 0
        wlanHosts = 0
        for n in itertools.count():
            try:
                host = self.fritzbox.call_action('Hosts1', 'GetGenericHostEntry', NewIndex=n)
            except IndexError:
                break
            hostsKnown = hostsKnown +1
            if host['NewActive']:
                hostsActive = hostsActive +1
                if host['NewInterfaceType'] == 'Ethernet': lanHostsActive = lanHostsActive +1
                if host['NewInterfaceType'] == '802.11': wlanHostsActive = wlanHostsActive +1
            if host['NewInterfaceType'] == 'Ethernet': lanHosts = lanHosts +1
            if host['NewInterfaceType'] == '802.11': wlanHosts = wlanHosts +1
        hosts = {'HostsKnown':hostsKnown, 'HostsActive':hostsActive, 'HostsKnownLAN':lanHosts, 'HostsActiveLAN':lanHostsActive, 'HostsKnownWLAN':wlanHosts, 'HostsActiveWLAN':wlanHostsActive,}
        return hosts


    def read_data(self):
        """
        Read information from connected FritzBox.
        """
        self.time = datetime.utcnow().isoformat()
        self.data['hostInfo'] = self._count_hosts()

        if self.is_dsl:
            self.data['connectionInfo'] = self._read_data('WANPPPConnection1', 'GetInfo')
        else:
            self.data['connectionInfo'] = self._read_data('WANIPConn1', 'GetStatusInfo')

        for [name,module,action] in [['deviceInfo',     'DeviceInfo1',                 'GetInfo'],
                                     ['wanInfo',        'WANCommonIFC1',               'GetCommonLinkProperties'],
                                     ['trafficInfo',    'WANCommonIFC1',               'GetAddonInfos'],
                                     ['dslInfo',        'WANDSLInterfaceConfig1',      'GetInfo'],
                                     ['dslError',       'WANDSLInterfaceConfig1',      'GetStatisticsTotal'],
                                     ['dhcpInfo',       'Hosts1',                      'GetHostNumberOfEntries'],
                                     ['lanStat',        'LANEthernetInterfaceConfig1', 'GetStatistics'],
                                     ['wlanStat24',     'WLANConfiguration1',           'GetStatistics'],
                                     ['wlanStat50',     'WLANConfiguration2',           'GetStatistics'],
                                     ['wlanStatGuest',  'WLANConfiguration3',           'GetStatistics'],
                                     ['wlanInfo24',     'WLANConfiguration1',           'GetInfo'],
                                     ['wlanInfo50',     'WLANConfiguration2',           'GetInfo'],
                                     ['wlanInfoGuest',  'WLANConfiguration3',           'GetInfo'],
                                     ['wlanAssoc24',    'WLANConfiguration1',           'GetTotalAssociations'],
                                     ['wlanAssoc50',    'WLANConfiguration2',           'GetTotalAssociations'],
                                     ['wlanAssocGuest', 'WLANConfiguration3',           'GetTotalAssociations'],
                                     ['userInterface',  'UserInterface1',               'GetInfo']
                                    ]:
            self.data[name] = self._read_data(module,action)


    def select_data(self):
        """
        Select the useful measurements to not save dozens of unnecessary numbers.
        """

        self.selected_data = {}
        try:
            self.selected_data['device'] = {'model':                   self.data['deviceInfo']['NewModelName'],
                                            'firmware':                self.fritzbox.device_manager.system_version,
                                            'update_available':        self.data['userInterface']['NewUpgradeAvailable'],
                                            'uptime':                  self.data['deviceInfo']['NewUpTime']
                                           }
        except:
            self.selected_data['device'] = {}

        try:
            self.selected_data['connection'] = {'connection_time':         self.data['connectionInfo']['NewUptime'],
                                                'connection_status':       self.data['connectionInfo']['NewConnectionStatus'],
                                                'connection_last_error':   self.data['connectionInfo']['NewLastConnectionError'],
                                                'connection_type':         self.data['wanInfo']['NewWANAccessType'],
                                                'physical_link':           self.data['wanInfo']['NewPhysicalLinkStatus'],
                                                'external_IP':             self.data['connectionInfo']['NewExternalIPAddress'],
                                                'bitrate_down_max':        self.data['wanInfo']['NewLayer1DownstreamMaxBitRate'],
                                                'bitrate_up_max':          self.data['wanInfo']['NewLayer1UpstreamMaxBitRate'],
                                                'dsl_rate_down':           self.data['dslInfo']['NewDownstreamCurrRate'],
                                                'dsl_rate_up':             self.data['dslInfo']['NewUpstreamCurrRate'],
                                                'dsl_rate_down_max':       self.data['dslInfo']['NewDownstreamMaxRate'],
                                                'dsl_rate_up_max':         self.data['dslInfo']['NewUpstreamMaxRate'],
                                                'noise_down':              self.data['dslInfo']['NewDownstreamNoiseMargin'],
                                                'noise_up':                self.data['dslInfo']['NewUpstreamNoiseMargin'],
                                                'power_down':              self.data['dslInfo']['NewDownstreamPower'],
                                                'power_up':                self.data['dslInfo']['NewUpstreamPower'],
                                                'attenuation_down':        self.data['dslInfo']['NewDownstreamAttenuation'],
                                                'attenuation_up':          self.data['dslInfo']['NewUpstreamAttenuation'],
                                                'error_fec':               self.data['dslError']['NewFECErrors'],
                                                'error_fec_local':         self.data['dslError']['NewATUCFECErrors'],
                                                'error_crc':               self.data['dslError']['NewCRCErrors'],
                                                'error_crc_local':         self.data['dslError']['NewATUCCRCErrors'],
                                                'error_hec':               self.data['dslError']['NewHECErrors'],
                                                'error_hec_local':         self.data['dslError']['NewATUCHECErrors']
                                            }
        except:
            self.selected_data['connection'] = {}

        try:
            self.selected_data['traffic'] = {'rate_byte_down':          self.data['trafficInfo']['NewByteReceiveRate'],
                                             'rate_byte_up':            self.data['trafficInfo']['NewByteSendRate'],
                                             'rate_packets_down':       self.data['trafficInfo']['NewPacketReceiveRate'],
                                             'rate_packets_up':         self.data['trafficInfo']['NewPacketSendRate'],
                                             'bytes_down_total':        self.data['trafficInfo']['NewTotalBytesReceived'],
                                             'bytes_up_total':          self.data['trafficInfo']['NewTotalBytesSent'],
                                             'bytes_down_total64':      self.data['trafficInfo']['NewX_AVM_DE_TotalBytesReceived64'],
                                             'bytes_up_total64':        self.data['trafficInfo']['NewX_AVM_DE_TotalBytesSent64'],
                                             'dns_server1':             self.data['trafficInfo']['NewDNSServer1'],
                                             'dns_server2':             self.data['trafficInfo']['NewDNSServer2']
                                            }
        except:
            self.selected_data['traffic'] = {}

        try:
            self.selected_data['network'] = {'hosts_known':             self.data['dhcpInfo']['NewHostNumberOfEntries'],
                                             'lan_packets_up':          self.data['lanStat']['NewPacketsSent'],
                                             'lan_packets_down':        self.data['lanStat']['NewPacketsReceived'],
                                             'wlan_24_name':            self.data['wlanInfo24']['NewSSID'],
                                             'wlan_24_channel':         self.data['wlanInfo24']['NewChannel'],
                                             'wlan_24_clients':         self.data['wlanAssoc24']['NewTotalAssociations'],
                                             'wlan_24_packets_up':      self.data['wlanStat24']['NewTotalPacketsSent'],
                                             'wlan_24_packets_down':    self.data['wlanStat24']['NewTotalPacketsReceived'],
                                             'wlan_50_name':            self.data['wlanInfo50']['NewSSID'],
                                             'wlan_50_channel':         self.data['wlanInfo50']['NewChannel'],
                                             'wlan_50_clients':         self.data['wlanAssoc50']['NewTotalAssociations'],
                                             'wlan_50_packets_up':      self.data['wlanStat50']['NewTotalPacketsSent'],
                                             'wlan_50_packets_down':    self.data['wlanStat50']['NewTotalPacketsReceived'],
                                             'wlan_guest_name':         self.data['wlanInfoGuest']['NewSSID'],
                                             'wlan_guest_channel':      self.data['wlanInfoGuest']['NewChannel'],
                                             'wlan_guest_clients':      self.data['wlanAssocGuest']['NewTotalAssociations'],
                                             'wlan_guest_packets_up':   self.data['wlanStatGuest']['NewTotalPacketsSent'],
                                             'wlan_guest_packets_down': self.data['wlanStatGuest']['NewTotalPacketsReceived']
                                            }
        except:
            self.selected_data['network'] = {}


    def format_data(self):
        """
        Format data in an InfluxDB compatible dictionary.
        The various groups of detailed information are separated using tags as field names can occur multiple times.
        """

        self.influx_data = [{'measurement': groupname, 'time': self.time, 'fields': group} for groupname,group in self.selected_data.items() if not group=={}]


    def get_influx_data(self):
        """
        Meta-function to acquire new data and format them correctly to be sent to InfluxDB directly.
        """
        self.read_data()
        self.select_data()
        self.format_data()
        return self.influx_data
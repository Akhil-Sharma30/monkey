const ICMP_SCAN_CONFIGURATION_SCHEMA = {
  'title': 'Ping scanner',
  'type': 'object',
  'properties': {
    'timeout': {
      'title': 'Ping scan timeout',
      'type': 'number',
      'description': 'Maximum time to wait for ping response'
    }
  }
}

export default ICMP_SCAN_CONFIGURATION_SCHEMA;

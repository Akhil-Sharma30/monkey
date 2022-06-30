const CONFIGURATION_TABS = {
  PROPAGATION: 'propagation',
  PAYLOADS: 'payloads',
  PBA: 'post_breach_actions',
  CREDENTIALS_COLLECTORS: 'credential_collectors',
  ADVANCED: 'advanced'
};

const advancedModeConfigTabs = [
  CONFIGURATION_TABS.PROPAGATION,
  CONFIGURATION_TABS.PAYLOADS,
  CONFIGURATION_TABS.PBA,
  CONFIGURATION_TABS.CREDENTIALS_COLLECTORS,
  CONFIGURATION_TABS.ADVANCED
];

const ransomwareModeConfigTabs = [
  CONFIGURATION_TABS.PROPAGATION,
  CONFIGURATION_TABS.PAYLOADS,
  CONFIGURATION_TABS.ADVANCED
];

const CONFIGURATION_TABS_PER_MODE = {
  'advanced': advancedModeConfigTabs,
  'ransomware': ransomwareModeConfigTabs
};

export default CONFIGURATION_TABS_PER_MODE;

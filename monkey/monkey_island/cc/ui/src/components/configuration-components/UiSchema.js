import AdvancedMultiSelect from '../ui-components/AdvancedMultiSelect';
import InfoBox from './InfoBox';
import TextBox from './TextBox.js';
import WarningBox from './WarningBox';
import SensitiveTextInput from '../ui-components/SensitiveTextInput';
import PluginSelectorTemplate from './PluginSelectorTemplate';

export default function UiSchema(props) {
  const UiSchema = {
    propagation: {
      exploitation: {
        exploiters: {
          'ui:classNames': 'config-template-no-header',
          'ui:ObjectFieldTemplate': PluginSelectorTemplate
        },
        options: {
          http_ports: {
            items: {
            }
          }
        }
      },
      credentials: {
        exploit_ssh_keys: {
          items: {
            public_key: {
            },
            private_key: {
            }
          }
        },
        exploit_password_list: {
          items: {
            'ui:classNames': 'config-template-no-header',
            'ui:widget': SensitiveTextInput
          }
        },
        exploit_lm_hash_list: {
          items: {
            'ui:classNames': 'config-template-no-header',
            'ui:widget': SensitiveTextInput
          }
        },
        exploit_ntlm_hash_list: {
          items: {
            'ui:classNames': 'config-template-no-header',
            'ui:widget': SensitiveTextInput
          }
        }
      },
      network_scan: {
        targets: {
          blocked_ips: {
            items: {
              'ui:classNames': 'config-template-no-header'
            }
          },
          inaccessible_subnets: {
            items: {
              'ui:classNames': 'config-template-no-header'
            }
          },
          info_box_scan_my_networks: {
            'ui:field': WarningBox
          },
          subnets: {
            items: {
              'ui:classNames': 'config-template-no-header'
            }
          }
        },
        tcp: {
          ports: {
            items: {
              'ui:classNames': 'config-template-no-header'
            }
          }
        },
        fingerprinters: {
          'ui:classNames': 'config-template-no-header',
          'ui:widget': AdvancedMultiSelect,
          fingerprinter_classes: {
            'ui:classNames': 'config-template-no-header'
          }

        }
      }
    },
    payloads: {
      'ui:classNames': 'config-template-no-header',
      encryption: {
        info_box: {
          'ui:field': InfoBox
        },
        file_extension: {
          'ui:emptyValue': ''
        },
        directories: {
          // Directory inputs are dynamically hidden
        },
        text_box: {
          'ui:field': TextBox
        },
        enabled: {
          'ui:widget': 'hidden'
        }
      },
      other_behaviors: {
        'ui:widget': 'hidden'
      }
    },
    credential_collectors: {
      'ui:classNames': 'config-template-no-header',
      'ui:widget': AdvancedMultiSelect,
      credential_collectors_classes: {
        'ui:classNames': 'config-template-no-header'
      }
    }
  };
  return UiSchema[props.selectedSection]
}

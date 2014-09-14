from pvauto.api import Argument

defaultDict = {
    Argument.CLI_USER[Argument.NAME]: 'jane',
    Argument.CLI_PASS[Argument.NAME]: 'jingli',
    Argument.SNMP_READ_COMM[Argument.NAME]: 'comstr_ro1',
    Argument.TFTP_SERVER[Argument.NAME]: '192.168.2.4',
    # Argument.REMOTE_FILE[Argument.NAME]: 'Baseline_configs/3930-04_baseline.config',
    Argument.SAOS_VERSION1[Argument.NAME]: 'saos-06-10-02-1486',
    Argument.SAOS_VERSION2[Argument.NAME]: 'saos-06-12-00-0249',
}

ipToConfigDict = {
    '192.168.1.53': 'Baseline_configs/3930-02_baseline.config',
    '192.168.1.54': 'Baseline_configs/3930-03_baseline.config',
    '192.168.1.55': 'Baseline_configs/3930-04_baseline.config',
    '192.168.1.56': 'Baseline_configs/3930-05_baseline.config',
    '192.168.1.57': 'Baseline_configs/3930-06_baseline.config',
    '192.168.1.58': 'Baseline_configs/3930-07_baseline.config',
    '192.168.1.59': 'Baseline_configs/3930-08_baseline.config',
    '192.168.1.60': 'Baseline_configs/3930-13_baseline.config',
    '192.168.1.61': 'Baseline_configs/3930-25_baseline.config',
    '192.168.1.68': 'Baseline_configs/3931-01_baseline.config',
    '192.168.1.69': 'Baseline_configs/3931-02_baseline.config',
    '192.168.1.70': 'Baseline_configs/3931-03_baseline.config',
    '192.168.1.71': 'Baseline_configs/3931-04_baseline.config',
    '192.168.1.72': 'Baseline_configs/3931-05_baseline.config',
    '192.168.1.73': 'Baseline_configs/3931-06_baseline.config',
    '192.168.1.74': 'Baseline_configs/3931-07_baseline.config',
    '192.168.1.75': 'Baseline_configs/3931-08_baseline.config',
    '192.168.1.64': 'Baseline_configs/3940-06_baseline.config',
    '192.168.1.65': 'Baseline_configs/3940-11_baseline.config',
    '192.168.1.51': 'Baseline_configs/3960-03_baseline.config',
    '192.168.1.52': 'Baseline_configs/3960-13_baseline.config',
    '192.168.1.62': 'Baseline_configs/5140-01_baseline.config',
    '192.168.1.63': 'Baseline_configs/5140-02_baseline.config',
    '192.168.1.66': 'Baseline_configs/5150-05_baseline.config',
    '192.168.1.67': 'Baseline_configs/5150-15_baseline.config',
}

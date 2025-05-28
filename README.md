https://www.dwd.de/DE/leistungen/cdc/cdc_ueberblick-klimadaten.html
- Monthly air temperature mean
- percipitation
- sunshine-duration


## prometheus.yml
global:
  scrape_interval: 1s

scrape_configs:
  - job_name: 'pushgateway'
    static_configs:
      - targets: ['localhost:9091']
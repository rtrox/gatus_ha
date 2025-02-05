
<div align="center">
<h2>Gatus Home Assistant Integrations</h2>

_Expose Your Gatus Uptime Checks as Sensors_

</div>

<div align="center">

[![GitHub branch check runs](https://img.shields.io/github/check-runs/rtrox/gatus_ha/main?style=for-the-badge&logo=pytest&logoColor=white&label=main)](https://github.com/rtrox/gatus_ha/actions?query=branch%3Amain)
[![Coveralls](https://img.shields.io/coverallsCoverage/github/rtrox/gatus_ha?branch=main&style=for-the-badge&logo=coveralls&logoColor=white)](https://coveralls.io/github/rtrox/gatus_ha?branch=main)
![GitHub Repo stars](https://img.shields.io/github/stars/rtrox/gatus_ha?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/rtrox/gatus_ha?style=for-the-badge)

[![HACS Custom Integration](https://img.shields.io/badge/HACS-Custom_Integration-blue?style=for-the-badge)](https://hacs.xyz/docs/faq/custom_repositories/)
</div>

# Installation

While in development, this Integration can be added through HACS, by adding this repo as a [HACS custom repository](https://hacs.xyz/docs/faq/custom_repositories/).

<img src=".github/images/custom_repositories.png" height="400"><img src=".github/images/add.png" height="400">

# Configuration

Once Installed, Add via the Web UI in the Integrations Menu

![Config Flow](.github/images/config_flow.png)

- **Instance Name**: A unique name for your Gatus deployment. This is only used as the label for the Integration in Home Assistant.
- **Base URL**: The Base URL for your Gatus Deployment, Including the protocol (`http://` or `https://`), and if necessary the port. Examples:
    - https://status.example.com
    - http://localhost:8080
- **Verify SSL**: Whether Home Assistant should verify that your SSL Certificate is valid (if using HTTPS).

# Sensors

This Integration will create a single Binary Sensor for each endpoint configured in your gatus instance, titled `binary_sensor.gatus_{key}`, where the key is the key in Gatus (it will be `{group}_{name}` if the Endpoint is in a group, or just `{name}` if it isn't.) Example: `binary_sensor.gatus_apps_shlink`. Each Binary Sensor will have the following attributes:

![Binary Sensor](.github/images/sensor.png)
Attribute | Definition
---|---
Name | The Name as configured in Gatus
Group | The Gatus Group the Endpoint is in
Key | The endpoint key in the Gatus API for this endpoint (used in URLs)
Hostname | The Hostname or IP of the endpoint
Last Checked | When Gatus last checked the endpoint
Response time | How quickly the endpoint responded in the last check, in nanoseconds
Errors | Any errors returned if the check was not successful
Url | The direct link to the Gatus Page for this endpointgit com
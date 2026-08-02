# Nkabom Savings & Loans PLC — Disaster Recovery Failover Test

**CY376: Network Monitoring, Security and Auditing — End-of-Semester Project (Blue Team)**

## Summary

A full-scale, working Disaster Recovery (DR) failover system built for a simulated banking
application. The environment spans three network-isolated sites (Primary, DR, and Monitor)
connected via a GNS3-emulated, OSPF-routed network, with PostgreSQL streaming replication
(TLS-encrypted) keeping the DR site continuously synchronised with Primary. An automated
health-check service detects Primary failures and redirects traffic to DR via DNS, without
human intervention. Two independent disaster scenarios were tested and measured, producing
a consistent Recovery Time Objective (RTO) of ~10 seconds and an observed Recovery Point
Objective (RPO) of ~0 seconds. A split-brain prevention safeguard and a full, tested failback
procedure are also included.

Full technical write-up: see [`docs/DR_Failover_Report.pdf`](docs/DR_Failover_Report.pdf).

## Author

- **Nakorei Abdulai Shafiyu**
- Index Number: FCM.41.018.180.23
- Team Role: Blue Team

## Tools and Technologies

- **Network emulation:** GNS3, FRRouting (OSPF), Cisco vIOS-L2
- **Virtualisation:** Oracle VirtualBox
- **Database:** PostgreSQL 18 (streaming replication, TLS/certificate authentication)
- **Application:** Python, Flask
- **DNS / failover:** dnsmasq, custom Python health-check + failover script
- **Containerisation:** Docker (FRRouting routers)
- **OS:** Ubuntu Server 26.04 LTS

## Repository Structure
scripts/ Application code, monitoring/failover script, split-brain guard
configs/ Sanitised configuration excerpts (PostgreSQL, dnsmasq, systemd)
docs/ Final report (PDF)
evidence/ Screenshots referenced in the report

## How to Run

This project runs across a 5-VM GNS3 + VirtualBox lab topology (three application VMs, two
network devices) and is not a single-command deployment. The full build procedure —
network topology, VM provisioning, database replication setup, TLS configuration, and
monitoring/failover deployment — is documented step by step in the report
(`docs/DR_Failover_Report.pdf`), Sections 4 and 5.

At a high level, to reproduce:
1. Build the GNS3 topology (3 sites: switch + FRRouting router each, full OSPF mesh).
2. Provision three Ubuntu Server VMs (Primary, DR, Monitor), each dual-homed for
   management (NAT) and DR-network traffic.
3. Deploy `scripts/app_primary.py` (as `app.py`) identically on Primary and DR, each with
   its own `SITE_NAME` / `SITE_IP` environment variables (see `configs/`).
4. Configure PostgreSQL streaming replication from Primary to DR (see `configs/postgresql/`).
5. Deploy `scripts/monitor.py` and `scripts/safe_restart_primary.sh` on the Monitor and
   Primary hosts respectively.

## Screenshots

See the `evidence/` folder for supporting screenshots (network topology, application UI on
both sites, replication proof, and split-brain guard test output), each referenced by figure
number in the report.

## Notes

- Credentials referenced in scripts are supplied via environment variables and are not
  present in this repository.
- All IP addressing shown is internal to an isolated lab network (10.10.x.x / 192.168.57.x)
  and is not routable or reachable outside the lab environment.

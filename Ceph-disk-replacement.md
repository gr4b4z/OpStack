# **Ceph disk crash replacement procedure**

## Symptoms

1. Ceph cluster status shows OSD(s) down
    ```bash
    ceph health
    ```
    Example output:
    ```bash
    HEALTH_WARN 1/3 in osds are down
    ```

2. Check which OSD(s) are down
    ```bash
    ceph osd tree
    ```
    Example output:
    ```bash
    HEALTH_WARN 1/3 in osds are down
    osd.0 is down since epoch 23, last address 192.168.106.220:6800/11080
    ```

3. Drain the OSD by setting its weight to zero
    ```bash
    ceph osd crush reweight osd.0 0
    ```

    ```bash
    ceph osd out 0
    ```

    ```bash
    systemctl stop ceph-osd@0
    ```

    ```bash
    ceph osd crush remove
    ```

    ```bash
    ceph auth del osd.0
    ```

    ```bash
    ceph osd rm 0
    ```

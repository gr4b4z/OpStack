# **Troubleshooting**

## **Recover storage node**

If ceph cluster is working and serving volumes, you could use
  ```bash
  ceph osd set noout
  ```
to disable rebalancing until evrything is done. Work on one node at a time in such case.

- Verify networking: bonds (`bond0` and `bond1`; speeds), ip addresses, gateways - if any problems, first use:
  ```bash
  systemctl restart network
  ```
- Verify ceph status with:
  ```bash
  ceph -s
  ceph osd tree
  ```
- Once everything looks good, enable rebalancing:
  ```bash
  ceph osd unset noout
  ```
  You can watch the progress with
  ```bash
    ceph -w
  ```

## **Recover controller node**

Configure one controller node at a time, putting the other in maintenance mode to prvent fencing.

- Verify networking: bonds (`bond0` and `bond1`; speeds), ip addresses, gateways - if any problems, first use:
  ```bash
  systemctl restart network
  ```
- Verify if rbdmap is started
  ```bash
  systemctl status rbdmap
  ```
- Verify the correct rbd mappings via `lsblk`. The proper output should include:
  ```bash
  rbd0     253:0    0     1G  0 disk
  rbd1     253:16   0   256G  0 disk
  └─rbd1p1 253:17   0   256G  0 part
  rbd2     253:32   0   100G  0 disk
  └─rbd2p1 253:33   0   100G  0 part
  ```
  If not restart rbdmap but use `stop` and `start` - not `restart`:
  ```bash
  systemctl stop rbdmap
  systemctl start rbdmap
  ```
- Remove file that prevents starting of corosync service
  ```bash
  rm /var/spool/corosync/block_automatic_start
  ```
- Start cluster services
  ```bash
  systemctl start corosync
  systemctl start pacemaker
  ```
- Once above is completed without error, rejoin crowbar:
  ```bash
  restart crowbar_join
  ```
- Cleanup resources in Hawk, pay special attention to g-postgres (and rabbitmq) resources:
  - filesystem - if rbd volumes are mapped properly, the correct volume is mounted at `/var/lib/postgres` (`/var/lib/rabbitmq`)
  - vip - the virtual ip address should be assigned to the `bond0` interface - check with `ip a`
  - database - service `postgresql` should be started - use `systemctl` to verify any possible errors

## **Recover compute node**

- Verify networking: bonds (`bond0` and `bond1`; speeds), ip addresses, gateways - if any problems, first use:
  ```bash
  systemctl restart network
  ```
- Verify if rbdmap is started
  ```bash
  systemctl status rbdmap
  ```
- Verify the correct rbd mappings via `lsblk`. The proper output should include:
  ```bash
  rbd0     253:0    0     1G  0 disk
  ```
- Rejoin crowbar:
  ```bash
  restart crowbar_join
  ```
- Cleanup resources in Hawk:
  - remote-*compute_node_name*
  - cl-g-nova-compute
  - nova-evacuate (will be green once nova resources for all compute nodes are ok)

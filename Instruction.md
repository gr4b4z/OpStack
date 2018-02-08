## 4.6 Install Ceph cluster
1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Ceph barclamp
3. Set the parameters:
    * Number of replicas of an object = 3
4. Allocate Ceph components to the nodes per the list below:
    * **ceph-mon**: *opstack-storage01*, *opstack-storage02*, *opstack-storage03* (all storage nodes)
    * **ceph-osd**: *opstack-storage01*, *opstack-storage02*, *opstack-storage03* (all storage nodes)
    * **ceph-rados-gw**: *opstack-storage01*
5. Click **Apply** to start applying Ceph barclamp  

## 4.7 Create shared storage for Pacemaker cluster
### 4.7.1 Create RBDs for postgres and rabbitmq:
* opstack-storage01

    ```bash
    rbd create shared-postgres --size 262144 --image-shared --pool rbd
    rbd create shared-rabbitmq --size 102400 --image-shared --pool rbd
    rbd create sbd1 --size 1024 --image-shared --pool rbd
    ```

### 4.7.2 Allocate IPs from public network to all compute/controller nodes:
* opstack-admin

    ```bash
    for i in $(seq 1 1 6) ; do crowbar network allocate_ip "default" opstack-node0$i.ocean.local "public" "host" ; done
    for i in $(seq 1 1 6) ; do crowbar network enable_interface "default" opstack-node0$i.ocean.local "public" ; done
    ```

### 4.7.3 Run chef client:
* opstack-node01
* opstack-node02
* opstack-node03
* opstack-node04
* opstack-node05
* opstack-node06

    ```bash
    chef-client
    ```

### 4.7.4 Install ceph-common and sbd, copy configuration files to nodes:
* opstack-node01
* opstack-node02
* opstack-node03
* opstack-node04
* opstack-node05
* opstack-node06

    ```bash
    zypper in -y ceph-common sbd
    scp root@opstack-storage01:'/etc/ceph/ceph.conf /etc/ceph/ceph.client.admin.keyring' /etc/ceph/
    chown ceph:ceph /etc/ceph/ceph.client.admin.keyring
    echo "rbd/sbd1 id=admin,keyring=/etc/ceph/ceph.client.admin.keyring" >> /etc/ceph/rbdmap
    ```


### 4.7.5 Add shared storage for postgres and rabbit to RBD map:
* opstack-node01
* opstack-node02

    ```bash
    echo "rbd/shared-postgres  id=admin,keyring=/etc/ceph/ceph.client.admin.keyring" >> /etc/ceph/rbdmap
    echo "rbd/shared-rabbitmq  id=admin,keyring=/etc/ceph/ceph.client.admin.keyring" >> /etc/ceph/rbdmap
    systemctl restart rbdmap
    ```

### 4.7.6 Initialize SBD:
* opstack-node01

    ```bash
    sbd -d /dev/rbd/rbd/sbd1 create
    ```


### 4.7.7 Restart RBDMap service:
* opstack-node01
* opstack-node02
* opstack-node03
* opstack-node04
* opstack-node05
* opstack-node06

    ```bash
    systemctl restart rbdmap
    ```


## 4.8 Install Pacemaker cluster
1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Pacemaker barclamp and provide a name for the cluster (i.e. **cluster”)
3. Set values for the following parameters:
    * Prepare cluster for DRBD = false   ·
    * Configuration mode for STONITH = Configured with STONITH Block Device (SBD)
    * Kernel module for watchdog = softdog 
    * Do not start corosync on boot after fencing = true
4. Allocate components according to the below:
    * pacemaker-cluster-member to *opstack-node01*, *opstack-node02*
    * hawk-server to *opstack-node01*, *opstack-node02* ·
    * pacemaker-remote to *opstack-node03*, *opstack-node04*, *opstack-node05*, *opstack-node06* (all compute nodes)
5. Fill in block device names for all nodes with value `/dev/rbd/rbd/sbd1`
6. Click **Apply** to start applying the Pacemaker barclamp

## 4.9 Install Database
1. Create a new partition and create a filesystem on it:
    * opstack-node01
        ```bash
        fdisk /dev/rbd1
        <n Ent> <Ent> <Ent> <Ent> <w>
        partprobe
        mkfs.xfs /dev/rbd1p1
        ```
    * opstack-node02
        ```bash
        systemctl restart rbdmap
        ```
3. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
4. Go to **Create** for Database barclamp
5. Set values for the following parameters:
    * **Storage Mode** = Shared Storage
    * **Name of Block Device or NFS Mount Specification** = /dev/rbd1p1
    * **Filesystem Type** = xfs 
6. Allocate components according to the below:
    * **database-server** to the cluster
7. Click **Apply** to start applying the Database barclamp

## 4.10 Install RabbitMQ
1. Create a new partition and create a filesystem on it:
    * opstack-node01
        ```bash
        fdisk /dev/rbd2
        <n Ent> <Ent> <Ent> <Ent> <w>
        partprobe
        mkfs.xfs /dev/rbd2p1
        ```
    * opstack-node02
        ```bash
        systemctl restart rbdmap
        ```
3. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
4. Go to **Create** for RabbitMQ barclamp
5. Set values for the following parameters:
    * Use RabbitMQ Clustering = false
    * Storage Mode = Shared Storage
    * Name of Block Device or NFS Mount Specification = /dev/rbd2p1
    * Filesystem Type = xfs
6. Allocate components according to the below:
    * **rabbitmq-server** to the cluster
7. Click **Apply** to start applying the Keystone barclamp
 
## 4.11 Install Keystone
1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Keystone barclamp
3. Allocate components according to the below:
    * **keystone-server** to the cluster
4. Click **Apply** to start applying the Keystone barclamp
 
## 4.12 Install Glance

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Glance barclamp
3. Set values for the following parameters:
    * **Default Storage Store** = Rados 
4. Allocate components according to the below:
    * **glance-server** to cluster
5. Click **Apply** to start applying the Glance barclamp
 
## 4.13 Install Cinder

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Cinder barclamp
3. Remove backend **default**
4. Add new backend named **ceph** with following properties:
    * **Use Ceph deployed by Crowbar** = true
    * **RADOS pool for Cinder volumes** = volumes
    * **RADOS user (Set only if using CephX authentication)** = cinder
5. Enter the raw edit mode, locate setting:
    * **default_volume_type** and set its value to **ceph**
6. Allocate components according to the below:
    * **cinder-controller** to cluster
    * **cinder-volume** to *opstack-node03*, *opstack-node04*, *opstack-node05*, *opstack-node06* (all compute nodes)
7. Click **Apply** to start applying the Cinder barclamp
 
## 4.14 Install Neutron

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Neutron barclamp
3. Set values for the following parameters:
    * **DHCP Domain** = openstack.local 
4. Allocate components according to the below:
    * **neutron-server** to cluster
    * **neutron-network** to cluster
5. Click **Apply** to start applying the Neutron barclamp
 
## 4.15 Install Nova

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Nova barclamp
3. Set values for the following parameters:
    * **Virtual RAM to Physical RAM allocation ratio** = 1
    * **Virtual CPU to Physical CPU allocation ratio** = 6
    * **Virtual Disk to Physical Disk allocation ratio** = 10
    * **Reserved Memory for Nova Compute hosts (MB)** = 8192
    * **Enable Libvirt Migration** = true
    * **Set up Shared Storage on nova-controller for Nova instances** = false
    * **Shared Storage for Nova instances has been manually configured** = false
4. Allocate components according to the below:
    * **nova-controller** to cluster
    * **nova-compute-kvm** to *opstack-node03*, *opstack-node04*, *opstack-node05*, *opstack-node06* (all compute nodes)
5. Click **Apply** to start applying the Nova barclamp
 
## 4.16 Install Horizon

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Horizon barclamp
3. Allocate components according to the below:
    * **horizon-server** to the cluster
4. Click **Apply** to start applying the Horizon barclamp
 
## 4.17 Install Heat

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Heat barclamp
3. Allocate components according to the below:
    * **heat-server** to the cluster
4. Click **Apply** to start applying the Heat barclamp
 
## 4.18 Install Ceilometer

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Ceilometer barclamp
3. Allocate components according to the below:
    * **ceilometer-server** to the cluster
    * **ceilometer-central** to the cluster
    * ceilometer-agent to *opstack-node03*, *opstack-node04*, *opstack-node05*, *opstack-node06* (all compute nodes)
4. Click **Apply** to start applying the Ceilometer barclamp
 
## 4.19 Install Aodh

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Aodh barclamp
3. Allocate components according to the below:
    * **aodh-server** to the cluster
4. Click **Apply** to start applying the Aodh barclamp
 
## 4.20 Install Magnum

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Magnum barclamp
3. Allocate components according to the below:
    * **magnum** to the cluster
4. Click **Apply** to start applying the Magnum barclamp
 
## 4.21 Install Tempest

1. Open SUSE OpenStack Cloud admin web portal <http://ADMIN_NODE_IP_ON_ADMIN_NETWORK> and go to Barclamps -> OpenStack
2. Go to **Create** for Tempest barclamp
3. Allocate components according to the below:
    * tempest to the *opstack-node01*
4. Click **Apply** to start applying the Tempest barclamp
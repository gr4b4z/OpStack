#!/usr/bin/python
import csv
import os
import subprocess
import sys

is_run_mode = len(sys.argv)>1 and sys.argv[1] == 'execute'

print('Execution mode  = {}'.format(is_run_mode))	

VOL_FILE='_import/vols.csv'
INSTANCE_FILE='_import/inst.csv'
VOL_INSTANCE_FILE='_import/vol_att.csv'
VOL_STATUS_FILE='_import/status-volumes.csv'
INSTANCE_STATUS_FILE='_import/status-instances.csv'




class Volume:
    def __init__(self,old_volume_id,size,bootable,display,isattached):
        self.old_volume_id=old_volume_id
        self.new_volume_id=None
        self.size=size
        self.is_bootable=(bootable=='t')
        self.display_name=display
        self.is_attached=isattached
        self.mount_point=''
        self.exists = False
   
    def __str__(self):
      return str("Processing volume {} {} size {} id {}".format(self.display_name,self.mount_point,self.size,self.old_volume_id))

    def setMountPoint(self,mount_point):
        self.mount_point=mount_point
    
    def exists(self):
        return self.new_volume_id!=None

class Instance:
    def __init__(self, host_name,old_instance_id,flavor_id):
      self.host_name = host_name
      self.flavor_id = flavor_id
      self.old_instance_id=old_instance_id
      self.new_instance_id=None
      self.volumes=[]
      self.exists = False


    def __str__(self):
      return str("Processing Instance {} Favour:{}  Id:{}".format(self.host_name,self.flavor_id,self.old_instance_id))

    def addVolume(self,volume):
      self.volumes.append(volume)
      self.volumes = sorted(self.volumes,key=lambda x: x.mount_point, reverse=False)
     
    def addVolumes(self,volumes):
      self.volumes = volumes
      self.volumes = sorted(self.volumes,key=lambda x: x.mount_point, reverse=False)
 
    def exists(self):
        return self.new_instance_id!=None

def processInstance( inst ):
    if inst.new_instance_id==None:
       # inst.new_instance_id = subprocess.check_output(['bash','-c', "./create_instance.sh {} {} {}".format(inst.flavor_id,inst.volumes[0].new_volume_id,inst.host_name)]).rstrip()
        
        inst.new_instance_id=subprocess.check_output(['bash','-c', "openstack server create --flavor {} --volume {} --security-group test --key-name cloud --nic net-id=a8b93582-2589-4a52-a2a5-862241eb3c8a {} -f value -c id".format(inst.flavor_id,vol.new_volume_id,inst.host_name)])
        subprocess.call(['sleep','5'])
        floatIP=subprocess.check_output(['bash','-c', "openstack floating ip list -f value | grep None | awk 'NR==1 {print {}}".format(inst.volumes[0].new_volume_id)])
        subprocess.call(['bash','-c', "openstack server add floating ip {} {}".format(instId,floatIP )])

        for vol in inst.volumes[1:]:
            print('Attaching volume {}'.format(vol.mount_point))
            subprocess.check_output(['bash','-c', "openstack server add volume {} {}".format(inst.new_instance_id,vol.new_volume_id)])
    return inst

def processVolume(vol):
    if vol.new_volume_id==None:
        if os.path.isfile('volumes/volume-{}.vmdk'.format(vol.old_volume_id)):
            print("Creating Volume")
            vol.new_volume_id = subprocess.check_output(['bash','-c', "openstack volume create --size {} {} -c id -f value".format(vol.size,vol.display_name)]).rstrip()
            subprocess.call(["sleep", "5"])
            subprocess.call(["rbd","rm","volumes/volume-{}".format(vol.new_volume_id)])
            subprocess.call(["qemu-img","convert","-p","-f","vmdk","-O","raw","./volumes/volume-{}.vmdk".format(vol.old_volume_id),"./volumes/volume-{}.raw".format(vol.old_volume_id)])
            subprocess.call(["rbd","import","--image-format","2","./volumes/volume-{}.raw".format(vol.old_volume_id),"volumes/volume-{}".format(vol.new_volume_id)])
            subprocess.call(["rm", "./volumes/volume-{}.raw".format(vol.old_volume_id)])

            if vol.is_bootable:
                print('Setting {} as bootable'.format(vol.new_volume_id))
                subprocess.check_output(['bash','-c', "cinder set-bootable {} True".format(vol.new_volume_id)])
        else:
            print("ignoring volume, it doesn't exists on disk")
    return vol



###PROCESS INSTANCESS
#host_name, instance_id, favour_id
instances = {'sdsd':12}
instances.clear()
with open(INSTANCE_FILE, 'r') as csv_file:
    reader = csv.reader(line for line in csv_file)
    instance_list = list(reader)

for element in instance_list:
    instance=Instance(element[0],element[1],element[2])   
    key=str(element[1])
    instances[key]=instance

########PROCES VOLUMES STATYUS
if os.path.isfile(INSTANCE_STATUS_FILE):
    with open(INSTANCE_STATUS_FILE, 'r') as csv_file:
        reader = csv.reader(line for line in csv_file)
        instance_status = list(reader)
        for ints in instance_status:
            instances[ints[0]].new_instance_id = ints[1]

###PROCESS VOLUMES
#def __init__(old_volume_id,size,bootable,display,isattached)

with open(VOL_FILE, 'r') as csv_file:
    reader = csv.reader(line for line in csv_file)
    volume_list = list(reader)

volumes = {'sdsd':23}
volumes.clear()

for element in volume_list:
    volume = Volume(element[0],element[1],element[2],element[3],element[4])
    volumes[element[0]]= volume

########PROCES VOLUMES STATYUS
if os.path.isfile(VOL_STATUS_FILE):
    with open(VOL_STATUS_FILE, 'r') as csv_file:
        reader = csv.reader(line for line in csv_file)
        volume_status = list(reader)
        for vol in volume_status:
            volumes[vol[0]].new_volume_id = vol[1]


###PROCESS VOLUMES_To_INSTANCE
#old_volume_id, instance_id , mount_point
with open(VOL_INSTANCE_FILE, 'r') as csv_file:
    reader = csv.reader(line for line in csv_file)
    volAttached = list(reader)

for element in volAttached:
    volume_id=str(element[0])
    instance_id=str(element[1])
    mount_point=element[2]
    if volume_id in volumes:
        volume=volumes[volume_id]
        volume.setMountPoint(mount_point)
        instances[instance_id].addVolume(volume)
        #print('{} -- {} -- {}'.format(instances[instance_id].host_name,mount_point,volume_id))
    else:
        print("Volume with id={} doesn't exists".format(volume_id))
        
all_instances = instances.values()




goodInstances = []
instancesWithMissingDisc = []
wrongRootVolume=[]
for instance in all_instances:
    exists = True
    existing_volumes=[]
    has_root_volume=False
    missing_volumes=[]
    for volume in instance.volumes:
        if os.path.isfile('volumes/volume-{}.vmdk'.format(volume.old_volume_id)):
             exists=exists & True
             existing_volumes.append(volume)
             has_root_volume=has_root_volume or (volume.mount_point=='/dev/vda')
        else:
             missing_volumes.append(volume.mount_point)
             exists=exists & False
    if exists:
        print('Complete VM {}'.format(instance.host_name))
        goodInstances.append(instance)
    elif has_root_volume:
	print('Not Complete VM {}- Root volume exists'.format(instance.host_name))
        for p in missing_volumes: print('   Missing volume {}'.format(p)) 
	instance.addVolumes(existing_volumes)
        instancesWithMissingDisc.append(instance)
    else:
        print('Wrong VM {} - No volume'.format(instance.host_name))
        for p in missing_volumes: print('   Missing volume {}'.format(p))
	wrongRootVolume.append(instance.host_name)
        
#	
print('-------------------------------')	
print('Good Instances              :{}'.format(len(goodInstances)))
print('Instances with missing disk :{}'.format(len(instancesWithMissingDisc)))
print('Instances with missing root :{}'.format(len(wrongRootVolume)))

all_instances = goodInstances+instancesWithMissingDisc


if is_run_mode==False:
    sys.exit() 


sys.exit() 


total=len(all_instances)
i=0
try:
    for instance in all_instances:
        i=i+1
        print('# Analyzing {}/{}'.format(i,total))
        print(instance)
        for volume in instance.volumes:
            print("   {}".format(volume))
            processVolume(volume)
        processInstance(instance)
except Exception as e: print(e)
finally:
    instanceFile = open(INSTANCE_STATUS_FILE,'w')
    volumeFile = open(VOL_STATUS_FILE,'w')
    for instance in all_instances:
        if instance.new_instance_id!=None:
            instanceFile.write('{},{}\n'.format(instance.old_instance_id,instance.new_instance_id)) 
        for volume in instance.volumes:
            if volume.new_volume_id!=None:
                volumeFile.write('{},{}\n'.format(volume.old_volume_id,volume.new_volume_id)) 
    volumeFile.close()
    instanceFile.close()

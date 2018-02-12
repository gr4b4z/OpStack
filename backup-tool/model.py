
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
      return str("Volume {} {} size {} id {}".format(self.display_name,self.mount_point,self.size,self.old_volume_id))

    def setMountPoint(self,mount_point):
        self.mount_point=mount_point
    
    def exists(self):
        return self.new_volume_id!=None

class Instance:
    def __init__(self, host_name,old_instance_id,flavor):
      self.host_name = host_name
      self.flavor  = flavor
      self.old_instance_id=old_instance_id
      self.new_instance_id=None
      self.volumes=[]
      self.exists = False


    def __str__(self):
      return str("Instance {} Flavor:{}  Id:{}".format(self.host_name,self.flavor,self.old_instance_id))

    def addVolume(self,volume):
      self.volumes.append(volume)
      self.volumes = sorted(self.volumes,key=lambda x: x.mount_point, reverse=False)
     
    def addVolumes(self,volumes):
      self.volumes = volumes
      self.volumes = sorted(self.volumes,key=lambda x: x.mount_point, reverse=False)
 
    def exists(self):
        return self.new_instance_id!=None

class Flavor:
    def __init__(self, name,memory,cpu):
      self.name = name
      self.ram = memory
      self.flavor_old_id = None
      self.cpu=cpu

    def __str__(self):
      return str("{} ({} MB,{} Cores)".format(self.name,self.ram,self.cpu))


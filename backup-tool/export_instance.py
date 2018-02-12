from model import Flavor,Volume,Instance

def export_metadata(user,passwd,project,url,instances = None):
	#global client
	from novaclient import client
	volume_list   = {}
	instance_list = {}
	flavor_list   = {}
	with client.Client('2', user,passwd,project,url) as nova:
		servers = nova.servers.list()
		flavors = nova.flavors.list()
		
		for fla in flavors:
			flavor_list[fla.id]=Flavor(fla.name,fla.ram,fla.vcpus)
			flavor_list[fla.id].flavor_old_id = fla.id
			
		for server in servers:
			if instances==None or instances != None and server.id in instances :
				instance_list[server.id]=Instance(server.name,server.id,flavor_list[server.flavor['id']])


	from cinderclient.v3 import client
	cinder = client.Client(user,passwd,project,url)
	volumes = cinder.volumes.list()
	for vol in volumes:
		for at in vol.attachments:
			if at['server_id'] in instance_list:
				s = instance_list[at['server_id']]
				volume=Volume(vol.id,vol.size,vol.bootable,vol.name,'yes')
				volume.setMountPoint(at['device'])
			        s.addVolume(volume)

	# if generate_output == False:
	return  (instance_list,flavor_list)	



	# print('====================== Instances =====================')	

	# instanceFile = open('backup_output.csv','w')
	# for instance in instance_list.values():
	# 	for volume in instance.volumes:
	            
	#             row=('{},{},{},{},{},{},{},{}'.format(instance.host_name, instance.old_instance_id, instance.flavor_id, volume.display_name, volume.mount_point, volume.is_bootable, volume.size,volume.old_volume_id)) 
	# 	    instanceFile.write("{}\n".format(row))
	# 	    print(row)
	# instanceFile.close()
	
	# print('====================== Flavors =======================')
				
	# instanceFile = open('flavor_output.csv','w')
	# for fla in flavor_list.values():
	#          row2 = ('{},{},{}\n'.format(fla.name,fla.cpu,fla.ram)) 
	#          instanceFile.write(row2)
	# 	 print(row2)
	# instanceFile.close()
	
	# return 	(instance_list,flavor_list)	


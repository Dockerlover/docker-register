from docker import Client
import etcd
import time
import os

POLL_TIMEOUT=60
ETCD_HOST = os.environ["ETCD_HOST"]
HOST_IP = os.environ["HOST_IP"]
DOCKER_HOST = os.environ["DOCKER_HOST"]

def get_images():
  c = Client(base_url=DOCKER_HOST)
  images = c.images()
  return images
  
def get_containers():
  c = Client(base_url=DOCKER_HOST)
  containers = c.containers(all=True)
  return containers

def get_container_info(container_id):
  c = Client(base_url=DOCKER_HOST)
  container = c.inspect_container(container_id)
  return container

def get_image_info(image_id):
  c = Client(base_url=DOCKER_HOST)
  image = c.inspect_image(image_id)
  return image

def get_etcd_addr():
  etcd_host = os.environ["ETCD_HOST"]
  
  port = 4001
  host = etcd_host

  if ":" in etcd_host:
    host, port = etcd_host.split(":")
  
  return host,port

def refresh_container(container_id,container):
  container_state =  container.get("State",{"Running",False})
  container_running = container_state.get("Running",False)
  container_start_dt = container_state.get("StartedAt","")
  container_image_id = container.get("Image","")
  
  client.write('/containers/'+container_id,
    "/"+container_image_id+"/"+str(container_running)+"/"+container_start_dt,
    ttl=3000 )
  
  return container
  
def refresh_image(image_id,image):
  container_id = image.get("Container","")
  image_size = image.get("Size","")
  image_create_dt = image.get("Created","")
  
  client.write('/images/'+image_id, 
    "/"+container_id+"/"+str(image_size)+"/"+image_create_dt, 
    ttl=3000 )
  return image

def refresh_service(container_id,image_id,container_info,container):
  container_config = container_info.get("Config",None)
  image_name = container_config.get("Image","")
  container_env = container_config.get("Env","")
  service_id = container_env.get("SERVICE_ID",None)
  
  if(service_id==None): 
    print "Error:No Service Id In Container["+HOST_IP+":"+container_id+"]!"
    return

  user_name = container_env("USER_NAME","admin")
  container_state =  contianer.get("State",{"Running",False})
  container_running = container_state.get("Running",False)
  
  
  container_ports = container.get("Ports",[])
  service_ports = []
  has_public_port = False
  for port in container_ports:
    if(port.get("PublicPort",None) != None):
      has_public_port = True
      service_ports.append({
        "public_port":port.get("PublicPort",""),
        "type":port.get("Type",""),
        "private_port":port.get("PrivatePort","") 
      })
  
  container_ports = ""
  if(has_public_port):
    p_i = 0
    for port in service_ports:
        container_ports +="/" port.get("type","")+":"+HOST_IP+":"+port.get("public_port","")+":"+port.get("private_port","")
  if container_ports=="":
    container_ports = "/"
  
  client.write('/services/'+user_name+'/'+service_id+'/'+container_id, container_ports, ttl=3000 )
  
  return container
  
  
def refresh(containers):
  host, port = get_etcd_addr()
  client = etcd.Client(host=host, port=int(port))
  
  for container in containers:
    container_id = container.get("Id",None)
    if(container_id==None) continue
    container_info = get_container_info(container_id)
    
    image_id = container_info.get("Image",None)
    if(image_id==None) continue
    image_info = get_image_info(image_id)
    
    refresh_container(container_id,image_id,container_info)
    refresh_image(image_id,image_info)
    refresh_service(container_id,image_id,container_info,container)
    
  return containers

if __name__ == "__main__":
    host, port = get_etcd_addr()
    client = etcd.Client(host=host, port=int(port))
    while True:
        try:
            containers = get_containers()
            if containers:
                print "containers refreshed. "
                refresh(containers)
                time.sleep(POLL_TIMEOUT)
                continue
        
        except Exception, e:
            print "Error:", e

        time.sleep(POLL_TIMEOUT)

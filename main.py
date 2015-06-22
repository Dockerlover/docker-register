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

def get_etcd_addr():
  etcd_host = os.environ["ETCD_HOST"]
  
  port = 4001
  host = etcd_host

  if ":" in etcd_host:
    host, port = etcd_host.split(":")
  
  return host,port

def refresh_containers(containers):

  host, port = get_etcd_addr()
  client = etcd.Client(host=host, port=int(port))
  
  # services = client.read('/services')
  # print services
  
  for container in containers:
    container_name = container.get("Id",None)
    container_image = container.get("Image",None)
    container_status = container.get("Status",None)
    container_ports = container.get("Ports",[])
    service_ports = []
    has_public_port = False
    for port in container_ports:
      if(port.get("PublicPort",None) != None):
        has_public_port = True
        service_ports.append({
          "public_port":port.get("PublicPort",None),
          "type":port.get("Type",None),
          "private_port":port.get("PrivatePort",None) 
        })
    
    if(has_public_port and container_name!=None):
      _prefix = '/services/'+container_name
      client.write(_prefix, None,dir=True, ttl=3000)
      client.write(_prefix+'/image', container_image, ttl=3000)
      client.write(_prefix+'/status', container_status, ttl=3000)
      _prefix = _prefix+"/ports"
      client.write(_prefix, None,dir=True, ttl=3000)
      for port in service_ports:
        port_prefix = _prefix+"/"+HOST_IP+":"+str(port.get("public_port",""))
        client.write(port_prefix+'/type', port.get("type"), ttl=3000)
    
  return containers

if __name__ == "__main__":
    host, port = get_etcd_addr()
    client = etcd.Client(host=host, port=int(port))
    while True:
        try:
            containers = get_containers()
            
            if containers:
                print "containers refreshed. "
                refresh_containers(containers)
                time.sleep(POLL_TIMEOUT)
                continue

        except Exception, e:
            print "Error:", e

        time.sleep(POLL_TIMEOUT)

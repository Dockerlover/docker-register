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
  
  services = client.get('/services')
  print services
  
  for container in containers:
    container_name = container.get("Id",None)
    container_image = container.get("Image",None)
    container_status = container.get("Status",None)
    container_ports = container.get("Ports",[])
    service_ports = []
    ports = []
    has_public_port = False
    for port in container_ports:
      port_public_port = port.get("PublicPort",None)
      port_private_port = port.get("PrivatePort",None)
      port_type = port.get("Type",None)
      ports.append({
        "public_port":port_public_port,
        "type":port_type,
        "private_port":port_private_port 
      })
      if(port_public_port != None):
        has_public_port = True
        service_ports.append({
          "public_port":port_public_port,
          "type":port_type,
          "private_port":port_private_port 
        })
    
    if(port_public_port and container_name!=None):
      _prefix = '/services/'+container_name
      client.write(_prefix, None, dir = True)
      client.write(_prefix+'/image', container_image)
      client.write(_prefix+'/status', container_status)
      client.write(_prefix+'/ports', None, dir = True)
      for port in service_ports:
        _prefix = _prefix+"/ports"
        client.write(_prefix+'/port', port.get("public_port"))
        client.write(_prefix+'/type', port.get("type"))
        client.write(_prefix+'/ip', DOCKER_HOST)
    
  return containers

if __name__ == "__main__":
    host, port = get_etcd_addr()
    client = etcd.Client(host=host, port=int(port))
    services = client.write('/services',None, dir = True)
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

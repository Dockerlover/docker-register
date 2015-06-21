from docker import Client
import etcd
import time

POLL_TIMEOUT=5

def get_images():
  c = Client(base_url='unix://var/run/docker.sock')
  images = c.images()
  return images
  
def get_containers():
  c = Client(base_url='unix://var/run/docker.sock')
  containers = c.containers(all=true)
  return containers

def refresh_containers(containers):
  print containers
  return containers
  
def container_changed():
  pass
  

if __name__ == "__main__":
    current_containers = {}
    while True:
        try:
            containers = get_containers()

            if not containers or containers == current_containers:
                refresh_containers(containers)
                time.sleep(POLL_TIMEOUT)
                continue

            print "containers changed. reload haproxy"
            container_changed()
            current_services = services

        except Exception, e:
            print "Error:", e

        time.sleep(POLL_TIMEOUT)

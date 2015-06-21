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
  containers = c.containers(all=True)
  return containers

def refresh_containers(containers):
  print containers
  return containers

if __name__ == "__main__":
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

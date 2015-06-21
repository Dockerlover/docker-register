HOST_IP=$(hostname --all-ip-addresses | awk '{print $1}')
ETCD_HOST=$HOST_IP:4001

docker run -it  --name register --rm   -e ETCD_HOST=$ETCD_HOST -e HOST_IP=$HOST_IP  \
-v /var/run:/var/run -v /var/docker_images/docker-register:/code docker-register /bin/bash

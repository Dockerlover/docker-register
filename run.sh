sudo git pull
docker build -t docker-register .

HOST_IP=$(hostname --all-ip-addresses | awk '{print $1}')
ETCD_HOST=$HOST_IP:4001

docker stop register
docker rm register

docker run -it  -d --name register \
-e ETCD_HOST=$ETCD_HOST -e HOST_IP=$HOST_IP  \
-v /var/docker_images/docker-register:/code \
-v /var/run:/var/run docker-register

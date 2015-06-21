# docker-register
Docker化etcd register

## 镜像特点

- 2015/6/21 继承基础镜像docker-ubuntu

## 使用方法

- 获取代码并构建

        git clone https://github.com/Dockerlover/docker-register.git
        cd docker-register
        docker build -t docker-register .

- 测试容器

        HOST_IP=$(hostname --all-ip-addresses | awk '{print $1}')
        
        docker run -it  --name register --rm  docker-register \
        -e ETCD_HOST=127.0.0.1:4001 -e HOST_IP=$HOST_IP  \
        -v /var/run:/var/run /bin/bash
        
        python main.py

- 运行容器

        docker run -it  -d --name register -v /var/run:/var/run docker-register

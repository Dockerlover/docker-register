# 基础镜像
FROM docker-python
# 维护人员
MAINTAINER  liuhong1.happy@163.com
# 添加环境变量
ENV USER_NAME admin
ENV SERVICE_ID register
ENV HOST_IP 127.0.0.1
# 应用相关的环境变量
ENV DOCKER_HOST unix:///var/run/docker.sock
ENV ETCD_HOST 127.0.0.1:4001
# 安装相关依赖包
RUN apt-get install -y libssl-dev libffi-dev
# 创建Docker配置文件路径
RUN touch /var/run/docker.sock
VOLUME ["/var/run","/code"]

# 复制代码
COPY . /code
WORKDIR /code
# 安装依赖包
RUN pip install -r pre-requirements.txt
RUN pip install -r requirements.txt
# 配置supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# 启动supervisord
CMD ["/usr/bin/supervisord"]

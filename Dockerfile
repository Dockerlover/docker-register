# 基础镜像
FROM docker-python
# 维护人员
MAINTAINER  liuhong1.happy@163.com
# 复制代码
COPY . /code
# 安装依赖包
COPY requirements.txt requirements.txt
RUN  pip install -r requirements.txt
# 配置supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# 启动supervisord
CMD ["/usr/bin/supervisord"]

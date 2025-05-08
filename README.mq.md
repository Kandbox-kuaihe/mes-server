
# IBMMQ ubnutu 版安装
https://www.ibm.com/support/pages/system/files/inline-files/MQ%209.2%20-%20deferring%20the%20acceptance%20of%20the%20license%20after%20the%20installation_3.pdf

# 创建队列管理器、队列、通道、window连接
https://blog.csdn.net/z19799100/article/details/129530009

参考 https://blog.csdn.net/z19799100/article/details/129497088

wget  https://public.dhe.ibm.com/ibmdl/export/pub/software/websphere/messaging/mqadv/mqadv_dev930_ubuntu_x86-64.tar.gz

tar -zxvf mqadv_dev930_ubuntu_x86-64.tar.gz

使用root 用户
su - 
./mqlicense.sh -accpet

 cd /opt/mqm/bin
 ./mqlicense -accept



dpkg -i ibmmq-runtime_9.3.0.0_amd64.deb
dpkg -i  ibmmq-sdk_9.3.0.0_amd64.deb
dpkg -i  ibmmq-gskit_9.3.0.0_amd64.deb
dpkg -i  ibmmq-server_9.3.0.0_amd64.deb
dpkg -i  ibmmq-client_9.3.0.0_amd64.deb
dpkg -i  ibmmq-samples_9.3.0.0_amd64.deb
dpkg -i  ibmmq-man_9.3.0.0_amd64.deb
dpkg -i  ibmmq-java_9.3.0.0_amd64.deb
dpkg -i  ibmmq-jre_9.3.0.0_amd64.deb
dpkg -i  ibmmq-gskit_9.3.0.0_amd64.deb

# 让它只返回安装路径
dspmqver -f 128


# 环境配置 
1.修改mqm用户密码

passwd mqm

#  修改环境变量 vim /etc/profile

chmod 777 /opt/mqm

PATH=$PATH:/opt/mqm/samp/bin

su - mqm     [123456]

启动队列管理器
strmqm QM16

停止队列
endmqm QM16

进入队列
runmqsc QM16

    启动监听
    start listener(TCP)

退出队列 
end


发送消息
amqsput  QUEUE_Q1 QM16
接受消息
amqsget  QUEUE_Q1 QM16


# PyMQI is expecting the MQ Client shared library to be in /usr/lib.
/opt/mqm/bin/setmqinst -i -n Installation1
rm -rf /usr/lib/libmqic_r.so 
ln -s   /opt/mqm/lib64/libmqic_r.so   /usr/lib/libmqic_r.so 


# python api  mq  参考
https://github.com/dsuch/pymqi
https://github.com/ibm-messaging/mq-dev-patterns/blob/master/Python/README.md




# 分区demo
CREATE TABLE dispatch_organization_test22.measurements (
    id serial4 NOT NULL,
    sensor_id INT NOT NULL,
    value FLOAT NOT NULL,
    measurement_time TIMESTAMP NOT null,
	CONSTRAINT measurements_pkey PRIMARY KEY (id,measurement_time)
) PARTITION BY RANGE (measurement_time);
 

CREATE TABLE dispatch_organization_test22.measurements_y2023m01 PARTITION OF dispatch_organization_test22.measurements
FOR VALUES FROM ('2023-01-01 00:00:00') TO ('2023-02-01 00:00:00');
 
CREATE TABLE dispatch_organization_test22.measurements_y2023m02 PARTITION OF dispatch_organization_test22.measurements
FOR VALUES FROM ('2023-02-01 00:00:00') TO ('2023-03-01 00:00:00');


INSERT INTO dispatch_organization_test22.measurements
(sensor_id, value, measurement_time)
VALUES(0, 0, '2023-01-01 10:00:00');

INSERT INTO dispatch_organization_test22.measurements
(sensor_id, value, measurement_time)
VALUES(0, 0, '2023-02-01 10:00:00');
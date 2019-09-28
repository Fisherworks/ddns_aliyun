# 阿里云DDNS自动化脚本（Python版）
**使用python操作阿里云API将本地公网IP自动打到指定由阿里云/万网提供服务的域名**
1. 确保你的路由器下有能够运行Python 2.7/3.x的广义计算机（电脑、NAS、可刷写openwrt或梅林等系统的路由器、甚至经过改动的手机等）
2. 安装requirements.txt中需要的python库，建议使用pip install -r requirements.txt
3. 将config_sample.json复制到config.json，设定RR，域名，阿里云key和secret（从阿里云管理界面获取，建议使用ram账户降低风险）
4. 运行`python ddns_update.py` 或者 `python3 ddns_update.py`检查执行效果，打完收工
5. 建议使用linux cron服务来让脚本定时运行
6. 建议使用python虚拟环境来管理该工程，避免该工程所需python库影响您的系统总体python环境
7. 对原理感兴趣请参考我的博客[基于阿里云API实现简单DDNS](http://fisherworks.cn/?p=2337)
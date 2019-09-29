# 阿里云DDNS自动化脚本（Python版）
**使用python操作阿里云API将本地公网IP自动打到指定由阿里云/万网提供服务的域名**
1. 确保你的路由器下有能够运行Python 2.7/3.x的广义计算机（电脑、NAS、可刷写openwrt或梅林等系统的路由器、甚至经过改动的手机等）
2. 安装requirements.txt中需要的python库，建议使用 `pip install -r requirements.txt`
3. 将config_sample.json复制到config.json，设定RR，域名，阿里云key和secret（从阿里云管理界面获取，建议使用ram账户降低风险）
4. 运行 `python ddns_update.py` 或者 `python3 ddns_update.py` 检查执行效果，打完收工
5. 建议使用linux cron服务来让脚本定时运行
6. 建议使用python虚拟环境来管理该工程，避免该工程所需python库影响您的系统总体python环境
7. 对原理感兴趣请参考我的博客[基于阿里云API实现简单DDNS](http://fisherworks.cn/?p=2337)
8. 脚本定时工作（假定10分钟一次）后日志文件大致如下

        [2019-09-29 10:40:02,184] Aliyun ip record of test.example.cn found - 222.222.222.222
        [2019-09-29 10:40:03,570] My public ip acquired - 222.222.222.222
        [2019-09-29 10:40:03,570] same ip - done exit   # 两IP一致，无需更新
        [2019-09-29 10:50:02,390] Aliyun ip record of test.example.cn found - 222.222.222.222
        [2019-09-29 10:50:03,189] My public ip acquired - 222.222.222.222
        [2019-09-29 10:50:03,190] same ip - done exit   # 两IP一致，无需更新
        [2019-09-29 11:00:02,413] Aliyun ip record of test.example.cn found - 222.222.222.222
        [2019-09-29 11:00:03,159] My public ip acquired - 333.333.333.333   # 本地公网IP变更（原因可能是光猫重启，可能是ISP强制更新），需对域名重设IP
        [2019-09-29 11:00:03,807] Aliyun ip record set done - {"RecordId":"1345678998764","RequestId":"22B56788-1094-4267-B537-24567890C"}
        [2019-09-29 11:00:03,808] done updated - exit   # 域名记录设置成功
        [2019-09-29 11:10:02,389] Aliyun ip record of test.example.cn found - 333.333.333.333
        [2019-09-29 11:10:05,432] My public ip acquired - 333.333.333.333
        [2019-09-29 11:10:05,432] same ip - done exit  # 两IP一致，无需更新
        [2019-09-29 11:20:02,142] Aliyun ip record of test.example.cn found - 333.333.333.333
        [2019-09-29 11:20:02,913] My public ip acquired - 333.333.333.333
        [2019-09-29 11:20:02,913] same ip - done exit

# Manto质量服务(回归环境)

## 环境准备
```
1.环境为python3.7
2.全局安装pipenv：pip install pipenv
3.项目根目录下：pipenv install (虚拟环境安装+依赖安装)
4.进入虚拟环境：pipenv shell
5.数据库准备：python manage.py makemigrations(settings文件夹下的配置项中不指定数据库即为django自带的sqlite)
6.数据库生成：python manage.py migrate
5.启动服务：python manage.py runserver 0.0.0.0:8000
6.建议用pycharm作为此项目的ide开发环境(vscode或者eclipse的支持体验力度有限)
```
## 代码入口
```
1.manto.schedule 文件夹下的urls即为本项目所有的接口入口
2.manto.schedule.handler是所有schedule应用下的处理器

ScheduleFlowHandler这个类是此服务的最关键，ScheduleFlowHandler下的flow_control方法是此服务的任务流管控
db2_handler为db2的相关处理
schedule_model_handler为此服务本身针对自身服务的mysql做了一些封装

3.manto.schedule.views即为接口对应的class方法
```
## 设计思路
```
采用工作流的设计思路，flow_control下总共为三个步骤：
1 清理和准备数据
2 运行shell脚本
3 验证数据

flow_control
根据传参决定是否运行单个case或全部case,捞出全部的待处理case,创建自身服务的一个主任务进入循环
(传参进来会判断是否有任务未执行结束，同一时刻只能有一条任务在跑)：

-第一个方法：进入clean_and_ready
首先任务明细表增加一条数据(任务号与主任务号相同)。
根据获取的对应case的clean字段的设定,进行对应表的truncate,此刻回写任务明细表的is_clean字段表示清理结束
清理后再根据对应case的ready字段的设定,进行对应表的copy，把用例表的数据copy到原始表，回写is_ready字段表示数据迁移结束

-第二个方法：进入run_batch
这里目前待完善，就是调个os的库进行shell命令的执行即可，根据设定拼成如下shell命令：
/home/cxlcs/runbatch.sh JAABDBY20 com.cathay.ab.y2.batch.ABY2_0150

-第三个方法：进入assert_data
捞取任务明细表全部待验证的数据,查询对应case_id的验证设定,根据设定把db2的验证表与原始表
进行比对，因为要记录每条数据明细+比对每一个字段，所以这边采用了主副表模式，数据多的表作为主表
跟副表进行比对，以免出现数组越界的情况。比对时根据验证设定的TAG，order 和 排除对应的字段与源数据
比对。验证完拼成json落在result结果表中。回写任务明细表is_assert字段,并且判断是否有余下待验证任务
如果没有，回写主任务is_done状态，任务结束
```
## 文档参考
```
django框架：https://docs.djangoproject.com/zh-hans/3.0/
django rest framework：https://www.django-rest-framework.org/
ibm-db：https://github.com/ibmdb/python-ibmdb
表结构直接看manto.schedule.models即可
```
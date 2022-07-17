# Swagger-hack 2.0

在测试中偶尔会碰到swagger泄露
常见的泄露如图：
![](https://github.com/jayus0821/swagger-hack/blob/main/images/image-20210201200842378.png)
有的泄露接口特别多，每一个都手动去试根本试不过来
于是用python写了个脚本自动爬取所有接口，配置好传参发包访问

**第一个版本仅适配了一个版本的swagger，不同版本间差距比较大，后续又调查了很多版本的swagger，将脚本的适配性增强了很多**

优化：
* 适配多个版本swagger
* 添加多进程
* 增强了程序的健壮性
* 优化了控制台显示，生成日志文件

单链接形式：
![](https://github.com/jayus0821/swagger-hack/blob/main/images/1.png)
文件形式：
![](https://github.com/jayus0821/swagger-hack/blob/main/images/2.png)

最终结果：
![](https://github.com/jayus0821/swagger-hack/blob/main/images/image-20210201201527999.png)



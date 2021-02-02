# swagger-hack

在测试中偶尔会碰到swagger泄露
常见的泄露如图：
![](https://github.com/jayus0821/swagger-hack/blob/main/images/image-20210201200842378.png)
有的泄露接口特别多，每一个都手动去试根本试不过来
于是用python写了个脚本自动爬取所有接口，配置好传参发包访问

原理是首先抓取http://url/swagger-resources
获取到有哪些标准及对应的文档地址
而后对每个标准下的接口文档进行解析，构造请求包，获取响应

尽量考虑到了所有可能的传参格式，实际测试只有少数几个会500或400响应需要手动修改一下，其余都是401或者200
200就是未授权访问接口了，可以进一步做其他诸如sqli等测试
运行时如图：
![](https://github.com/jayus0821/swagger-hack/blob/main/images/image-20210201200607110.png)
所有测试结果都存储在csv中：
![](https://github.com/jayus0821/swagger-hack/blob/main/images/image-20210201201527999.png)

欢迎大家关注稻草人安全团队，后续有更多技术文章、工具分享等
![](https://github.com/jayus0821/swagger-hack/blob/main/images/640.jpg)

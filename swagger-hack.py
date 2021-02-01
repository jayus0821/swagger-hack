import json
import time
import requests
import csv,numpy.compat.setup
 


def banner():
    print('''

                                              _                _    
 _____      ____ _  __ _  __ _  ___ _ __     | |__   __ _  ___| | __
/ __\ \ /\ / / _` |/ _` |/ _` |/ _ \ '__|____| '_ \ / _` |/ __| |/ /
\__ \\ V  V / (_| | (_| | (_| |  __/ | |_____| | | | (_| | (__|   < 
|___/ \_/\_/ \__,_|\__, |\__, |\___|_|       |_| |_|\__,_|\___|_|\_\\
                   |___/ |___/                                      
                                                            by jayus
    ''')

def get_specs(url):#获取标准列表
    specs_url = url + "/swagger-resources"
    res = requests.get(url = specs_url)
    #print(res.text)
    specs = json.loads(res.text)
    # for spec in specs:
    #     print(spec)#{'name': 'kt-research-biz', 'url': '/research/v2/api-docs', 'swaggerVersion': '2.0', 'location': '/research/v2/api-docs'}
    return specs

def check_spec(spec_url,url,f):#前一个是接口文档，用于分析，后一个是文档对应的实际接口请求地址
    res = requests.get(url = spec_url)
    try:
        paths = json.loads(res.text)['paths']
        print("[+] : 此标准下共有 %d 个接口"%(len(paths)))
    except:
        print("此标准为空")
        return 0

    for path in paths:
        print("[+] : 开始测试接口 %s " %(path))
        methods = paths[path]
        for method in methods:
            #print("接口请求方式: ",method)#get/post/put...
            #print( paths[path][method])#对应method的配置信息
            tags = paths[path][method]['tags'][0]
            summary = paths[path][method]['summary']
            #print("接口summary: ",summary)
            operationId = paths[path][method]['operationId']
            if 'consumes' in paths[path][method].keys():#json格式
                consumes = paths[path][method]['consumes'][0]
                #print(consumes)
            else:
                consumes = '0'
                
            if consumes != '0':#如果是json格式传输  post/put #post和post都是发送的json，但是接口文档并没有如何构造json的参数，目前只是随便发送一个
                #print("使用json格式传输")
                # json_array = {}
                # if 'parameters' in paths[path][method]:
                #     parameters = paths[path][method]['parameters']
                #     print("接口参数个数为 %d"%(len(parameters)))
                #     for parameter in parameters:
                #         #print(parameter)
                #         if parameter['type'] == "boolean":#布尔型全为true，string和数字全部为1
                #             json_array[parameter['name']] = 'true'
                #         else:
                #             json_array[parameter['name']] = '1'
                # else:
                #     json_array = ''
                #     print("接口参数个数为 %d"%(0))
                
                # print("构造请求参数...")
                # json_string = json.dumps(json_array)
                # print(json_string)

                json_string = '''{
  "contractNumber": "string",
  "createdBy": "string",
  "createdTime": "2021-02-01T09:33:58.398Z",
  "cutoffDate": "2021-02-01T09:33:58.398Z",
  "delFlag": "string",
  "dispatchForm": "string",
  "dispatchUnit": "string",
  "effectDate": "2021-02-01T09:33:58.398Z",
  "fileList": "string",
  "id": 0,
  "makeDate": "2021-02-01T09:33:58.398Z",
  "manageMethod": "string",
  "name": "string",
  "peopleNumber": "string",
  "remark": "string",
  "title": "string",
  "updatedBy": "string",
  "updatedTime": "2021-02-01T09:33:58.398Z"
}'''


                if method == "post":
                    res = requests.post(url = url + path , data = json_string)
                elif method == "put":
                    res = requests.put(url = url + path , data = json_string)
                # print(method)
                # print(url + path)
                # print(res.status_code)
                try:#post居然也可能没参数
                    row = [spec_url,summary,path,method,consumes,url + path,str(len(paths[path][method]['parameters'])),json_string,res.status_code,res.text]
                except:
                    row = [spec_url,summary,path,method,consumes,url + path,'0',json_string,res.status_code,res.text]
                writer.writerow(row)
                

            else:#不是json传输 
                # print("不使用json格式传输")
                if "{" in path:
                    # print("parameter in url")
                    parameter = paths[path][method]['parameters'][0]
                    try:
                        if parameter['type'] == "boolean":#布尔型全为true，string和数字全部为1
                            tmp = "true"
                        else:
                            tmp = "1"
                    except:
                        # print("no type")
                        tmp = "{1}"
                    if method == 'get':
                        res = requests.get(url = url + path[:path.index('{')] + tmp)
                        # print(method)
                    elif method == 'delete':
                        res = requests.delete(url = url + path[:path.index('{')] + tmp)
                        # print(method)
                    # print(url + path[:path.index('{')] + tmp)
                    # print(res.status_code)

                    row = [spec_url,summary,path,method,consumes,url + path[:path.index('{')],str(len(paths[path][method]['parameters'])),"",res.status_code,res.text]
                    writer.writerow(row)

                else:
                    query_string = ''
                    if 'parameters' in paths[path][method]:
                        parameters = paths[path][method]['parameters']
                        num_of_param = len(parameters)
                        # print("接口参数个数为 %d"%(len(parameters)))
                        for parameter in parameters:
                            #print(parameter)
                            try:
                                if parameter['type'] == "boolean":#布尔型全为true，string和数字全部为1
                                    query_string += "&%s=true"%(parameter['name'])
                                else:
                                    query_string += "&%s=1"%(parameter['name'])
                            except:
                                # print("no type...")
                                query_string += "&%s={1}"%(parameter['name'])
                    else:
                        query_string = ''
                        num_of_param = 0
                        # print("接口参数个数为 %d"%(0))
                    # print("构造请求参数...")
                    query_string = query_string[1:]
                    # print(query_string)

                    if method == "get":
                        res = requests.get(url = url + path + "?" + query_string)
                        # print(method)
                    elif method == "delete":
                        res = requests.delete(url = url + path + "?" + query_string)
                    #     print(method)
                    # print(url + path + query_string)
                    # print(res.status_code)

                    row = [spec_url,summary,path,method,consumes,url + path + "?" + query_string,str(num_of_param),"",res.status_code,res.text]
                    writer.writerow(row)




        # print("================")
        # print()

        time.sleep(0)


if __name__ == '__main__':
    banner()
    url = "https://xx.xx.xx"#eg:https://pay2.kuairui.tech/swagger-ui.html 只取前面host部分
    specs = get_specs(url)
    print("[+] 共抓取到 %d 个标准"%(len(specs)))

    f = open('swagger.csv','w',newline='',encoding='utf-8')#写到csv中
    writer = csv.writer(f)
    try:
        writer.writerow(["标准","summary","path","method","consumes","url","num of params","data","status_code","response"])
    except Exception as e:
        print(e)

    for spec in specs:
        spec_url = url + spec['url']
        pre = spec['url'].split('/')[1]
        print("[+] : 开始测试 %s 标准"%(spec_url))
        check_spec(spec_url,url + "/" + pre,f)
        #break

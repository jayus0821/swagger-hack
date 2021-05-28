#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import json,os,re
import time, sys
from urllib.parse import urlparse
import requests
import csv
import argparse
from multiprocessing import Pool, Manager
requests.packages.urllib3.disable_warnings()


from loguru import logger
logger.remove()
handler_id = logger.add(sys.stderr, level="DEBUG")#设置输出级别




payload_array = {"string":"1","boolean":"true","integer":"1","array":"1","number":"1","object":""} #根据参数类型进行赋值

#post类型就发送这个数据
json_payload = """{
  "code": "string",
  "createTime": "2021-02-05T10:34:37.691Z",
  "delFlag": "string",
  "deptId": 0,
  "fullName": "string",
  "fullPathCode": "string",
  "fullPathName": "string",
  "isVirtual": true,
  "name": "string",
  "outCode": "string",
  "outParentCode": "string",
  "parentCode": "string",
  "parentId": 0,
  "parentName": "string",
  "sort": 0,
  "updateTime": "2021-02-05T10:34:37.691Z"
}"""

def banner():
    logger.info('''

                                              _                _    
 _____      ____ _  __ _  __ _  ___ _ __     | |__   __ _  ___| | __
/ __\ \ /\ / / _` |/ _` |/ _` |/ _ \ '__|____| '_ \ / _` |/ __| |/ /
\__ \\ V  V / (_| | (_| | (_| |  __/ | |_____| | | | (_| | (__|   < 
|___/ \_/\_/ \__,_|\__, |\__, |\___|_|       |_| |_|\__,_|\___|_|\_\\
                   |___/ |___/                                      
                                                            by jayus
    
    
python swagger.py -h
---------------------------------------------------------------------
    ''')


def check(url):
    try:
        res = requests.get(url = url, timeout = 5, verify = False)
        if "<html" in res.text:
            logger.debug("[+] 输入url为swagger首页，开始解析api文档地址")
            return 3 #html
        elif "\"parameters\"" in res.text:
            logger.debug("[+] 输入url为api文档地址，开始构造请求发包")
            return 2 #api doc
        elif "\"location\"" in res.text:
            logger.debug("[+] 输入url为resource地址，开始解析api文档地址")
            return 1 #source
    except KeyboardInterrupt:
        print("kill")
    except Exception as e:
        print(e)
        return 0
    

def savedata(filename):
    if ".csv" in filename:
        pass
    elif ".txt" in filename:
        pass


def get_api_docs_pathes(resource_url):#输入resource，解析出各api文档的url
    domain = urlparse(resource_url)
    domain = domain.scheme + "://" + domain.netloc
    try:
        res = requests.get(url = resource_url, verify = False, timeout = 10)
        resources = json.loads(res.text)
    except Exception as e:
        print(e)
        return []

    pathes = []
    if isinstance(resources,tuple):
        if "apis" in resources.keys():#版本不同，格式不一样
            for api_docs in resources['apis']:
                pathes.append(domain + api_docs['path'])
            return pathes
    else:
        for i in resources:
            pathes.append(domain + i['location'])
        return pathes
    





def go_source(url):
    pass




def go_docs(url,global_data):
    try:
        domain = urlparse(url)
        domain = domain.scheme + "://" + domain.netloc
        try:
            res = requests.get(url = url, timeout = 5, verify = False)
        except:
            logger.error("timeout...")
        res = json.loads(res.text)
        basePath = ''
        if "basePath" in res.keys():
            basePath = res['basePath']  #eg:/santaba/rest
        elif "servers" in res.keys():
            basePath = res["servers"]['url']
        else:
            basePath = ''
        paths = res['paths']
        path_num = len(paths)
        logger.info("[+] {} has {} paths".format(url,len(paths)))
        for path in paths:#path字符串
            res_path = path
            logger.debug("test on {} => {}".format(url,path))
            try:
                for method in paths[res_path]:#get/post/字符串
                    path = res_path
                    text = str(paths[path][method])
                    param_num = text.count("'in':")
                    try:
                        summary = paths[path][method]['summary'] 
                    except:
                        summary = path
                    if method == 'post' or method == 'put':#这两种请求，参数如何构造在接口文档中没有，暂时不知道在哪找，所以随便发一个包
                                                            #post分没参数和有参数两种，没参数直接随便post个json，有参数但是in body还是json
                                                            #有参数但是in path 就判断类型填到path 。in query就需要构造了
                        if "'in': 'body'" in text:
                            if method == 'post':
                                req = requests.post(url = domain + basePath + path , data = json_payload,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,domain + basePath + path,param_num,json_payload,req.status_code,req.text]
                            else:
                                req = requests.put(url = domain + basePath + path , data = json_payload,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,domain + basePath + path,param_num,json_payload,req.status_code,req.text]
                        elif "'in': 'path'" in text:
                            param_map = {}
                            parameters = paths[path][method]['parameters']
                            for param in parameters:
                                p_type = ''
                                if "type" in param.keys():
                                    p_type = param['type']
                                elif "schema" in param.keys():
                                    if "type" in param["schema"].keys():
                                        p_type = param['schema']['type']
                                p_name = param['name']
                                param_map[p_name] = payload_array[p_type]
                            if "{" in path:
                                tmps = re.findall("\{[^\}]*\}",path)
                                for tmp in tmps:
                                    path = path.replace(tmp,param_map[tmp[1:-1]]) 
                            if method == 'post':
                                req = requests.post(url = domain + basePath + path , data = json_payload,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,domain + basePath + path,param_num,json_payload,req.status_code,req.text]
                            else:
                                req = requests.put(url = domain + basePath + path , data = json_payload,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,domain + basePath + path,param_num,json_payload,req.status_code,req.text]
                        elif "'in': 'query'" in text:
                            param_map = {}
                            parameters = paths[path][method]['parameters']
                            for param in parameters:
                                p_type = ''
                                if "type" in param.keys():
                                    p_type = param['type']
                                elif "schema" in param.keys():
                                    if "type" in param["schema"].keys():
                                        p_type = param['schema']['type']
                                p_name = param['name']
                                param_map[p_name] = payload_array[p_type]
                            if method == 'post':
                                req = requests.post(url = domain + basePath + path , data = param_map,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,domain + basePath + path,param_num,param_map,req.status_code,req.text]
                            else:
                                req = requests.put(url = domain + basePath + path , data = param_map,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,domain + basePath + path,param_num,param_map,req.status_code,req.text]
                        else:#没有parameters这个key
                            if method == 'post':
                                req = requests.post(url = domain + basePath + path , data = json_payload,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,domain + basePath + path,param_num,json_payload,req.status_code,req.text]
                            else:
                                req = requests.put(url = domain + basePath + path , data = json_payload,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,domain + basePath + path,param_num,json_payload,req.status_code,req.text]
                        global_data.put(hhh)

                    elif method == "get" or method == "delete":
                        querystring = ""
                        param_map = {}
                        if "parameters" in paths[path][method].keys():#有参数
                            parameters = paths[path][method]['parameters']
                            for param in parameters:
                                p_type = ''
                                if "type" in param.keys():
                                    p_type = param['type']
                                elif "schema" in param.keys():
                                    if "type" in param["schema"].keys():
                                        p_type = param['schema']['type']
                                p_in = param['in']
                                p_name = param['name']
                                try:
                                    param_map[p_name] = payload_array[p_type]
                                except:
                                    logger.error("参数类型不全，需要手动添加... => {}".format(p_type))
                            for key in param_map.keys():
                                querystring = querystring + key + "=" + param_map[key] + "&"
                            if "{" in path:
                                tmps = re.findall("\{[^\}]*\}",path)
                                for tmp in tmps:
                                    path = path.replace(tmp,param_map[tmp[1:-1]]) #替换掉basePath里的{abc}
                            query_url = domain + basePath + path + '/?' + querystring[:-1]
                            if method == 'get':
                                req = requests.get(url = query_url,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,query_url,param_num,param_map,req.status_code,req.text]
                            else:
                                req = requests.delete(url = query_url,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,query_url,param_num,param_map,req.status_code,req.text]
                        
                        else:#无参数
                            try:
                                query_url = domain + basePath + path
                            except Exception as e:
                                print(e)
                            if method == 'get':
                                req = requests.get(url = query_url,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,query_url,param_num,param_map,req.status_code,req.text]
                            else:
                                req = requests.delete(url = query_url,timeout = 5,verify = False)
                                hhh = [url,summary,path,method,query_url,param_num,param_map,req.status_code,req.text]


                        global_data.put(hhh)

                    else:
                        logger.error("[!] 遇到了没有添加的请求方法...{}".format(method))
                        #exit()
            except Exception as e:
                logger.error(e)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        logger.error(e)


def go_html(urlq,q):
    pass


def run(data):
    url = data[0]
    q = data[1]
    url_type = check(url)
    if url_type == 0:
        logger.error("[!] Error")
        exit()
    elif url_type == 1:
        logger.success("working on {}".format(url) ,"type: source")
        go_source(url,q)
    elif url_type == 2:
        logger.success("working on {}".format(url) ,"type: api-docs")
        go_docs(url,q)
    else:
        logger.success("working on {}".format(url) ,"type: html")
        go_html(url,q)


def print_error(value):
    print("进程池出错,出错原因为: ", value)

def run_pool(urls):
    p = Pool(8)
    manager = Manager()
    q = manager.Queue()
    for url in urls:
        url = url.strip()
        param = [url,q]
        p.apply_async(run,args=(param,),error_callback=print_error)
    p.close()
    p.join() 
    output_to_csv(q)


def output_to_csv(global_data):
    f = open('swagger.csv','w',newline='',encoding='utf-8')#写到csv中
    writer = csv.writer(f)
    try:
        writer.writerow(["api-doc-url","summary","path","method","query_url","num of params","data","status_code","response"])
    except Exception as e:
        print(e)
    while not global_data.empty():
        writer.writerow(global_data.get())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest='target_url', help="resource地址 or api文档地址 or swagger首页地址")
    parser.add_argument("-f", "--file", dest='url_file', help="批量测试")
    args = parser.parse_args()


    logger.add("file.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
    banner()
    if args.target_url:
        run_pool([args.target_url])
    elif args.url_file:
        f = open(args.url_file, 'r')
        urls = f.readlines()
        run_pool(urls)

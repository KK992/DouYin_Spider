import os
import requests
import base64


class AutomatedAdvertisingCollection:
    
    apiHost = os.getenv('SJZHLW_SERVICE_HOST')

    @classmethod
    def upload_file(cls, filePath:str, **kwargs):
        """
        上传文件到后台.
        :param cls: class object.
        :param filePath: 本地文件路径.
        :return: JSON.
        """
        api = f'{cls.apiHost}/Api/AutomatedAdvertisingCollection/UploadFile';

        try:
            files = {
                'file': open(filePath,'rb')  # 'file' 对应 C# 后台的 IFormFile file
            }
            data = {
               
            }
            response = requests.post(api, data=data, files = files)
            if response.status_code == 200 and response.json()["Success"] == True:
                print("文件上传成功！服务器返回:", response.json())
                return response.json()
            else:
                print(f"文件上传失败，状态码: {response.status_code}")
                print("错误信息:", response.text)
                return response.json()
        except Exception as e:
            print("文件上传发生异常:", str(e))
            return {"Success":False, "Message": str(e)}
        finally:
            files['file'].close()

    @classmethod
    def upload_base64file(cls, filePath:str, **kwargs):
        """
        上传base64文件到后台.
        :param cls: class object.
        :param filePath: 本地文件路径.
        :return: JSON.
        """
        api = f'{cls.apiHost}/Api/AutomatedAdvertisingCollection/UploadBase64File';

        try:
            with open(filePath,'rb') as file:
                file_base64_str = base64.b64encode(file.read()).decode('utf-8')
                file_name = os.path.basename(filePath)
                name, ext = os.path.splitext(file_name)
                file_name = name
                file_type = ext.replace(".","")
            jsondata = {
                "base64file": file_base64_str,
                "name": file_name,
                "type": file_type
            }
            response = requests.post(api,json = jsondata)
            if response.status_code == 200 and response.json()["Success"] == True:
                print("文件上传成功！服务器返回:", response.json())
                return response.json()
            else:
                print(f"文件上传失败，状态码: {response.status_code}")
                print("错误信息:", response.text)
                return response.json()
        except Exception as e:
            print("文件上传发生异常:", str(e))
            return {"Success":False, "Message": str(e)}
        finally:
            file.close()

    @classmethod      
    def AddDYAdvertising(cls, advJson, ** kwargs):
        """
        上传抖音广告信息.
        :param cls: class object.
        :param advJson: 广告信息.
        :return: JSON.
        """

        api = f'{cls.apiHost}/Api/AutomatedAdvertisingCollection/AddDYAdvertising';
        try:
            jsonData = advJson
            response = requests.post(api,json=jsonData)
            if response.status_code == 200 and response.json()["Success"] == True:
                print("抖音广告上传成功！服务器返回:", response.json())
                return response.json()
            else:
                print(f"抖音广告上传失败，状态码: {response.status_code}")
                print("错误信息:", response.text) 
                return response.json()           
        except Exception as e:
            print("抖音广告上传发生异常:", str(e))
            return {"Success":False, "Message": str(e)}
 
if __name__ == '__main__':
    # 本地要上传的文件路径
    path = "/Users/kangkai/Documents/源码/抖音爬虫/DouYin_Spider/datas/media_datas/承德热河青年文化传媒有限公司_87381891354/承德单青年看过来，躺平大赛即将开幕，快来报名吧承德躺平大赛开幕快来找我报名吧，躺_7680367745159277504/video.mp4" 
    AutomatedAdvertisingCollection.upload_base64file(filePath=path)


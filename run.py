import hashlib
import json
import os

import redis
import requests
import threadpool

save_path = input("Please input avatar save path : ")
while not os.path.exists(save_path):
    save_path = input("Path not find. Re-put : ")

if save_path[-1] != "\\" or save_path[-1] != "/":
    save_path += "/"


class DTAvatar:
    def __init__(self, img_save_path):
        self.img_count = 0
        self.save_path = img_save_path
        self.__connect_redis()

    def __connect_redis(self):
        try:
            self.redis = redis.Redis(host="127.0.0.1", port="6379", db=0)
            redis_info = self.redis.info()
            print("Redis Version: %s" % (redis_info["redis_version"]))
        except Exception as redis_err:
            print(redis_err)

    @staticmethod
    def __md5sum(filename, block_size=65536):
        img_hash = hashlib.md5()
        with open(filename, "rb") as f:
            # 必须是rb形式打开的，否则的两次出来的结果不一致
            for block in iter(lambda: f.read(block_size), b""):
                img_hash.update(block)
        return img_hash.hexdigest()

    @staticmethod
    def __find_last(string, find_str):
        last_position = -1
        while True:
            position = string.find(find_str, last_position + 1)
            if position == -1:
                return last_position + 1
            last_position = position

    def get_img_name(self, img_url):
        return img_url[self.__find_last(img_url, "/"): len(img_url)]

    def __check_img(self, img_file):
        md5 = self.__md5sum(self.save_path + img_file)
        if self.redis.get(md5) is None:
            self.redis.set(md5, "true")
            self.img_count += 1
            # print("%s[%s] Download completed" % (img_file, md5))
        else:
            os.remove(self.save_path + img_file)
            print(img_file + " has existed")

    def get_img_count(self):
        return self.img_count

    def read_img(self, img_url):
        img_name = img_url[self.__find_last(img_url, "/"):len(img_url)]
        img_res = requests.get(img_url)
        try:
            with open(save_path + img_name, 'wb') as f:
                f.write(img_res.content)
            self.__check_img(img_name)
        except IOError as save_err:
            print("[Error]%s save failed case : %s" % (img_name, save_err))


avatar = DTAvatar(save_path)

images_dict = dict()
start = 0  # 头像开始参数
total = 1  # 总计头像页数
filter_id = "头像_女生"  # 头像类别
pool = threadpool.ThreadPool(10)  # 创建线程池
count = 0  # 已经循环次数
while start < total:  # 判断是否采集完成
    images_list = list()
    url = "https://www.duitang.com/napi/blog/list/by_filter_id/?filter_id=" + filter_id + "&start=" + str(start)
    try:
        response = requests.get(url)
        obj = json.loads(response.text)
        start = int(obj["data"]["next_start"])
        total = int(obj["data"]["total"])
        for photo in obj["data"]["object_list"]:
            img_path = photo["photo"]["path"]
            img_msg = photo["msg"]
            file_name = avatar.get_img_name(img_path)
            like_count = photo["favorite_count"]
            images_dict[file_name] = like_count
            if img_path != "":
                images_list.append(img_path)
        requests_pool = threadpool.makeRequests(avatar.read_img, images_list)  # 加入线程池任务
        [pool.putRequest(req) for req in requests_pool]
        pool.wait()
        count += 1
        print("Total : %d Next start : %d Already count : %d" % (total, start, count))
    except IOError as err:
        print(err.args)
images_dict = sorted(images_dict.items(), key=lambda x: x[1], reverse=True)
report = ""
for item in images_dict:
    report += item[0] + "   " + str(item[1]) + "\n"
f = open(save_path + "report.txt", "w")
f.write(report)
f.close()
print("[Completed] Images count : %d Thanks your use !" % avatar.get_img_count())

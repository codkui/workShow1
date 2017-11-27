## -*- coding: UTF-8 -*-
import time
import json
import random

dataModel=[]
mappingList=[]
allMapping=[]
workLine=[]
makeWorkLineS=[]
#生成地形总集
def makeMapping():
    for i in range(len(dataModel)):
        #mappingList.append(dataModel[i]["mapping"])
        #转换为相对第一点的相对坐标
        mappingZero=[]
        mappingSample=json.loads(json.dumps(dataModel[i]["mapping"]))
        zero=json.loads(json.dumps(mappingSample[0]))
        #print(zero)
        for n in range(len(mappingSample)):
            mappingSample[n][0]=mappingSample[n][0]-zero[0]
            mappingSample[n][1]=mappingSample[n][1]-zero[1]
            #print(mappingSample[n])
        mappingList.append([mappingSample,dataModel[i]["workArea"],dataModel[i]["workTime"],dataModel[i]["charge"],dataModel[i]["flyNum"]])
        #print(mappingSample)
        for n in range(len(mappingSample)):
            newSample=json.loads(json.dumps(mappingSample))
            del newSample[n]
            mappingList.append([newSample,dataModel[i]["workArea"],dataModel[i]["workTime"],dataModel[i]["charge"],dataModel[i]["flyNum"]])
    return
#记录有作业点集
def getWorkLine():
    for i in range(len(dataModel)):
        workLine.append(json.loads(json.dumps([dataModel[i]["mapping"][0],dataModel[i]["province"],dataModel[i]["city"],dataModel[i]["district"]])))

#生成偏移点集

def makeWorkLine():
    hadList={}
    for i in range(len(workLine)):
        lat=int(workLine[i][0][0]*100)
        lng=int(workLine[i][0][1]*100)
        hadList[str(lat)+"-"+str(lng)]=True
        for n in range(100):
            a=random.randint(1,20000)
            b=random.randint(1,20000)
            newLat=workLine[i][0][0]+a/2000  #这里是计算的每1000/2 的范围为随机格
            newLng=workLine[i][0][1]+b/2000
            lat=int(newLat*100)
            lng=int(newLng*100)
            if hadList.get(str(lat)+"-"+str(lng),False)!=True:
                hadList[str(lat)+"-"+str(lng)]=True
                makeWorkLineS.append([[newLat,newLng],workLine[i][1],workLine[i][2],workLine[i][3]])
    random.shuffle(makeWorkLineS)

#根据地形与点，生成作业路径
def makeRelMapping(line,mapping):
    newMapping=[]
    for i in range(len(mapping)):
        newMapping.append([mapping[i][0]+line[0],mapping[i][1]+line[1]])
    return newMapping

#加载数据，清洗不合理的数据
def loadData():
    with open("./无标题.json","r+") as f:
        data=f.read()
        data=json.loads(data)
        data=data["RECORDS"]
        for i in range(len(data)):
            #print(data[i]["Id"])
            if int(data[i]["workTime"])>3600:
                continue
            if data[i]["type"]=="line":
                continue
            workLines=json.loads(data[i]["mappingBorder"])
            if workLines[0][0]>30.49 and workLines[0][0]<30.53 and workLines[0][1]>104.1 and workLines[0][1]<104.14:
                continue
            #workTime=int(time.mktime(time.strptime(data[i]["flyEndTime"],"%Y-%m-%d %H:%M:%S")))-int(time.mktime(time.strptime(data[i]["flyStartTime"],"%Y-%m-%d %H:%M:%S")))
            workInfos=data[i]["uavInfo"].split("@@@,")
            # print(len(workInfos))
            # print(data[i]["uavInfo"])
            # print(workInfos)
            if len(workInfos)<1:
                workYao=0
            else:
                workYao=0 
                for n in range(len(workInfos)):
                    if workInfos[n][-1]!="]":
                        continue
                    #print(workInfos[n])
                    workInfos[n]=workInfos[n].replace("@@@","")
                    workYaoO=json.loads(workInfos[n])
                    #print(workYaoO)
                    if len(workYaoO)<=1:
                        workYao+=0
                    else:
                        workYao+=(int(workYaoO[0]["charge"])-int(workYaoO[-1]["charge"]))
            dataModel.append({"province":data[i]["province"],"city":data[i]["city"],"district":data[i]["district"],"mapping":workLines,"title":data[i]["title"],"workArea":data[i]["workArea"],"workTime":data[i]["workTime"],"charge":workYao,"flyNum":data[i]["flyNum"]})
        return True


#根据面积参数增加数据

def addMapping(doneArea):
    doneMapping=[]
    hadArea=0
    maxMapping=len(mappingList)
    for i in range(len(dataModel)):
        doneMapping.append(dataModel[i])
        hadArea+=float(dataModel[i]["workArea"])
    c=0
    
    while hadArea<doneArea:
        if len(makeWorkLineS)==0:
            print("已有设置生成的面积过小::"+str(hadArea))
            return doneMapping
        c+=1
        cha=random.randint(0,maxMapping-1)
        mapping=json.loads(json.dumps(mappingList[cha]))
        line=makeWorkLineS.pop(0)
        relMapping=makeRelMapping(line[0],mapping[0])
        relSample={"province":line[1],"city":line[2],"district":line[3],
        "mapping":relMapping,"title":"","workArea":mapping[1],"workTime":mapping[2],"charge":mapping[3],"flyNum":mapping[4]}
        doneMapping.append(relSample)
        hadArea+=float(mapping[1])
        # print(c)
        # print(cha)
        # print(mapping[1])
        # print(hadArea)
    print("已生成作业面积: %s 亩" % (hadArea))
    print("生成作业数: %s 次" % (c))
    return doneMapping

def tongji(mapping):
    cityList={}
    allInfo={"workArea":0,"flyNum":0,"charge":0,"time":0,"workNum":0}
    allList={}
    for i in range(len(mapping)):
        #格式化省市地址
        if mapping[i]["province"][-1]!="省":
            mapping[i]["province"]=mapping[i]["province"]+"省"
        if mapping[i]["city"][-1]!="市":
            mapping[i]["city"]=mapping[i]["city"]+"市"
        hadProvince=cityList.get(mapping[i]["province"],False)
        if hadProvince==False:
            cityList[mapping[i]["province"]]={"list":{},"workArea":0,"flyNum":0,"charge":0,"time":0,"workNum":0}
        hadCity=cityList[mapping[i]["province"]]["list"].get(mapping[i]["city"],False)
        if hadCity==False:
            cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]={"list":{},"workArea":0,"flyNum":0,"charge":0,"time":0,"workNum":0}
        hadDistrict=cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["list"].get(mapping[i]["district"],False)
        if hadDistrict==False:
            cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["list"][mapping[i]["district"]]={"list":{},"workArea":0,"flyNum":0,"charge":0,"time":0,"workNum":0}
        allInfo["workArea"]+=float(mapping[i]["workArea"])
        allInfo["flyNum"]+=float(mapping[i]["flyNum"])
        allInfo["charge"]+=float(mapping[i]["charge"])
        allInfo["time"]+=float(mapping[i]["workTime"])
        allInfo["workNum"]+=1
        cityList[mapping[i]["province"]]["workArea"]+=float(mapping[i]["workArea"])
        cityList[mapping[i]["province"]]["flyNum"]+=float(mapping[i]["flyNum"])
        cityList[mapping[i]["province"]]["charge"]+=float(mapping[i]["charge"])
        cityList[mapping[i]["province"]]["time"]+=float(mapping[i]["workTime"])
        cityList[mapping[i]["province"]]["workNum"]+=1
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["workArea"]+=float(mapping[i]["workArea"])
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["flyNum"]+=float(mapping[i]["flyNum"])
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["charge"]+=float(mapping[i]["charge"])
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["time"]+=float(mapping[i]["workTime"])
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["workNum"]+=1
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["list"][mapping[i]["district"]]["workArea"]+=float(mapping[i]["workArea"])
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["list"][mapping[i]["district"]]["flyNum"]+=float(mapping[i]["flyNum"])
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["list"][mapping[i]["district"]]["charge"]+=float(mapping[i]["charge"])
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["list"][mapping[i]["district"]]["time"]+=float(mapping[i]["workTime"])
        cityList[mapping[i]["province"]]["list"][mapping[i]["city"]]["list"][mapping[i]["district"]]["workNum"]+=1
        if allList.get(mapping[i]["province"]+"-"+mapping[i]["city"]+"-"+mapping[i]["district"],False)==False:
            allList[mapping[i]["province"]+"-"+mapping[i]["city"]+"-"+mapping[i]["district"]]=[]
        allList[mapping[i]["province"]+"-"+mapping[i]["city"]+"-"+mapping[i]["district"]].append(mapping[i])
    with open("info/allInfo.json","w+") as f:
        json.dump(allInfo,f)
    with open("info/cityList.json","w+") as f:
        json.dump(cityList,f)
    for k in allList:
        with open("info/"+k+".json","w+") as f:
            json.dump(allList[k],f)
    return cityList,allInfo
if __name__=="__main__":
    loadData()
    #print(dataModel)
    #exit()
    makeMapping()
    print("生成的随机测绘模型: %s 个" % (len(mappingList)))
    
    getWorkLine()

    makeWorkLine()
    #print(makeWorkLineS)
    print("已有的随机作业点: %s 个" % (len(workLine)))
    print("生成的随机作业点: %s 个" % (len(makeWorkLineS)))
    a=addMapping(634250)
    tongji(a)
    #print(a)

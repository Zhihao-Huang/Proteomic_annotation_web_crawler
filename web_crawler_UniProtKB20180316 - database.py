#coding=utf-8
#################################################################################################################
#功能：根据基因名csv文件检索Uniprot数据库,匹配对应accession号，再进行GO注释,生成xls文件。
#六个输入参数：1、工作路径；2、输入geneID文件名；3、输出文件名；4、输出重新检索文件名；5、输出无法检索文件名；6、GO数据库名。
#注意：
#1、geneID的csv文件是1列n行的结构；
#2、结果文件中的第二列也是基因名，根据accession号生成，可以与第一列的输入文件基因名比较，校对是否匹配到正确的ac号；
#3、python2.7版本；
#4、需要先安装模块：pyExcelerator。
#Version: Web_Crawler20180316;select GO database.
#author：huangzhihao@genomics.cn
#################################################################################################################
import urllib
import re
import socket
import os
import time
from pyExcelerator import *

workspace = 'C:\\Users\\huangzhihao\\Desktop'
GOdatabase = '.*?'
inputfile = 'gene.csv'
outputfile = 'gene_annotation_d.xls'
annot_com = 'gene_annotationcomplement_d.xls'
genemiss = 'gene_annotation_miss_d.txt'

starttime = time.asctime(time.localtime(time.time()))
os.chdir(workspace)#1、修改工作路径。
def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html

def gettitle(html):
    reg = r'<title>.*?</title>'
    titre = re.compile(reg)
    titl = re.findall(titre,html)
    titlist = re.match(r'<title>(.*?)\ -\ (.*?)\ -\ (.*?)</title>',titl[0])#一次正则匹配不到，用两次；不能match列表，用字符串
    
    return titlist
def getfunc(html):
    ref = r'</script><meta content=.*?</head>'
    funre = re.compile(ref)
    fun = re.findall(funre,html)
    funlist = re.match(r'</script><meta content=\"(.*?)\"(.*?)</head>',fun[0])
    return funlist

def getgo(html):
    reg = r';\">.*?Source\: '+ GOdatabase +'<'
    gore = re.compile(reg)
    gol = gore.findall(html)
    golistr =[]
    for i in range(len(gol)):
        if len(gol[i]) < 5000:
            golistr.append(gol[i])
        else:
            break
    golist =[]
    for i in range(len(golistr)):
        go = re.findall(r';\">(.*?)</a>',str(golistr[i]))
        if len(go) <500:
            golist.append(go[-1])
    return golist

with open(inputfile) as a:  ##2、修改输入文件名。导入基因名。导入之前要保证csv中的基因名在第一列。
    geneid = []
    for line in a.readlines():
        geneid.append(line.strip())
w=Workbook()
ws = w.add_sheet('id')
ws.write(0,0,"GeneID")        ##五个列名
ws.write(0,1,"GeneID_ac")
ws.write(0,2,"Protein Names")
ws.write(0,3,"function")
database_name = 'alldatabase' if GOdatabase =='.*?' else GOdatabase
ws.write(0,4,"GO_annotation"+"_"+database_name)

missac = []
network = 'The network connection is successful!'
for i in range(len(geneid)):
    socket.setdefaulttimeout(30)
    try:
        htmls = getHtml("http://www.uniprot.org/uniprot/?query=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22+"+geneid[i]+"&sort=score")  #联网搜ac号
        ref = r'</script></td></tr></thead><tbody><tr\ id=\".*?\" class=\"\ entry\ selected-row'
        accom = re.compile(ref)
        plist = re.findall(accom,htmls)
        acma = re.match(r'</script></td></tr></thead><tbody><tr\ id=\"(.*?)\" class=\"\ entry\ selected-row',plist[0])
        acnumber = acma.group(1)
    except:
        print geneid[i]+" can't connect Uniprot in 30s, we will connect once again..."
        socket.setdefaulttimeout(30)
        try:  
            htmls = getHtml("http://www.uniprot.org/uniprot/?query=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22+"+geneid[i]+"&sort=score")  #联网搜ac号
            ref = r'</script></td></tr></thead><tbody><tr\ id=\".*?\" class=\"\ entry\ selected-row'
            accom = re.compile(ref)
            plist = re.findall(accom,htmls)
            acma = re.match(r'</script></td></tr></thead><tbody><tr\ id=\"(.*?)\" class=\"\ entry\ selected-row',plist[0])
            acnumber = acma.group(1)
            print "reconnection is seccessful!"
        except:
            print "can't connect the uniprot "+geneid[i]
            missac.append(geneid[i])                    #不能联网的保存到missac
            
    try:
        print "connecting the No."+str(i+1)+" gene "+geneid[i]+", please wait..."
        html = getHtml("http://www.uniprot.org/uniprot/"+acnumber)   #联网
        if len(html) < 1000:
            network = 'the network had been broken!'   ###断网的情况下才会发生，unipro的源代码不止1000.为什么不直接html == None？因为之前在学校断网自动跳到锐捷验证，有源代码<1000
    except:
        print geneid[i]+" can't connect web in 30s, we will connect once again..."
        socket.setdefaulttimeout(30)
        try:  
            html = getHtml("http://www.uniprot.org/uniprot/"+acnumber)
            print "reconnection is seccessful!"
        except:
            print "can't connect the web-"+geneid[i]
            missac.append(geneid[i])                    #不能联网的保存到missac
    try:
        print geneid[i]+" is matching..."
        ws.write(i+1,0,geneid[i])
        ws.write(i+1,1,''.join(gettitle(html).group(1)))#titlist里面有3个组，2,3组是想要的。
        ws.write(i+1,2,''.join(gettitle(html).group(2)))
        ws.write(i+1,3,''.join(getfunc(html).group(1)))   #匹配想要的文本
        ws.write(i+1,4,'; '.join(getgo(html)))
    except:
        print "can't match the web"+geneid[1]
    print "done"
w.save(outputfile)                #3、修改输出文件名，输出结果，能联网ID结果；

####为miss的ID再爬一次
geneid = missac
missac = []
z=Workbook()
zs = z.add_sheet('id')
ws.write(0,0,"GeneID")
ws.write(0,1,"GeneID_ac")
ws.write(0,2,"Protein Names")
ws.write(0,3,"function")
ws.write(0,4,"GO_annotation"+"_"+GOdatabase)
for i in range(len(geneid)):                        
    socket.setdefaulttimeout(30)
    htmls = getHtml("http://www.uniprot.org/uniprot/?query=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22+"+geneid[i]+"&sort=score")  #联网搜ac号
    ref = r'</script></td></tr></thead><tbody><tr\ id=\".*?\" class=\"\ entry\ selected-row'
    accom = re.compile(ref)
    plist = re.findall(accom,htmls)
    acma = re.match(r'</script></td></tr></thead><tbody><tr\ id=\"(.*?)\" class=\"\ entry\ selected-row',plist[0])
    acnumber = acma.group(1)
    try:
        print "connecting the No."+str(i+1)+" gene "+geneid[i]+", please wait..."
        html = getHtml("http://www.uniprot.org/uniprot/"+acnumber)   #联网
        if len(html) < 1000:
            network = 'the network had been broken!'
    except:
        print geneid[i]+" can't connect web in 30s, we will connect once again..."
        socket.setdefaulttimeout(30)
        try:       
            html = getHtml("http://www.uniprot.org/uniprot/"+acnumber)
            print "reconnection is seccessful!"
        except:
            print "can't connect the web-"+geneid[i]
            missac.append(geneid[i])                    #不能联网的保存到missac
    try:
        print geneid[i]+" is matching..."
        zs.write(i+1,0,geneid[i])
        zs.write(i+1,1,''.join(gettitle(html).group(1)))#titlist里面有3个组，2,3组是想要的。
        zs.write(i+1,2,''.join(gettitle(html).group(2)))
        zs.write(i+1,3,''.join(getfunc(html).group(1)))   #匹配想要的文本
        zs.write(i+1,4,''.join(getgo(html)))
    except:
        print "can't match "+geneid[i]
    print "done"
z.save(annot_com)           #4、修改重新检索文件名
with open(genemiss,'w') as f:  #5、修改无法检索文件名，输出连接不上的ac
    k = ' '.join(i for i in missac);
    f.write(k)
endtime = time.asctime(time.localtime(time.time()))
print "\n\n" + network + " The work has been finished.\nStart time: "+str(starttime)+";\nEnd time: "+str(endtime)+"." 



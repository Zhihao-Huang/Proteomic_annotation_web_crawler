#coding=utf-8
#################################################################################################################
#How it works：
#Import gene names by csv file, then search Uniprot database, matching accession ID and GO annotation, and finally output as xls file.
#6 parameters：
#1. workpath; 2. geneID csv file; 3. output result file; 4. output mismatch file; 5. choose a database.
#Note:
#1. all geneID in one column in csv file;
#2. there may be mismatch accessionID when using gene symbol ID for searching. the 2nd column of result file is geneID from database,
#   which is used for proofing ID matching.
#3. python2.7.
#4. model: pyExcelerator。
#Version: Web_Crawler20180316; select GO database.
#author：zhihao.jnu@gmail.com
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
os.chdir(workspace)
def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html

def gettitle(html):
    reg = r'<title>.*?</title>'
    titre = re.compile(reg)
    titl = re.findall(titre,html)
    titlist = re.match(r'<title>(.*?)\ -\ (.*?)\ -\ (.*?)</title>',titl[0])#matching again;
    
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

with open(inputfile) as a:  ##input csv file
    geneid = []
    for line in a.readlines():
        geneid.append(line.strip())
w=Workbook()
ws = w.add_sheet('id')
ws.write(0,0,"GeneID")        ##write 5 columns
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
            missac.append(geneid[i])                    #mismatch ID was stored in missac
            
    try:
        print "connecting the No."+str(i+1)+" gene "+geneid[i]+", please wait..."
        html = getHtml("http://www.uniprot.org/uniprot/"+acnumber)   #connecting
        if len(html) < 1000:
            network = 'the network had been broken!'   ###special case.unipro html contain mor than 1000 rows. 为什么不直接html == None？因为之前在学校断网自动跳到锐捷验证，有源代码<1000
    except:
        print geneid[i]+" can't connect web in 30s, we will connect once again..."
        socket.setdefaulttimeout(30)
        try:  
            html = getHtml("http://www.uniprot.org/uniprot/"+acnumber)
            print "reconnection is seccessful!"
        except:
            print "can't connect the web-"+geneid[i]
            missac.append(geneid[i])                    
    try:
        print geneid[i]+" is matching..."
        ws.write(i+1,0,geneid[i])
        ws.write(i+1,1,''.join(gettitle(html).group(1)))
        ws.write(i+1,2,''.join(gettitle(html).group(2)))
        ws.write(i+1,3,''.join(getfunc(html).group(1)))   
        ws.write(i+1,4,'; '.join(getgo(html)))
    except:
        print "can't match the web"+geneid[1]
    print "done"
w.save(outputfile)                #3. output file;

####running again for mismatch ID.
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
        html = getHtml("http://www.uniprot.org/uniprot/"+acnumber) 
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
            missac.append(geneid[i])                  
    try:
        print geneid[i]+" is matching..."
        zs.write(i+1,0,geneid[i])
        zs.write(i+1,1,''.join(gettitle(html).group(1)))
        zs.write(i+1,2,''.join(gettitle(html).group(2)))
        zs.write(i+1,3,''.join(getfunc(html).group(1))) 
        zs.write(i+1,4,''.join(getgo(html)))
    except:
        print "can't match "+geneid[i]
    print "done"
z.save(annot_com)         
with open(genemiss,'w') as f:  
    k = ' '.join(i for i in missac);
    f.write(k)
endtime = time.asctime(time.localtime(time.time()))
print "\n\n" + network + " The work has been finished.\nStart time: "+str(starttime)+";\nEnd time: "+str(endtime)+"." 



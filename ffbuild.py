# Python 3.7
# Encoding: UTF-8

JDK_PATH="C:/Program Files/Java/jdk1.8.0_202"

if __name__!="__main__":
    print("请通过命令行运行这个脚本。")
    exit(1)

import os
import shutil
import sys
from xml.dom.minidom import Document

if not os.path.exists(JDK_PATH):
    JDK_PATH=os.environ.get("programfiles")+"/Java"
    for item in os.listdir(JDK_PATH):
        if item[:3].lower()=="jdk":
            JDK_PATH=JDK_PATH+"/"+item
            break

font_package_name="FFCustom"
project_dir="FFCustom"
assets_path=project_dir+"/assets"

# ffconfig 字体名 {字体替换组}
if len(sys.argv)<=1:
    print("命令行：ffbuild.py <字体名> <字体文件1> <替换文件1> [<字体文件2> <替换文件2>…]")
    print("字体文件：指要显示的字体的所需文件。")
    print("替换文件：指系统中原来存在的文件，比如DroidSans.ttf，DroidSans-Bold.ttf，DroidSansFallback.ttf等。")
    print("\n使用方法：\n 1.先用本程序配置工程，\n 2.然后将本工程用AndroidStudio打开并构建生成字体包，\n 3.将生成的APK安装至手机，")
    print(" 4.在手机上下载“爱字体”点击“我的安装”找到生成的字体后选择“应用”，\n 5.在系统设置里选择由“爱字体”生成的字体。（即后面带有(iFont)字样的字体）")
    exit(1)

def copy_font(font_file):
    to_path=assets_path+"/fonts/"+get_file_name(font_file)
    if not os.path.exists(to_path):
        shutil.copyfile(font_file,to_path)
        print("复制 "+font_file+" 到 "+to_path)
    else:
        print(to_path+" 已经存在。")

def clear_dir(path):
    for item in os.listdir(path):
        if os.path.isfile(path+"/"+item):
            os.remove(path+"/"+item)

def get_file_name(path):
    slash_i=path.rfind("/")
    if slash_i==-1:
        slash_i=path.rfind("\\")
    if slash_i==-1:
        return path
    return path[slash_i+1:]

class FontXML:
    document=None
    xf=None
    tagSans=None
    
    def __init__(self):
        self.document=Document()
        self.xf=self.document.createElement("font")
        self.document.appendChild(self.xf)
        self.tagSans=self.document.createElement("sans")
        self.xf.appendChild(self.tagSans)

    def setDisplayName(self,name):
        self.xf.setAttribute("displayname",name)

    def addFont(self,replacing_font,existing_font):
        copy_font(replacing_font)
        tagFile=self.document.createElement("file")
        tagFilename=self.document.createElement("filename")
        tagFilename.appendChild(self.document.createTextNode(get_file_name(replacing_font)))
        tagDroidname=self.document.createElement("droidname")
        tagDroidname.appendChild(self.document.createTextNode(existing_font))
        tagFile.appendChild(tagFilename)
        tagFile.appendChild(tagDroidname)
        self.tagSans.appendChild(tagFile)

    def saveToFile(self,path):
        f=open(path,mode="wb")
        f.write(self.document.toprettyxml(indent="    ",encoding="utf-8"))
        f.close()
        print("保存至 "+path)
        
font_xml=FontXML()
font_xml.setDisplayName(sys.argv[1])
print("配置 \"%s\"…"%(sys.argv[1]))
clear_dir(assets_path+"/fonts")
clear_dir(assets_path+"/xml")
xml_name=""
for i in range(2,len(sys.argv),2):
    if i+1<len(sys.argv):
        if sys.argv[i][-4:].lower()==".otf":
            sys.argv[i]+=".ttf"
        font_xml.addFont(sys.argv[i],sys.argv[i+1])
        if sys.argv[i+1].lower()=="droidsans.ttf":
            xml_name=sys.argv[i][:sys.argv[i].rfind(".")]

if xml_name=="":
    print("未指定 DroidSans.ttf 的替换字体。")
    exit(1)
font_xml.saveToFile(assets_path+"/xml/"+xml_name+".xml")

def save_string_app_name(app_name):
    document=Document()
    string_node=document.createElement("string")
    string_node.setAttribute("name","app_name")
    string_node.appendChild(document.createTextNode(app_name))
    root_node=document.createElement("resources")
    root_node.appendChild(string_node)
    document.appendChild(root_node)
    f=open(project_dir+"/res/values/strings.xml",mode="wb")
    f.write(document.toprettyxml(indent="    ",encoding="utf-8"))
    f.close()
    print("APP_NAME 设置为 \""+app_name+"\"")

def sign_apk(apk_path,signed_apk_path):
    jarsigner="\""+JDK_PATH+"/bin/jarsigner.exe\""
    f=open("ffkskey.txt",mode="w")
    f.write("ffkeys")
    f.close()
    result=os.system(jarsigner+" -keystore ffks.jks -storepass ffcustom -signedjar "+signed_apk_path+" "+apk_path+" cert<ffkskey.txt")
    os.remove("ffkskey.txt")
    return result

save_string_app_name(sys.argv[1])
out_path=sys.argv[1]+".apk"
sign_path=sys.argv[1]+"_signed.apk"
if os.system("java -jar apktool.jar b -o"+out_path+" "+project_dir):
    print("执行 apktool 出错，请检查是否已正确安装 Java 以及命令行是否正确。")
else:
    if sign_apk(out_path,sign_path):
        print("执行 jarsigner 失败，你可能没有正确安装 JDK 或密钥输入错误。")
    else:
        print("生成成功，文件已输出至："+sign_path)

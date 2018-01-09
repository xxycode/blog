#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import datetime
import json
import markdown
import sys
import shutil
reload(sys)
sys.setdefaultencoding('utf8')

#格式化时间戳
def TimeStampToTime(timestamp):
	timeStruct = time.localtime(timestamp)
	return time.strftime('%Y-%m-%d',timeStruct)

#获取文章创建时间
def getArticleCreateTime(filePath):
	filePath = unicode(filePath,'utf8')
	t = getArticleDate(filePath)
	return TimeStampToTime(t)

#展示时间
def getArticleDisplayTime(filePath):
	filePath = unicode(filePath,'utf8')
	t = getArticleDate(filePath)
	timeStruct = time.localtime(t)
	return time.strftime('%b %d, %Y',timeStruct)

#获取配置项
def getConfig(key):
	configFilePath = 'config.json'
	configFile = open(configFilePath,'r')
	configDict = json.load(configFile)
	configValue = configDict[key]
	return configValue

#获取主题路径
def getThemePath():
	theme = getConfig('theme')
	if theme is None:
		theme = 'default'
	themePath = 'themes' + '/' + theme + '/'
	return themePath

#拷贝主题目录下面的css js images
def copyThemeFiles():
	themePath = getThemePath()
	publicPath = 'public/'
	cssPath = publicPath + 'css'
	jsPath = publicPath + 'js'
	imagesPath = publicPath + 'images'
	fontPath = publicPath + 'font'
	
	tCssPath = themePath + 'css'
	tJsPath = themePath +'js'
	tImagePath = themePath + 'images'
	tFontPath = themePath + 'font'

	if os.path.exists(cssPath):
		shutil.rmtree(cssPath)
	if os.path.exists(jsPath):
		shutil.rmtree(jsPath)
	if os.path.exists(imagesPath):
		shutil.rmtree(imagesPath)
	if os.path.exists(fontPath):
		shutil.rmtree(fontPath)

	shutil.copytree(tCssPath, cssPath)
	shutil.copytree(tJsPath, jsPath)
	shutil.copytree(tImagePath, imagesPath)
	shutil.copytree(tFontPath, fontPath)


#根据模板文件生成html
def generalArticleHtml(content,title = '',cTime = '',nLink = '',pLink = ''):

	htmlStr = md2html(content)
	themePath = getThemePath()
	articleTemplatePath = themePath + 'post.xt'
	template = open(articleTemplatePath,'r')
	templateContent = ''
	for line in template:
		templateContent = templateContent + line
	template.close()
	htmlContent = templateContent.replace(str("{content}"),str(htmlStr))
	htmlContent = htmlContent.replace(str("{title}"),str(title))
	htmlContent = htmlContent.replace(str("{cTime}"),str(cTime))
	
	return htmlContent

#md转html
def md2html(mdStr):
	exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
	ret = markdown.markdown(mdStr,extensions=exts)
	return ret

#排序函数
def compare(x,y):
	xTime = getArticleDate(x)
	yTime = getArticleDate(y)
	return yTime - xTime

#获取文章日期
def getArticleDate(article):
	aTime = int(getFileLine(article,1).replace('date:',''))
	return aTime

#获取文章标题
def getArticleTitle(article):
	return getFileLine(article,0).replace('title:','')

#获取文件的指定行数
def getFileLine(path,line):
	file = open(path,'r')
	lines = file.readlines()
	if line >= len(lines):
		return ''
	file.close()
	return lines[line]

#生成文章详情页
def generalPosts(articles):
	articles.sort(cmp = compare)
	for article in articles:
		createTime = getArticleCreateTime(article)
		timeInfos = createTime.split('-')
		

		articlePathInfo = article.split('/')
		articleFileInfo = articlePathInfo[1].split('.')
		articleFileName = articleFileInfo[0]


		publicPath = 'public'
		articlePath = publicPath + '/' + timeInfos[0] + '/' + timeInfos[1] + '/' + timeInfos[2] + '/' + articleFileName
		#没有当天的目录就创建一个
		if not os.path.exists(articlePath):
			os.makedirs(articlePath)

		articleTitle = getArticleTitle(article)
		articleFile = open(article,'r')
		articleContent = ''
		i = 0
		for line in articleFile:
			if i >= 2:
				articleContent = articleContent + line
			i = i + 1
		articleFile.close()

		htmlContent = generalArticleHtml(articleContent,articleTitle,getArticleDisplayTime(article))
		htmlPath = articlePath + '/index.html'
		if os.path.exists(htmlPath):
			os.remove(htmlPath)
		htmlFile = open(htmlPath,'w')
		htmlFile.write(htmlContent)
		htmlFile.close()
		
		print('根据'+ article + '，生成：' + htmlPath)

#更新博客
def updateBlog():
	print('正在更新博客...')
	print('拷贝资源文件...')
	copyThemeFiles()
	print('更新html文件...')
	articlePath = 'md_files' #文章目录
	articles = os.listdir(articlePath) #得到文件夹下面的所有文件名称
	s = []
	for article in articles:
		if not os.path.isdir(article):
			str = articlePath + '/' + article
			s.append(str)
	generalPosts(s)
	print('更新完成...')

#写新文章
def newBlog():
	articlePath = 'md_files'
	print('md文件目录：/' + articlePath)
	fileName = raw_input('请输入文件名：')
	title = raw_input('请输入文章标题：')
	if title == '':
		title = fileName
	createTime = int(time.time())
	filePath = articlePath + '/' + fileName + '.md'
	if os.path.exists(filePath):
		replace = raw_input('文件已存在，是否覆盖(y/n)')
		if replace == 'y':
			os.remove(filePath)
		else:
			filePath = articlePath + '/' + fileName + '_1.md'
	mdFile = open(filePath,'w')
	mdFile.write('title:' + title + '\n')
	mdFile.write('date:' + str(createTime) + '\n')
	mdFile.close()
	print('md文件创建完成：'+filePath)

#主函数
def main():
	argv = sys.argv
	if len(argv) < 2:
		print('没有参数哦，用法如下：\n    new/n:创建新博客\n    update/up:更新站点')
		return
	cmd = sys.argv[1]
	if cmd == 'new' or cmd == 'n':
		newBlog()
	elif cmd == 'update' or cmd == 'up':
		updateBlog()

main()

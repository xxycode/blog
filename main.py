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


# 格式化时间戳
def time_stamp_to_time(timestamp):
    time_str = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d', time_str)


# 获取文章创建时间
def get_article_create_time(file_path):
    file_path = unicode(file_path, 'utf8')
    t = get_article_date(file_path)
    return time_stamp_to_time(t)


# 展示时间
def get_article_display_time(file_path):
    file_path = unicode(file_path, 'utf8')
    t = get_article_date(file_path)
    time_str = time.localtime(t)
    return time.strftime('%b %d, %Y', time_str)


# 获取配置项
def get_config(key):
    config_file_path = 'config.json'
    config_file = open(config_file_path, 'r')
    config_dict = json.load(config_file)
    config_value = config_dict[key]
    return config_value


# 获取主题路径
def get_theme_path():
    theme = get_config('theme')
    if theme is None:
        theme = 'default'
    theme_path = 'themes' + '/' + theme + '/'
    return theme_path


# 拷贝主题目录下面的css js images
def copy_theme_files():
    theme_path = get_theme_path()
    public_path = 'public/'
    css_path = public_path + 'css'
    js_path = public_path + 'js'
    images_path = public_path + 'images'
    font_path = public_path + 'font'

    t_css_path = theme_path + 'css'
    t_js_path = theme_path + 'js'
    t_image_path = theme_path + 'images'
    t_font_path = theme_path + 'font'

    if os.path.exists(css_path):
        shutil.rmtree(css_path)
    if os.path.exists(js_path):
        shutil.rmtree(js_path)
    if os.path.exists(images_path):
        shutil.rmtree(images_path)
    if os.path.exists(font_path):
        shutil.rmtree(font_path)

    shutil.copytree(t_css_path, css_path)
    shutil.copytree(t_js_path, js_path)
    shutil.copytree(t_image_path, images_path)
    shutil.copytree(t_font_path, font_path)


# 根据模板文件生成html
def general_article_html(content, title='', c_time='', n_link='', p_link=''):
    html_str = md2html(content)
    theme_path = get_theme_path()
    article_template_path = theme_path + 'post.xt'
    template = open(article_template_path, 'r')
    template_content = ''
    for line in template:
        template_content += line
    template.close()
    html_content = template_content.replace(str("{content}"), str(html_str))
    html_content = html_content.replace(str("{title}"), str(title))
    html_content = html_content.replace(str("{c_time}"), str(c_time))

    return html_content


# md转html
def md2html(mdStr):
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
            'markdown.extensions.toc']
    ret = markdown.markdown(mdStr, extensions=exts)
    return ret


# 排序函数
def compare(x, y):
    x_time = get_article_date(x)
    y_time = get_article_date(y)
    return y_time - x_time


# 获取文章日期
def get_article_date(article):
    aTime = int(get_file_line(article, 1).replace('date:', ''))
    return aTime


# 获取文章标题
def get_article_title(article):
    return get_file_line(article, 0).replace('title:', '')


# 获取文件的指定行数
def get_file_line(path, line):
    file = open(path, 'r')
    lines = file.readlines()
    if line >= len(lines):
        return ''
    file.close()
    return lines[line]


# 生成文章详情页
def general_posts(articles):
    articles.sort(cmp=compare)
    for article in articles:
        create_time = get_article_create_time(article)
        time_infos = create_time.split('-')

        article_path_info = article.split('/')
        article_file_info = article_path_info[1].split('.')
        article_fle_name = article_file_info[0]

        public_path = 'public'
        archive_path = '/' + time_infos[0] + '/' + time_infos[1] + '/' + time_infos[2] + '/' + article_fle_name
        article_path = public_path + '/' + time_infos[0] + '/' + time_infos[1] + '/' + time_infos[2] + '/' + article_fle_name
        # 没有当天的目录就创建一个
        if not os.path.exists(article_path):
            os.makedirs(article_path)

        article_title = get_article_title(article)
        article_file = open(article, 'r')
        article_content = ''
        i = 0
        for line in article_file:
            if i >= 2:
                article_content += line
            i += 1
        article_file.close()

        html_content = general_article_html(article_content, article_title, get_article_display_time(article))
        html_path = article_path + '/index.html'
        if os.path.exists(html_path):
            os.remove(html_path)
        html_file = open(html_path, 'w')
        html_file.write(html_content)
        html_file.close()

        print('根据' + article + '，生成：' + html_path)


# 更新博客
def update_blog():
    print('正在更新博客...')
    print('拷贝资源文件...')
    copy_theme_files()
    print('更新html文件...')
    article_path = 'md_files'  # 文章目录
    articles = os.listdir(article_path)  # 得到文件夹下面的所有文件名称
    s = []
    for article in articles:
        if not os.path.isdir(article):
            if article.endswith(".md"):
                str = article_path + '/' + article
                s.append(str)
    general_posts(s)
    print('更新完成...')


# 写新文章
def new_blog():
    article_path = 'md_files'
    print('md文件目录：/' + article_path)
    file_name = raw_input('请输入文件名：')
    title = raw_input('请输入文章标题：')
    if title == '':
        title = file_name
    create_time = int(time.time())
    file_path = article_path + '/' + file_name + '.md'
    if os.path.exists(file_path):
        replace = raw_input('文件已存在，是否覆盖(y/n)')
        if replace == 'y':
            os.remove(file_path)
        else:
            file_path = article_path + '/' + file_name + '_1.md'
    md_file = open(file_path, 'w')
    md_file.write('title:' + title + '\n')
    md_file.write('date:' + str(create_time) + '\n')
    md_file.close()
    print('md文件创建完成：' + file_path)


# 主函数
def main():
    argv = sys.argv
    if len(argv) < 2:
        print('没有参数哦，用法如下：\n    new/n:创建新博客\n    update/up:更新站点')
        return
    cmd = sys.argv[1]
    if cmd == 'new' or cmd == 'n':
        new_blog()
    elif cmd == 'update' or cmd == 'up':
        update_blog()


main()

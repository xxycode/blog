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


# 年
def get_article_year(file_path):
    file_path = unicode(file_path, 'utf8')
    t = get_article_date(file_path)
    time_str = time.localtime(t)
    return time.strftime('%Y', time_str)


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
def general_article_html(content, title='', c_time='', n_link='', p_link='', template='post'):
    html_str = md2html(content)
    template_content = get_template_content(template)
    html_content = template_content.replace(str("{content}"), str(html_str))
    html_content = html_content.replace(str("{title}"), str(title))
    html_content = html_content.replace(str("{c_time}"), str(c_time))
    host = get_config('host')
    html_content = html_content.replace(str("{host}"), str(host))
    page_nav = ''
    if p_link != '':
        pre_template = get_template_content('page_nav_pre')
        pre_html = pre_template.replace(str("{link}"), str(p_link))
        page_nav += pre_html
    if n_link != '':
        next_template = get_template_content('page_nav_next')
        next_html = next_template.replace(str("{link}"), str(n_link))
        page_nav += next_html
    html_content = html_content.replace(str("{page_nav}"), str(page_nav))
    return html_content


# 根据模板文件名获取模板内容
def get_template_content(file_name):
    theme_path = get_theme_path()
    file_path = theme_path + file_name + '.xt'
    template = open(file_path, 'r')
    template_content = ''
    for line in template:
        template_content += line
    template.close()
    return template_content


# md转html
def md2html(md_str):
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
            'markdown.extensions.toc']
    ret = markdown.markdown(md_str, extensions=exts)
    return ret


# 排序函数
def compare(x, y):
    x_time = get_article_date(x)
    y_time = get_article_date(y)
    return y_time - x_time


# 获取文章日期
def get_article_date(article):
    a_time = int(get_file_line(article, 1).replace('date:', ''))
    return a_time


# 获取文章标题
def get_article_title(article):
    return get_file_line(article, 0).replace('title:', '')


# 获取文件的指定行数
def get_file_line(path, line):
    m_file = open(path, 'r')
    lines = m_file.readlines()
    if line >= len(lines):
        return ''
    m_file.close()
    return lines[line]


# 创建一个目录，没有就创建，有就不做任何操作
def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


# 生成文章详情页
def general_posts(articles):
    articles.sort(cmp=compare)
    articles_list = []
    for article in articles:
        create_time = get_article_create_time(article)
        time_info_arr = create_time.split('-')
        article_path_info = article.split('/')
        article_file_info = article_path_info[1].split('.')
        article_file_name = article_file_info[0]
        public_path = 'public'
        archive_path = '/' + time_info_arr[0] + '/' + time_info_arr[1] + '/' + time_info_arr[2] + '/' + article_file_name
        article_path = public_path + '/' + time_info_arr[0] + '/' + time_info_arr[1] + '/' + time_info_arr[2] + '/' + article_file_name
        create_dir(article_path)
        article_title = get_article_title(article)
        article_file = open(article, 'r')
        article_content = ''
        i = 0
        for line in article_file:
            if i >= 2:
                article_content += line
            i += 1
        article_file.close()
        article_dic = {'content': article_content,
                       'title': article_title,
                       'time': get_article_display_time(article),
                       'year': get_article_year(article),
                       'link': archive_path,
                       'article_path': article_path
                       }
        articles_list.append(article_dic)
    for index, article_dic in enumerate(articles_list):
        article_content = article_dic['content']
        article_title = article_dic['title']
        display_time = article_dic['time']
        article_path = article_dic['article_path']
        n_link = ''
        p_link = ''
        if index > 0:
            p_link = articles_list[index - 1]['link']
        if index < len(articles_list) - 1:
            n_link = articles_list[index + 1]['link']
        html_content = general_article_html(article_content, article_title, display_time, n_link, p_link)
        html_path = article_path + '/index.html'
        if os.path.exists(html_path):
            os.remove(html_path)
        html_file = open(html_path, 'w')
        html_file.write(html_content)
        html_file.close()
        print('根据' + article + '，生成：' + html_path)
        general_home(article_dic, index, len(articles_list), article_dic['link'])
    general_archives(articles_list)
    general_about()


# 生成关于我也没
def general_about():
    about_path = 'public/about'
    md_file_path = 'md_files/about.md'
    create_dir(about_path)
    article_file = open(md_file_path, 'r')
    article_content = ''
    i = 0
    for line in article_file:
        if i >= 2:
            article_content += line
        i += 1
    article_file.close()
    html_content = general_article_html(article_content, '关于我', '', '', '')
    html_path = about_path + '/index.html'
    if os.path.exists(html_path):
        os.remove(html_path)
    html_file = open(html_path, 'w')
    html_file.write(html_content)
    html_file.close()


# 生成首页
def general_home(article_dic, index, count, link):
    n_link = ''
    p_link = ''
    article_path = 'public/page/' + str(index + 1)
    create_dir(article_path)
    if index == 0:
        article_path = 'public'
    if index > 0:
        p_link = '/page/' + str(index - 1)
        if index == 1:
            p_link = '/'
    if index < count - 1:
        n_link = '/page/' + str(index + 1 + 1)
    article_content = article_dic['content']
    article_title = article_dic['title']
    display_time = article_dic['time']
    html_content = general_article_html(article_content, article_title, display_time, n_link, p_link, 'index')
    html_content = html_content.replace(str('{link}'), str(link))
    html_path = article_path + '/index.html'
    if os.path.exists(html_path):
        os.remove(html_path)
    html_file = open(html_path, 'w')
    html_file.write(html_content)
    html_file.close()
    print('根据' + article_dic['article_path'] + '，生成：' + html_path)


# 生成archive页面
def general_archives(articles):
    print('开始生成archives...')
    max_count = int(get_config('archive_item_count'))
    current_count = 0
    total_count = 0
    ori_file_path = 'public/archives'
    archive_list_item_template = get_template_content('archive_list_item')
    archive_year_template = get_template_content('archive_year')
    archive_container_template = get_template_content('archive_container')
    archive_page_template = get_template_content('archives')
    current_year = articles[0]['year']
    container_str = ''
    for index, article_dic in enumerate(articles):
        year = article_dic['year']
        if year != current_year or current_count == 0:
            year_tmp = archive_year_template.replace(str('{year}'), str(year))
            container_str += year_tmp
            current_year = year
        list_item_tmp = archive_list_item_template.replace(str('{display_time}'), str(article_dic['time']))
        list_item_tmp = list_item_tmp.replace(str('{link}'), str(article_dic['link']))
        list_item_tmp = list_item_tmp.replace(str('{title}'), str(article_dic['title']))
        container_str += list_item_tmp
        total_count += 1
        current_count += 1
        if total_count % max_count == 0 or total_count == len(articles):
            current_count = 0
            current_page = int(total_count / max_count)
            next_link = '/archives/page/' + str(current_page + 1)
            if total_count == len(articles):
                current_page += 1
                next_link = ''
            pre_link = '/archives/page/' + str(current_page - 1)
            if current_page - 1 == 1:
                pre_link = '/archives/'
            current_file_path = ori_file_path + '/page/' + str(current_page)
            if current_page == 1:
                current_file_path = ori_file_path
                pre_link = ''
            page_nav = ''
            if pre_link != '':
                pre_template = get_template_content('page_nav_pre')
                pre_html = pre_template.replace(str("{link}"), str(pre_link))
                page_nav += pre_html
            if next_link != '':
                next_template = get_template_content('page_nav_next')
                next_html = next_template.replace(str("{link}"), str(next_link))
                page_nav += next_html
            create_dir(current_file_path)
            tmp_container = archive_container_template.replace(str("{container}"), str(container_str))
            tmp_archives = archive_page_template.replace(str("{archives}"), str(tmp_container))
            host = get_config('host')
            tmp_archives = tmp_archives.replace(str("{host}"), str(host))
            tmp_archives = tmp_archives.replace(str("{page_nav}"), str(page_nav))
            html_file_path = current_file_path + '/index.html'
            if os.path.exists(html_file_path):
                os.remove(html_file_path)
            html_file = open(html_file_path, 'w')
            html_file.write(tmp_archives)
            html_file.close()
            print('生成：'+html_file_path+' currentpage: '+str(current_page))
            container_str = ''


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
            if article.endswith(".md") and article != 'about.md':
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
    command = 'open ' + file_path
    os.system(command)
    print('md文件创建完成：' + file_path)


def start_http_server():
    command = 'cd Public'
    os.system(command)
    command = 'python -m SimpleHTTPServer'
    os.system(command)


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
    elif cmd == 'start' or cmd == 's':
        start_http_server()

main()

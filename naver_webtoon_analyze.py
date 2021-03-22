# 1) BeautifulSoup으로 기본적인 Parsing 시작
import requests
from bs4 import BeautifulSoup
import unicodedata

URL = 'https://comic.naver.com/webtoon/weekday.nhn'
html = requests.get(URL).text
soup = BeautifulSoup(html,'html.parser')

webtoons_per_day={} # 요일별 웹툰 리스트 
total_webtoon_num=0 # 총 웹툰 개수
#my webtoons dictionary. key is day. ex)'mon','tue'..
my_webtoons_dic={'mon':['소녀의 세계','유일무이 로맨스','칼가는 소녀','와이키키 뱀파이어','이중첩자'],'tue':['바른연애 길잡이','하루만 네가 되고 싶어','달콤살벌한 부부','집이 없어'],'wed':['복학왕','엔딩 후 서브남을 주웠다','노곤하개','남주의 첫날밤을 가져버렸다','닥터앤닥터 육아일기'],'thu':['독립일기','어차피 남편은!','성스러운 아이돌'],'fri':['재혼 황후','여성전용헬스장 진달래짐','피와 나비'],'sat':['힙한 남자','피라미드 게임','내게 필요한 NO맨스'],'sun':['이번 생도 잘 부탁해','결혼까지 망상했어!','곱게 키웠더니, 짐승']}
#내가 보는 웹툰 이름 서치를 쉽게 하기 위해 my_webtoons 딕셔너리 value들을 리스트로 바꿔주었다.
my_webtoons_list=[]
for i in range(7):
    for j in list(my_webtoons_dic.values())[i]:
        my_webtoons_list.append(j)
total_my_webtoon_num=0 # 내가 보는 웹툰 개수

#print(soup.prettify())

#make dictionary of webtoon titles with key 'day' {'mon':[],'tue':[],'wed':[],'thu':[],'fri':[],'sat':[],'sun':[]}
webtoon_list= soup.find_all('div',{'class':'col_inner'})
all_titles=[] #전체 작품 이름 저장. 
for w in webtoon_list:
    day=str(w.h4.get("class")[0]) #  day = 'mon' , day ='tue'....
    webtoons_per_day[day]=[] # 요일별로 웹툰들을 저장하기 위해 딕셔너리 value 타입을 리스트로 만든다. 
    webtoons_per_day_list = w.find_all('a',{'title'})
    for each_webtoon in webtoons_per_day_list:
        titlestr = each_webtoon.get("title")
        if(titlestr in all_titles): #두 번 이상 연재하는 작품들은 한 번만 저장.
            continue
        else:
            webtoons_per_day[day].append(titlestr)
            all_titles.append(titlestr)
    total_webtoon_num += len(webtoons_per_day[day])

print(webtoons_per_day)


# 2) selenium으로 webdriver 불러온 후 필요한 웹 페이지로 넘어가 정보 수집. 
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time

driver_path = '/Users/mac/Downloads/chromedriver'
driver = webdriver.Chrome(driver_path)
driver.get(URL)
driver.implicitly_wait(time_to_wait=5)

webtoon_genre={} #장르별로 웹툰 개수 저장
my_webtoon_genre={}#장르별로 내가 보는 웹툰 개수 저장
webtoon_artist=[] #작가님 닉네임 리스트로 저장 value type은 스트링
webtoon_score=[]
comment_dic={}
all_titles.clear()

for i in range(total_webtoon_num):
    #너무 빨리 넘어가면 html파일을 충분히 못불러와서 StaleElementReferenceException 가 생김. 방지하기 위해 implicitly_wait메소드 이용
    try:
        time.sleep(0.4)
        page_list=driver.find_elements_by_class_name('title') 
        page_list[i].click() #move to each webtoon page
        
        html = driver.page_source
        soup = BeautifulSoup(html,'html.parser')

        # 작품 이름 수집
        current_title = str(soup.find('div',{'class':'thumb'}).find('img').get('title'))
        if current_title in all_titles: #이미 있는 작품이면 넘어가기
            continue
        else:
            driver.implicitly_wait(time_to_wait=5)
            all_titles.append(current_title)
            # 작가님 닉네임 수집
            nickname = str(soup.find('span',{'class':'wrt_nm'}).text)
            webtoon_artist.append(nickname)
            # 작품 장르 수집
            genre = str(soup.find('span',{'class':'genre'}).text)
            if(webtoon_genre.get(genre.split(',')[1])==None):
                webtoon_genre[genre.split(',')[1]]=1
            else:
                webtoon_genre[genre.split(',')[1]]+=1
                # 현재 페이지의 웹툰이 내가 보는 웹툰인지 체크
                if(current_title in my_webtoons_list):
                    if(my_webtoon_genre.get(genre.split(',')[1])==None):
                        my_webtoon_genre[genre.split(',')[1]]=1
                    else:
                        my_webtoon_genre[genre.split(',')[1]]+=1

            #  작품 첫 페이지에 나오는 회차 별점 평균
            time.sleep(0.5)
            score=soup.find_all('strong') 
            start=9
            sum=0
            num=0
            while(score[start].text[0].isnumeric()):
                sum+=float(score[start].text)
                num+=1
                start+=1
            webtoon_score.append(round(sum/num,2))
            time.sleep(0.4)
   #############  가장 최신화 웹툰 댓글 첫번째 페이지 베댓 리스트로 저장###############
            episode = driver.find_elements_by_class_name('title')[0].text # 최신화 회차랑 제목 텍스트
            eplink = driver.find_elements_by_partial_link_text(episode)
            eplink[0].click()
            #만화가 있는 곳에서는 페이지 소스를 볼 수 없기 때문에 따로 댓글 있는 페이지 URL을 만든다. 
            cur_html = driver.current_url
            cur_page = cur_html[cur_html.find('?'):]
            comment_URL = 'https://comic.naver.com/comment/comment.nhn' + cur_page
            driver2 = webdriver.Chrome(driver_path)
            time.sleep(0.4)
            driver2.get(comment_URL)
            comment_list=[]
            #클린봇 해제
            while(True):
                try:
                    time.sleep(0.1)
                    driver2.find_element_by_class_name('u_cbox_cleanbot_setbutton').click()
                    time.sleep(0.1)
                    driver2.find_element_by_class_name('u_cbox_layer_cleanbot_checkbox').click()
                    time.sleep(0.1)
                    driver2.find_element_by_class_name('u_cbox_layer_cleanbot_extrabutton').click()
                    #comment list
                    time.sleep(0.5)
                    comments=driver2.find_elements_by_class_name('u_cbox_contents')
                    for k in range(len(comments)):
                        comment_list.append(str(comments[k].text))
                    driver2.close()
                    break
                except Exception as ex:
                    driver2.close()
                    print('driver 2 error',ex)
                    break 
            if(len(comment_list)<5):
                comment_list=['empty','empty','empty','empty','empty']
            comment_list=comment_list[:5]
            comment_dic[current_title]=comment_list
    except IndexError:
        driver.back()
        continue
    driver.back()
    
############ 크롤링 끝. 크롬 창 닫기 #######################
driver.close()
    
print(webtoon_genre)
print(my_webtoon_genre)
import matplotlib.pyplot as plt
#matplotlib는 기본 글꼴이 영문 글꼴이어서, 한글을 그래프에 표기하려고 하면 경고(warning)가 뜨고, 그래프에는 ▯라고 표시된다.
#이를 방지하기 위해 폰트 설정
plt.rc('font', family='NanumBarunGothic')
plt.rc('axes', unicode_minus=False)
wedgeprops={'width': 0.7, 'edgecolor': 'w', 'linewidth': 1}
# 전체 웹툰 장르 파이 그래프
plt.pie(list(webtoon_genre.values()),labels=list(webtoon_genre),autopct='%.1f%%',wedgeprops=wedgeprops)
plt.show()
# 내가 보는 웹툰 장르 파이 그래프
plt.pie(list(my_webtoon_genre.values()),labels=list(my_webtoon_genre),autopct='%.1f%%',wedgeprops=wedgeprops)
plt.show()

# 3) Pandas 라이브러리와 Numpy 라이브러리를 사용해 모은 데이터를 CSV 파일로 변환

import pandas as pd
import numpy as np
# 필요한 데이터들 
#all_titles
#webtoon_artist
#webtoon_score
#comment_dic
# 데이터프레임 형식으로 만들고 -> csv

df = pd.DataFrame(data=np.array([webtoon_artist,webtoon_score]),columns=all_titles,index=['artist','score'])
df2 = pd.DataFrame(comment_dic,index=['best_comment1','best_comment2','best_comment3','best_comment4','best_comment5'])
all_data=pd.concat([df,df2])
display(all_data)
all_data.to_csv('NaverWebtoonAnalyze.csv',mode='w',encoding='utf-8-sig')





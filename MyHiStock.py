from MyDataBase import MyDataBase
from bs4 import BeautifulSoup
import requests


class MyHiStock:

    def download(code, name):
        mydb = MyDataBase()
        if code is not None:
            url = f"https://histock.tw/stock/{code}/%E9%99%A4%E6%AC%8A%E9%99%A4%E6%81%AF"
            req = requests.get(url)
            html_content = req.content
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table', class_='tb-stock text-center tbBasic')
            # print(table)
            trs = table.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                if len(tds) > 6:
                    ymd = f"{tds[1].get_text()}/{tds[3].get_text()}"
                    value = tds[6].get_text()
                    mydb.insert_etfdiv_table(ymd, code, name, value)
                    print(f" {ymd} {code} {name} {value}")
               #  mydb.insert_etfdiv_table()
        """
              <table class="tb-stock text-center tbBasic"> 
            <tbody><tr><th class="w1 f13 w58">所屬年度</th><th class="w1 f13 w58">發放年度</th><th class="w1 f13 w58">除權日</th><th class="w1 f13 w58">除息日</th><th class="w1 f13 w58">除權息<br>前股價</th><th class="w1 f13 w58">股票股利</th><th class="w1 f13 w58">現金股利</th><th class="w1 f13 w58">EPS</th><th class="w1 f13 w58">配息率</th><th class="w1 f13 w58">現金<br>殖利率</th><th class="w1 f13 w58" style="display:none;">扣抵稅率</th><th class="w1 f13 w58">增資<br>配股率</th><th class="w1 f13 w58">增資<br>認購價</th></tr>
            <tr></tr><tr class="alt-row"><td class="date">2022</td><td class="date">2023</td><td></td><td class="b-b">12/18</td><td>32.21</td><td class="b-b">0</td><td>0.35</td><td class="b-b">-</td><td>-</td><td class="b-b">1.09%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr><td class="date">2022</td><td class="date">2023</td><td></td><td class="b-b">10/19</td><td>28.87</td><td class="b-b">0</td><td>0.21</td><td class="b-b">-</td><td>-</td><td class="b-b">0.73%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr class="alt-row"><td class="date">2022</td><td class="date">2023</td><td></td><td class="b-b">07/18</td><td>32.87</td><td class="b-b">0</td><td>0.25</td><td class="b-b">-</td><td>-</td><td class="b-b">0.76%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr><td class="date">2022</td><td class="date">2023</td><td></td><td class="b-b">04/21</td><td>33.42</td><td class="b-b">0</td><td>0.35</td><td class="b-b">-</td><td>-</td><td class="b-b">1.05%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr class="alt-row"><td class="date">2022</td><td class="date">2023</td><td></td><td class="b-b">01/30</td><td>33.8</td><td class="b-b">0</td><td>0.38</td><td class="b-b">-</td><td>-</td><td class="b-b">1.12%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr><td class="date">2021</td><td class="date">2022</td><td></td><td class="b-b">10/19</td><td>33.25</td><td class="b-b">0</td><td>0.35</td><td class="b-b">-</td><td>-</td><td class="b-b">1.05%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr class="alt-row"><td class="date">2021</td><td class="date">2022</td><td></td><td class="b-b">07/18</td><td>36.66</td><td class="b-b">0</td><td>0.3</td><td class="b-b">-</td><td>-</td><td class="b-b">0.82%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr><td class="date">2021</td><td class="date">2022</td><td></td><td class="b-b">04/20</td><td>37.34</td><td class="b-b">0</td><td>0.26</td><td class="b-b">-</td><td>-</td><td class="b-b">0.70%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr class="alt-row"><td class="date">2021</td><td class="date">2022</td><td></td><td class="b-b">01/18</td><td>41.43</td><td class="b-b">0</td><td>0.22</td><td class="b-b">-</td><td>-</td><td class="b-b">0.53%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr><td class="date">2020</td><td class="date">2021</td><td></td><td class="b-b">10/19</td><td>43</td><td class="b-b">0</td><td>0.22</td><td class="b-b">-</td><td>-</td><td class="b-b">0.51%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr class="alt-row"><td class="date">2020</td><td class="date">2021</td><td></td><td class="b-b">07/16</td><td>43.84</td><td class="b-b">0</td><td>0.24</td><td class="b-b">-</td><td>-</td><td class="b-b">0.55%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr><td class="date">2020</td><td class="date">2021</td><td></td><td class="b-b">04/20</td><td>42.14</td><td class="b-b">0</td><td>0.24</td><td class="b-b">-</td><td>-</td><td class="b-b">0.57%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr class="alt-row"><td class="date">2020</td><td class="date">2021</td><td></td><td class="b-b">01/19</td><td>45.59</td><td class="b-b">0</td><td>0.19</td><td class="b-b">-</td><td>-</td><td class="b-b">0.42%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr><tr><td class="date">2019</td><td class="date">2020</td><td></td><td class="b-b">10/21</td><td>49.18</td><td class="b-b">0</td><td>0.18</td><td class="b-b">-</td><td>-</td><td class="b-b">0.37%</td><td style="display:none;"></td><td class="b-b">0</td><td>0</td></tr>
        </tbody></table>  
        """

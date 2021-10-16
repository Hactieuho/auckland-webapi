import scrapy
import sys
import re   # Bộ phân tích cú pháp để loại bỏ các thẻ html
import json
import datetime       # Tính toán thời gian
from scrapy.http import FormRequest

#Cấu trúc chứa thông tin cần lấy về
class VictimItem():
    Location = ""
    AssessmentNumber = ""
    HRubbish  = ""
    HRecycling  = ""
    HComment  = ""
    HNext  = [[""]]
    CComment  = ""
    CNext  = ""
    
class AucklandSpider(scrapy.Spider):
    name = 'aucklandspider'
    
    #địa điểm cần lấy thông tin từ tham số dòng lệnh
    param_address=sys.argv[3][3::]
    param_location = param_address

    # Tạo url truy cập
    start_urls = [
                    'https://www.aucklandcouncil.govt.nz/_vti_bin/ACWeb/ACservices.svc/GetMatchingPropertyAddresses',
                    'https://www.aucklandcouncil.govt.nz/rubbish-recycling/rubbish-recycling-collections/Pages/collection-day-detail.aspx?an='
                 ]
        
    
    # --------------------------------------------------------------------------------------------
    """ 
        Liệu một chuỗi có phải là số nguyên không?
    """
    def isInt(a_str):
        try:
            x=int(a_str)
            return True
        except Exception as error:
            return False    
            
    # --------------------------------------------------------------------------------------------
    """ 
        Chuyển đổi dạng html thành văn bản thô text plain
        :param html:  Nội dung html cần chuyển đổi. Ví dụ '<div> abc <p> d </p> </div>'
        :return:      Văn bản dạng text plain. Ví dụ 'abc d'
    """
    def html2plain(html):
            tmp = re.sub(re.compile('<.*?>'), '', html)
            #tmp = tmp.replace('"', '')
            #tmp = tmp.replace('\'', '')
            return tmp

    #--------------------------------------------------------------------------------------------            
    """ 
        Chuyển đổi dạng văn bản thành thời gian theo khuôn dạng chuẩn
        :param weekday:  Text chứa ngày. Ví dụ 'Thursday 1 July' sẽ được qui đổi thành yyyymmdd là 20210701    
        :param tictac:   Text chứa thời điểm trong ngày. Ví dụ 'Put your bins out before 6am, or the night before' sẽ qui đổi thành  -->  hhmmss 060000
        :return:         mảng 2 phần từ cho biết thời điểm bắt đầu và kết thúc [from, to]. Ví dụ [ "202107101 000000", "202107101 055959" ]
    """
    def String2Date(weekday, tictac):
            # Lấy ngày hiện tại
            today = datetime.datetime.today()
                        
            #Ngày mục tiêu
            try:
                deadline = datetime.datetime.strptime(weekday + " " + today.strftime("%Y"), '%A %d %B %Y')
            except:
                deadline = datetime.datetime(2000, 1, 1)
            
            datefrom = deadline.strftime("%Y%m%d")   
            dateto = deadline.strftime("%Y%m%d")   
                
                
            #Giờ mục tiêu
            #   Put bins out the night before or before 7am.
            #   Put your bins out before 6am, or the night before
            if tictac.find("night before"):  
                #đêm tức là 23h30 ngày hôm trước
                #datefrom = (deadline - datetime.timedelta(days=1)).strftime("%Y%m%d") 
                #timefrom= "233000"
                #đêm tức là đúng ngày
                datefrom = deadline.strftime("%Y%m%d") 
                timefrom= "000000"
            else:       
                timefrom= "000000"

            # Tìm tới cụm từ thời gian    
            try:            
                hour = re.findall(r'before (\d+[a,p]m)', tictac) 
                # Qui đổi 6pm thành giờ hệ thống, rồi chuyển đổi theo format
                timeto = datetime.datetime.strptime(hour[0], '%I%p')
                # Giảm đi 1 giây cho xứng đang với từ before
                timeto = timeto - datetime.timedelta(seconds=1)
                timeto = timeto.strftime("%H%M%S")       
            except:
                timeto = "123456"                
                
            return {"detail":weekday, "from": datefrom + " " + timefrom, "to": dateto + " " + timeto}

        
    #-----------------------------------------------------------------------------
    #  VICTIM
    #        <div class="card-content m-b-2">
    #            <div class="card-header">
    #                <h3 class="card-title h2">Household collection</h3>
    #                <h4 class="h6"><span class="icon-rubbish"><span class="sr-only">Rubbish</span></span> Rubbish</h4>
    #                <p>There are no council-run rubbish collections in this area. This service is performed by independent waste operators. Check your bag or bin to see which operator makes your collections. </p>
    #                
    #                <h4 class="h6 m-t-1"><span class="icon-recycle"><span class="sr-only">Recycle</span></span> Recycling</h4>
    #                <p>Collection day: <strong>Friday, fortnightly</strong> except after a <a class="border-link" href="/rubbish-recycling/rubbish-recycling-collections/Pages/public-holiday-collections.aspx">public holiday</a>.</p>
    #                Put bins out the night before or before 7am.
    #                
    #            </div>
    #            <div id="ctl00_SPWebPartManager1_g_dfe289d2_6a8a_414d_a384_fc25a0db9a6d_ctl00_pnlHouseholdBlock" class="card-block">
	#					
    #                <h4 class="h6 m-t-1" style="margin-left: 10px;"><strong>Your next collection dates:</strong></h4>
    #                
    #                    <div class="links"><span class="m-r-1">Friday 9 July</span><span class="icon-recycle"><span class="sr-only">Recycle</span></span> </div>
    #                
    #                <div class="links"><a id="ctl00_SPWebPartManager1_g_dfe289d2_6a8a_414d_a384_fc25a0db9a6d_ctl00_lnkWhere" href="javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions(&quot;ctl00$SPWebPartManager1$g_dfe289d2_6a8a_414d_a384_fc25a0db9a6d$ctl00$lnkWhere&quot;, &quot;&quot;, true, &quot;&quot;, &quot;&quot;, false, true))"><span class="docs">Where you can put your rubbish and recycling for collection</span></a>  </div>
    #                <div class="links"><a id="ctl00_SPWebPartManager1_g_dfe289d2_6a8a_414d_a384_fc25a0db9a6d_ctl00_hlRecycle" href="/rubbish-recycling/bin-requests/Pages/what-put-your-recycling.aspx"><span class="docs">What you can put in your recycle bin</span></a></div>
    #                <div class="links"><a id="ctl00_SPWebPartManager1_g_dfe289d2_6a8a_414d_a384_fc25a0db9a6d_ctl00_hlRubbish" href="/rubbish-recycling/bin-requests/Pages/what-put-your-rubbish.aspx"><span class="docs">What you can put in your rubbish bin</span></a></div>              
    #            
	#				</div>
    #        </div>
    #--------------------------------------------------------------------------------------------            
    """ 
        Thực hiện crawl số liệu từ trang https://www.aucklandcouncil.govt.nz/rubbish-recycling/rubbish-recycling-collections/Pages/collection-day-detail.aspx?an=12342681539
        trong để lấy được ngày giờ đổ rác
        :param self: Tham số ngầm định
        :param response: Nội dung html thu thấp được cần phân tích
        :param location: Tên phố xá, gợi nhớ của assessment_number. Có thể để trống. Ví dụ 244 New Lync
        :param assessment_number: Bắt buộc phải có để crawl. Ví dụ 12342681539 hoặc 12340127437
    """    
    def crawl_rubblish_from_an(self, response, location, assessment_number):

        # tạo đối tượng chứa kết quả
        victim = VictimItem()

        # Tìm tới thẻ  <div class="card-content">. Sẽ có 2 thẻ này, tương ứng với 2 mục Household collection và Commercial collection
        count = 0
        victim.Location = location
        victim.AssessmentNumber = assessment_number

        for cardcontent in response.xpath('//div[has-class("card-content")]'):

            # Lấy danh sách các ngày được đổ rác tiếp theo, lấy ra các thẻ p
            collection = cardcontent.css('p')

            # Loại bỏ các thẻ html thì nội dung text chính là dữ liệu cần tìm            
            rubblish = AucklandSpider.html2plain(collection[0].get())
            recycling = AucklandSpider.html2plain(collection[1].get())
            next = cardcontent.css('span.m-r-1::text').getall()     # Lấy danh sách các ngày được đổ rác tiếp theo, chỉ lấy text trong thẻ span thuộc class m-r-1
            try:
                list = cardcontent.css('div.card-header ::text').extract()  # Lấy danh sách các dòng text
                comment = [k for k in list if 'Put' in k][-1]               # Dòng ghi chú là dòng cuối cùng có chứa chữ Put. Put bins out the night before or before 7am.
                comment = comment.replace("\r\n", '').strip()
            except:
                comment = ''

            # Biến đổi văn bàn thành dạng thời gian chuẩn tắc yyyymmdd hhmmss
            nexttime = []
            for nextinweek in next:
                nexttime.append(AucklandSpider.String2Date(nextinweek,comment))

            if (count == 0):
                victim.HRubbish = rubblish
                victim.HRecycling = recycling
                victim.HNext = nexttime 
                victim.HComment = comment
            if (count == 1):
                victim.CRubbish = rubblish
                victim.CRecycling = recycling
                victim.CNext = nexttime
                victim.CComment = comment
            count = count + 1           

        # Lưu lại vị trí
        print(json.dumps(victim.__dict__))

    #--------------------------------------------------------------------------------------------            
    """ 
        Thực hiện crawl số liệu từ trang https://www.aucklandcouncil.govt.nz/_vti_bin/ACWeb/ACservices.svc/GetMatchingPropertyAddresses
        để qui đổi từ địa chỉ thành số assesstment number
        :param self: Tham số ngầm định
        :param response: Nội dung html thu thấp được cần phân tích
        :return: Ghi đè số assessment number vào tham số param_location . Ví dụ 12342681539 hoặc 12340127437
    """    
    def crawl_an_from_address(self, response):
        # Dạng response
        # [{'ACRateAccountKey': '12340325328', 'Address': '1 Pohue Avenue, Huapai', 'Suggestion': '1 Pohue Avenue, Huapai'}]
        jsonresponse = json.loads(response.text)
        #print("---------------------------")
        #print(jsonresponse)
        #print("Size = " + str(len(jsonresponse)))
        #print("---------------------------")

        # Lấy kết quả đầu tiên. Dạng {'ACRateAccountKey': '12340325328', 'Address': '1 Pohue Avenue, Huapai', 'Suggestion': '1 Pohue Avenue, Huapai'}
        AucklandSpider.param_location =  "12340000000"            
        try:
            if len(jsonresponse) > 0:
                AucklandSpider.param_location =  jsonresponse[0]['ACRateAccountKey'] 
                AucklandSpider.param_address =  jsonresponse[0]['Address'] 
        except:
            AucklandSpider.param_location =  "12340000000"            
            AucklandSpider.param_address =  ""
        
        # Ghi kết quả ra file để đỡ mất công tìm kiếm lại
        try:
            f = open('./an.csv', 'a')
            f.write(AucklandSpider.param_address + "," + AucklandSpider.param_location + "\n")
            f.close()
        except:
            x=1
            
        #-------------Thực hiện crawl thông tin thùng rác------------------
        AucklandSpider.start_urls[1]=AucklandSpider.start_urls[1] + AucklandSpider.param_location  # Bổ sung mã an để có URL để truy cập vào trang 
        yield scrapy.Request(AucklandSpider.start_urls[1], 
                                callback=self.crawl_rubblish_from_an,       # Khai báo hàm callback phân tích html
                                cb_kwargs=dict(location=AucklandSpider.param_address, assessment_number = AucklandSpider.param_location),  # Truyền tham số vào hàm callback
                                dont_filter=True)
        return
        
    #----------------------------------------------------------------------------------
    """ 
        Hàm tổng quát thực hiện crawl, từ đó phân chia cho từng URL khác nhau.
    """    
    def start_requests(self):
        # Trường hợp thông tin địa chỉ là dạng số nguyên --> assessment number rồi --? thực hiện lấy thông tin đổ rác luôn
        if not AucklandSpider.isInt(AucklandSpider.param_location): 
            jsondata = json.dumps({
                                "ResultCount":"1",  #Số lượng gợi ý
                                "SearchText":AucklandSpider.param_location,     # Địa chỉ cần tìm
                                "RateKeyRequired":"false"}
                                  )
            #-------------Thực hiện crawl thông tin assessment number------------------
            yield scrapy.FormRequest(AucklandSpider.start_urls[0], 
                                    method='POST',
                                    body=jsondata,
                                    headers={
                                                    'Content-Type':'application/json;charset=utf-8',
                                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.59',
                                                    'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,fr;q=0.7',
                                                    'Accept': 'application/json, text/plain, */*'
                                            },
                                    callback=self.crawl_an_from_address       # Khai báo hàm callback phân tích html                                  
                            )
        else:    
            #-------------Thực hiện crawl thông tin thùng rác------------------
            AucklandSpider.start_urls[1]=AucklandSpider.start_urls[1] + AucklandSpider.param_location  # Bổ sung mã an để có URL để truy cập vào trang 
            yield scrapy.Request(AucklandSpider.start_urls[1], 
                                    callback=self.crawl_rubblish_from_an,       # Khai báo hàm callback phân tích html
                                    cb_kwargs=dict(location=AucklandSpider.param_address, assessment_number = AucklandSpider.param_location),  # Truyền tham số vào hàm callback
                                    dont_filter=True)
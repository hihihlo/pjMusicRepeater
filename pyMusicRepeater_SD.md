
# doc addr
mpv.io
    https://mpv.io/manual/master/
wx.lib.agw.ultimatelistctrl.UltimateListCtrl — wxPython Phoenix 4.2.1 documentation
    https://docs.wxpython.org/wx.lib.agw.ultimatelistctrl.UltimateListCtrl.html?highlight=insertcolumninfo#wx.lib.agw.ultimatelistctrl.UltimateListCtrl.SetUserLineHeight
RichTextCtrl
    wx.richtext.RichTextCtrl — wxPython Phoenix 4.2.1 documentation
        https://docs.wxpython.org/wx.richtext.RichTextCtrl.html#wx.richtext.RichTextCtrl
    Overview — wxPython Phoenix 4.2.1 documentation
        https://docs.wxpython.org/richtextctrl_overview.html    
            
# GUI layout
waveWide
waveNarr = snteLong
(SelRange)  //臨時性質, 只有一組, 加入 snteMini 後就清空
main snte       #有 SelRange 且 Select main snte row 時若 Enter : [add to subSnte]
    sub snte    #Select sub snte row 時出現 SelRange (可修改其範圍), 若 Enter : [update subSnte]

# keyboard
a       : pause/play
space   : select current snippet (and enter SelRange mode)
(hjkl = left down up right)
i = a-left  [speed]
o = a-right [speed]

//navigate_snte / snte_repeat_count / speed / adjust-position
up/dowon        : [snte] prev/next snte (if row is sub snte : enter SelRange mode)
a-up/a-down     : [snte] prev/next snte (skip sub snte)
(or PgUp/PgDn ?)

in SelRange mode : 
    PgUp            : active/inactive begin_point
    PgDn            : active/inactive end_point
    left/right      : [pos]   if active begin/end point : adjust_position
                      [count] dec/add repeat count    // (0/def), 1, 2, 3, ...
                      0   <- def -> 1
                      def <-  0  -> 1
                      -1  <-  N  -> +1
    a-left/a-right  : [speed] dec/add play speed of the snte
    Enter           : add SelRange to sub snte (or update modify), then exit SelRange mode (to continue play)
    Esc             : exit SelRange mode (to continue play)
    Del             : del SelRange (sub snte),  or disable main snte


# play plan setting
M* : play Main snte by setting count (count/speed=row setting)      //主句
S* : play Sub snte  by setting count (count/speed=row setting)      //子句
C* : play Copy-main-snte by setting count (count/speed=row setting) //複句
M1 : play Main snte once (count=1, speed=row setting)  //overwrite row count setting !
即 speed 皆取自 row setting, cnt 可能指定覆蓋 row setting

default :
    def Main_snte cnt      = 2, speed=100%
    def Sub_snte cnt       = 2, speed=50%
    def Copy_main_snte cnt = 1, speed=65%
    故 `M*S*C*M1` 可播放 常速主句2次 + 極慢速子句2次 + 複句(=稍慢速主句)1次 + 常速主句1次

menu item : 
    set all snte to current def setting (include Main_snte+Sub_snte+Copy_main_snte)
    set all Main_snte to current "def Main_snte" setting : cnt & speed
                                                           cnt
                                                           speed
    set all Sub_snte to current "def Sub_snte" setting   : cnt & speed
                                                           cnt
                                                           speed
    set all Copy_main_snte to current "def Copy_main_snte" setting : cnt & speed
                                                                     cnt
                                                                     speed
    
# envir

## intro / AD
- 可輸入 youtube 網址, 直接把線上影片的內容拿來複讀學習
  https://github.com/jaseg/python-mpv   如其前面部份 Usage 所示

## sale / shop / 第三方電子商務平台
//keyword : 第三方電子商務平台 銀行轉帳
//希望支援 : 信用卡刷卡, LINE Pay, Apple Pay, Android Pay, Google Pay, (虛擬帳號/Web ATM)
發票 ??  第三方支付平台可以提供完整的服務，從收款、開發票到提醒消費者付款等，都有人幫你處理好

電商平台是什麼？2024年6大電商平台比較！手把手教你如何選擇適合自己的網路開店平台！ ｜ ShopStore 電商教室
    https://shopstore.tw/article/268
    還將比較結果整理成 可下載的 excel 檔 ! 含支援的金流
    1. ShopStore 
        為原生台灣本土電商平台，主打網路開店輕鬆好上手、功能完整的購物網站，並且以台灣市場（[提供海外刷卡]）、零售商家為主。整體後台規劃操作上，以「簡單好上手」為主軸
        ShopStore 的開店方案總共有三種：
            新手開店－0 元／每月             抽成 5%
            小資開店－4,680元／每年  （主打）抽成 2%
            旗艦計畫－47,988 元／每年        不抽成
        Facebook／Google／LINE 登入, 電子發票自動開立, 線上退貨退款機制
        由 KOL／部落客幫您作網站推廣, 會詳細分明的列出，透過導購網址下單的訂單明細、傭金分潤
        ShopStore 提供的所有功能，只要方案為「小資開店」方案以上就都可以全功能使用，商店如需要使用獨立網域，ShopStore 都會免費協助店家設定與綁定，並免費申請 SSL 安全憑證，不須額外設定費！
        支援國內外金物流、支援各大超商取貨付款、完善的訂單及庫存系統、多元的優惠促銷搭配、分潤導購、外觀半自訂、不綁約
    2. Waca 
        為台灣原生的電商平台。Waca 主打「簡單開一間不簡單的店」，提供專屬的開店顧問、強調方案[不綁約]、全方案皆[不抽成]，部分功能與 Shopline 一樣採用模組加購的方式，且不限方案都可以加購    
        輕量版－599元／每月、專業版－2099元／每月、（主打）企業版－4099／每月、尊爵版－8099元／月
        如果店家有跨境電商的需求，Ｗaca 有提供多國貨幣的模組加購功能，以及多國語言（僅提供簡體、繁體、英文），而在跨境物流會需要商家另外找物流廠商做簽約合作
        如有需要綁定獨立網域的店家，Waca 會收取「SSL 安全憑證」的安裝費與設定費：個人憑證：7,000元／每年、商業憑證：12,000元／每年
        比較推薦對電商經營較有經驗的店家做使用，因功能強大、提供非常多元的變化、完善的數據分析報表與工具, 如果您是有經驗、有資金的商家，追求強大多元的功能，Waca 會是個不錯的選擇！
    

【2024電商金流懶人包】3分鐘一次搞懂！全通路整合多元支付，有效提升下單付款率 - CYBERBIZ 電商部落格
    https://www.cyberbiz.io/blog/2020%E9%9B%BB%E5%95%86%E9%87%91%E6%B5%81%E6%87%B6%E4%BA%BA%E5%8C%85-%E5%85%A8%E9%80%9A%E8%B7%AF%E6%95%B4%E5%90%88%E3%80%8C%E5%A4%9A%E5%85%83%E6%94%AF%E4%BB%98%E3%80%8D/

想當電商營運者，店主第一課：如何處理金流？|數位時代 BusinessNext
    https://www.bnext.com.tw/article/62785/e-commerce-payment-flow-may?

電商平台比較：哪一個網店平台最適合你開店創業？ - eCommerce 台灣 我們來2021檢查網路開店 （ecommerce）SEO!
    https://www.ecommercetw.com/%e9%9b%bb%e5%95%86%e5%b9%b3%e5%8f%b0/
    Shopify         [費用不是太便宜] 使用Shopify開店不需額外尋找網站託管商，更不用花費心力維護網路伺服器，因此我們能夠肯定地說，Shopify是我們最愛用的網路開店平台
        https://www.ecommercetw.com/mianfei/shopify-review-page
        有別於大部分其他平台提供免費的基本服務方案，Shopify只提供三款付費方案。然而他們的免費試用期長達90天
        Basic Shopify——每月29美元／約872新台幣／約225港元
    Webnode         [方案價格漂亮] 銷售工具雖然較少，卻是對新手最友善的平台, 號稱是網路上最簡單的架站平台 
        https://www.ecommercetw.com/mianfei/webnode
    Easy Store      不收手續費、維護費、設定費，也不抽成交佣金，[讓商家完全吸收利潤, 月費價格也很划算]; 網路平台號稱是「亞洲版的Shopify」
        https://www.ecommercetw.com/mianfei/easystore-hp
    Wix
    WooCommerce     最便宜, 必須自己從頭設定起。舉例來說，你可以找一個較便宜的[網站託管商]託管你的店家，先安裝WordPress，然後在你的WordPress上安裝WooCommerce，如此開店
    Weebly
    Shopline        以簡單使用著稱
    91App           以簡單使用著稱
    上述所有平台皆有中文介面，英文不好沒關係！

Microsoft 網上商店 / Microsoft市集 / (前身為 Windows市集)
    可在此購買所有Metro UI應用程式及、傳統應用程式、現代化應用程式
    早期策略錯誤，許多未轉成UWP的Win32應用程式和工具皆未收錄在Windows Store上，也讓用戶揚棄Windows Store App而改用第三方package manager，如 Chocolatey、Ninite、OneGet 等來協助 App 安裝
    新版Windows Store，最值得注意是透過和Amazon的合作，讓所有Amazon App Appstore上架的Android App或遊戲，都能在Windows Store搜尋到
    Windows App上架的App開發商可不使用微軟收費機制（Microsoft Commerce），而用第三方或自己的收費機制，如此一來可以保有在平臺上所有收入。(這項規定並不適用於遊戲類)

蝦皮 ?

Amazon

GPT : 
    Shopify：Shopify是一個功能強大的電子商務平台，提供簡單易用的網店建立工具、支付處理、訂單管理和報告等功能。
    WooCommerce：WooCommerce是一個基於WordPress的開源電子商務外掛，可以將電子商務功能整合到您的WordPress網站中。
    BigCommerce：BigCommerce是一個全功能的電子商務平台，提供了豐富的功能，包括網店建立、訂單管理、支付處理和行銷工具等。
    Magento：Magento是一個強大的開源電子商務平台，提供了豐富的功能和定製選項，適用於中大型企業。
    Square Online：Square Online是由Square提供的電子商務平台，可以輕鬆建立在線商店，並整合Square的支付處理解決方案。
    考慮到您是一個獨立開發者，希望維護成本低的情況，以下是一些相對適合的選擇：
        Shopify：Shopify提供了一個簡單易用的平台，您可以在其上建立您的網店。它有許多現成的主題和外掛，可以快速搭建您的網店，而且它的維護和更新都由Shopify團隊負責，您不需要花太多時間和精力在這方面。
        WooCommerce：WooCommerce是一個基於WordPress的開源電子商務外掛，如果您已經熟悉WordPress，那麼使用WooCommerce可能會更加方便。它的基本功能是免費的，而且有許多免費或付費的外掛可供擴展功能。
        Square Online：Square Online提供了一個簡單的方式來建立在線商店，它的介面設計直觀，功能也相對簡單。[Square的支付處理解決方案與其網店平台整合得很好]，這可以簡化您的支付處理流程。
        這些平台都提供了簡單易用的介面和管理工具，而且您也不需要擔心伺服器管理、安全更新等問題，因為這些都由平台供應商處理。這樣您就可以專注於開發您的軟體，而不必花費太多時間在網站維護上。

別讓你的程式碼在 Github 上自生自滅，把它丟上來這賣吧 | TechOrange 科技報橘
    https://buzzorange.com/techorange/2014/03/26/binpress/
    不同於 Kickstarter 上的「產品」, Binpress 就是把程式碼這樣「內容產品」交易化的平台
    你可以把它看成商業版本的 Github，或者開源項目的 Amazon; ... 它有三種交易模式：
        - 用戶可以直接一次性購買這些開源項目的商業許可，然後使用，價格由開發者自己定義，根據複雜程度，從幾十到上千美元不等
        - 也可以進行訂閱（Subscribe），這樣就可以持續得到開發者的質量維護和更新；
        - 而如果用戶的需求比較複雜，還可以進行個性化定制，比如買一個能滿足 30% 需求的開源程式碼庫，然後聯繫這個作者，讓他進行剩餘功能的定制。
    要達到讓人付費的標準，Binpress 上的項目至少要符合三點：合法、高質量、有問題開發者可以保證技術支持。
    他們會聘請律師來保證這些項目的商業許可不衝突；同時他們自己團隊會對每一個庫都進行人工審核，來驗證代碼的質量；
    另外，更關鍵的是，他們支持 14 天的退款保證 —— 這樣可以讓不少客戶打消疑慮    
    Binpress 現在對每筆交易收取 20%-30% 的平台費用
    
### misc
Shopify與自架網站大比拚 該如何選擇？ – 杜吉 Duki
    https://dukiapp.com/shopify-vs-own-website-advantages/
    
2023 Shopify 台灣案例 介紹 - 內含判斷 Shopify 網站工具 – AkoCommerce
    https://akocommerce.com/blogs/shopify-success-stories/shopify-taiwan-cases-2023
    偵測網站是否使用 Shopify 建置, 可使用以下 browser plugin  :     
        工具一：Wappalyzer
        Wappalyzer 可以讓你輕易地安裝在瀏覽器中，可以快速又簡單的判別出電子商務使用到什麼樣的系統。
        除了電商外，甚至還可以看到一些底層技術或串接額外的工具，雖然不是 100% 正確，但對於快速的參考來說是非常方便的！
        工具二：Koala Inspector
        
KT 選讀 #5. 平台如何協助軟體與硬體公司銷售產品 | by KT Huang | Medium
    https://medium.com/@kthuang/kt-%E9%81%B8%E8%AE%80-no-5-f7dea33765fb 
    
其實更容易的方式是針對企業開發，開發他們缺少的功能和工具，企業更加願意為軟體付款，而且價格也會比個人高很多

Windows 下開發的軟體如何收費？ - 知乎.mhtml
    很簡單，到微軟store上發佈一個demo版（限制高級功能）。
    再把升級系統做好，並且在升級介面中提供一個二維碼支付，收到款後才給與升級。
    升級更新（開放高級功能）成功後，開始計時，開放高級功能。
    計時功能，用於檢測年費是否到期，需要組態一個雲伺服器用於聯網校驗使用者資料，包括帳號資訊（區別使用者）、付費記錄（付費計時）、和當前硬體ID（繫結電腦主機）。
    軟體一定要設計成必須聯網才能運行。
    每次軟體啟動，都需要聯網校驗，如果聯網不成功，給出提示，並鎖死高級功能。
    校驗資料一定要加密！加密！加密！
    一年滿後，軟體檢測到付費過期，就提示繼續付費，並自動降為demo版。

    找個軟體銷售平台，[數位荔枝][少數派][軟購商城]之類的，賣註冊碼
    
    建議使用[淘寶]購買，以訂單號和電話號碼做為啟動碼
        
## serial protect / 防止盜版
可能使用的序號 : 
    MAC, 當下時間, UUID : 其它資訊可整個複製至他台電腦執行, 硬體資訊如 MAC 較不易有此缺點
    須能由 user 電腦中取得, 或須自行保管好

python查詢電腦序列號 CPU、主機板、硬碟、MAC、BIOS_python獲取cpu型號-CSDN部落格
    https://blog.csdn.net/lekmoon/article/details/111478394

python讀取電腦產品碼_海風HiFine的技術部落格
    https://blog.51cto.com/HiFine/7496847
    讀取電腦硬體資訊 / 加密解密演算法 / 含判斷到期日

軟體保護 - 銓安智慧科技 (IKV-Tech)
    https://ikv-tech.com/zh/2020-09-08-06-53-32/2020-09-08-07-28-25.html
    您可以依據安全要求及成本考量選擇
        軟體模式：成本最低，但是仍能鎖定安裝的電腦，複製無效
        智慧卡模式：成本較高，需搭配讀卡機，是目前 IT 領域最強的認證機制
        USB金鑰模式：成本適中，安全等級可以客戶使用情境調整
    硬體環境鑑識技術
        防堵應用環境非法複製，ACP 具有辨識安裝環境硬體特徵的能力，所有加密機制的金鑰，均以安裝環境特有的硬體訊息計算產生，任何非法複製均很難成功，[即使使用對應複製硬碟，都無法達成非法複製]。    
    
產品金鑰 - 維基百科，自由的百科全書
    https://zh.wikipedia.org/zh-tw/%E4%BA%A7%E5%93%81%E5%AF%86%E9%92%A5
    產品金鑰，常稱為序列號或金鑰，是一種製造商用來保護著作權的防盜版措施。
    例如Microsoft Windows等的一些商業軟體需要[經過製造商的網路驗證，防止使用者以同一組產品金鑰啟用多套軟體]

如何把資料做成只有授權的電腦才能讀取? - iT 邦幫忙::一起幫忙解決難題，拯救 IT 人的一天
    https://ithelp.ithome.com.tw/questions/10044478
    - PKI (Pulic Key Infrastructure)
    - 去找 SSL 這是個 open source library
    - 讀取電腦硬體的序號當唯一識別碼(ex MAC)，產生一組數值A1給軟體公司，軟體公司會根據你給他的數值A1產生另外一組數值B1
      軟體在啟動時會讀取硬體序號及已經存入的B1決定要不要給予使用， (must match 硬體序號 A1 <-> 軟體公司提供的 B1)
      換了電腦 A1 會改變，所以在甲電腦的授權 B1，在乙電腦無法使用
    
[設計案例] "授權碼" 如何實作? #3, 數位簽章 — 安德魯的部落格
https://columns.chicken-house.net/2016/02/24/casestudy_license_03_digital_signature/
[設計案例] “授權碼” 如何實作? #3 (補) - 金鑰的保護 — 安德魯的部落格
    https://columns.chicken-house.net/2016/03/19/casestudy_license_03_appendix_key_management/

加密護盾：保護你的Python .exe程序免受反編譯的利器 - 掘金
    https://juejin.cn/post/7350520171612209203
    Python 在打包或最佳化運行速度時會生成.pyc檔案，這些.pyc檔案可以被簡單地反編譯為.py檔案
    由C語言編譯生成的機器碼更難以反編譯。目前還沒有一種直接將機器碼轉換回 Python 程式碼的方法。因此，我們可以利用這一點來加密我們的程式碼。
    使用Cython配合加密打包程序 : Cython 是一個編譯器，可以將 Cython 原始碼轉換為高效的C或C++原始碼。然後，我們可以將這些原始碼編譯 為Python 擴展模組或獨立的可執行檔案。
            
## library/install
Windows 下製作可攜式 Python 的方法 - DEV Community
    https://dev.to/codemee/windows-xia-zhi-zuo-ke-xi-shi-python-de-fang-fa-1m05
    從 Python 3.5 開始, 官方提供有 Windows 下的 embeddable package 版本, 這是為了讓你可以將 Python 內嵌在自己的應用程式而特別設計的最精簡版本 Python 執行環境, 原本的用途是讓你：
        - 幫應用程式加上腳本功能, 可以讓使用者用 Python 撰寫你自己應用程式的腳本。
        - 讓你用 Python 寫的程式可以成為單獨的應用程式, 不需要使用者自己安裝 Python 環境。
        這也表示我們可以使用這個版本製作一個獨立可攜的 Python 執行環境, 有點像是虛擬環境, 但是更獨立可攜
    要安裝 pip 工具, 只要下載對應版本的 get-pip.py 檔案後執行即可, 如果...    
    因為它會去執行原本記錄路徑的 Python。你可以改用以下方式執行 pip, 不要直接執行 scripts 下的可執行檔：./python -m pip list
    如果你還是比較喜歡執行可執行檔, 也可以強制 pip 重新安裝：./python -m pip install --upgrade --force-reinstall pip
        這樣它就會更新那些執行檔, 記錄目前使用的 Python 路徑了
    補充:另一種可攜式 Python 環境的選擇是使用 WinPython
        
## library License
python-mpv inherits the underlying libmpv's license, which can be either GPLv2 or later (default) or LGPLv2.1 or later. For details, see the mpv copyright page.
    https://github.com/mpv-player/mpv/blob/master/Copyright
python-mpv 繼承了底層 libmpv 的許可證，可以是 GPLv2 或更高版本（預設），也可以是 LGPLv2.1 或更高版本。詳情請參閱mpv版權頁。
  
# TODO
- Playback mode during note editing (F2) : loop / auto pause
    - GUI 上動態改變/標示 play mode, ex: 平時4種, editing 時2種且標示"editing"
- 應將 plan 放進 GUI & yaml, 目前暫使用 `_addPlan` 
  故依目前設定, 僅有主句, disable 子句/副句 時, 會播放 *主句次數 + 1* 次;  因未看到 GUI 設定, 容易以為是 bug !
- edit 原文/譯文 (F3)
- 增加效能 : 減少不必要的 `_updMapping`
- AB point mark text
- AB point can use drag
- file open
    - recent files
    - open next file (同目錄, 字串排序後的下個檔名)
- 調整(微調)字幕時間對應
- 分詞/方便產生 srt
- loadfile 可指定字幕檔, 或使用 `player.sub_add('test.srt')`
- 自動記錄產生過的 .MusRep (或目錄), 允許從中篩選出 playCnt >= N 的 snte (即時蒐集、產生 play list)
    - 若記錄檔遺失, 或重灌作業系統前未備份, 可自動使用 everything 取得 `*.MusRep`

- stop_on_end 的可能改善方式
    - 每次播完後會自動停止 (idle_active=1, time_pos=None), 須再次 play or loadfile, 大檔或許會影響效能
    - 繼承 MPV, 改寫 `__init__`, 於其中增加必須在初始化時做的設定
    - 使用 mpv.conf
    - 改用 playlist(即使只播放一個檔案), 並自動增加一個 silence vox file, 當被跳到該檔時就移回 file 0, 就不必 reload file 了

## idea
- 點選單字、輸入單字後, 使用 真人發音網站 播放 or 下載
- 輸入 youtube 網址, 可下載影片 (不確定是否合法 !)  mpv 文件也提到不少 youtube-dl !
    - [[#Youtube download]]
- 輸入 youtube 網址, 不下載影片, 但能記錄、儲存 播放範圍、速度, (無下載, 故無波形圖 !)

## DICT query/download
QryDict_to_Anki.py :   C:\DriveD\MyPro\DataProc\Parser_Script\Python\NET\+download\爬蟲_crawl\CAI\QryDict_to_Anki.py

讀取英文單字後由線上字典網站讀取資料，並解析內容萃取資訊，再產生成Markdown文字，再下載語音檔到本地
    https://gist.github.com/emisjerry/64d5f4deea7cc20145ae6c4b4f7783ed
    translate.ahk
    語音檔：https://s.yimg.com/bg/dict/dreye/live/f/xxx.mp3

如何用Python下載線上字典上的單詞或者短語mp3_mp3詞典資料下載
    https://blog.csdn.net/henanlion/article/details/126277738
    爬取有道詞典上的單詞音標、詞義、發音mp3
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
    data = {"audio":text, "lang": "zh","type":2} #向有道批次發請求，得到單詞、短語的發音
    resp = requests.post("https://dict.youdao.com/dictvoice", data=data, headers=headers) #發起資料請求
    with open(target_name,"wb") as f:#獲取請求結果並寫入本地
        f.write(resp.content)

YahooDictionary/yahooDictionary.py at master · LaiYongRen/YahooDictionary
    https://github.com/LaiYongRen/YahooDictionary/blob/master/yahooDictionary.py
    
文字介面的奇摩字典搜尋工具 | DarkRanger's Secret Area
    https://darkranger.no-ip.org/content/%E6%96%87%E5%AD%97%E4%BB%8B%E9%9D%A2%E7%9A%84%E5%A5%87%E6%91%A9%E5%AD%97%E5%85%B8%E6%90%9C%E5%B0%8B%E5%B7%A5%E5%85%B7
    https://darkranger.no-ip.org/uploads/src/ydict/ydict.py
    DICT_URL = "https://tw.dictionary.yahoo.com/dictionary?p="
    AUDIO_URL = "https://s.yimg.com/tn/dict/dreye/live"

yahoo字典 command line 版
    https://github.com/chenpc/ydict/blob/a1939726307ba0e76d56ecccfb3b5999f2293934/ydict
    python 2.x, 許多需要修改的, 作者已不再維護, 並推薦 https://github.com/zdict/zdict

zdict/zdict: The last online dictionary CLI framework you need.
    https://github.com/zdict/zdict    
    關注任何類型的線上字典。這個專案最初是從 https://github.com/chenpc/ydict 分叉出來的，它是 Yahoo! 的一個 CLI 工具

yahoo字典 command line 版,      簡短的 code (save to catDict.py)
    胖喵Blog: Python 版奇摩字典
        https://rocfatcat01.blogspot.com/2007/06/python.html
    [轉貼] Python 版奇摩字典 @ 胖虎的祕密基地 :: 痞客邦 ::
        https://idobest.pixnet.net/blog/post/24566998    

johnyluyte/fetch-online-dictionaries-audio: 可下載多個網路字典發音的 Chrome 外掛。
    https://github.com/johnyluyte/fetch-online-dictionaries-audio
    非 python, 但可下載非常多線上字典, 也列出線上字典網址
    
Undefeated-man/Online-translater-dictionary: A dictionary/translate combined software - catch some translating website's result, so you can get the result simultaneously.
    https://github.com/Undefeated-man/Online-translater-dictionary

Ryanshuai/English_Chinese_online_dictionary_crawler
    https://github.com/Ryanshuai/English_Chinese_online_dictionary_crawler
    
ashishps1/Online-Dictionary
    https://github.com/ashishps1/Online-Dictionary
    這是一個Python軟體，用於在線尋找英語單字的含義。使用Trie資料結構實現有效單字的高效搜尋。還實現了拼字糾正（使用動態編程）和自動建議。使用 BeautifulSoup 庫進行網頁抓取以進行線上尋找
    
pydict · PyPI
    https://pypi.org/project/pydict/
    Pydict is a simple command line dictionary, it lets you search the meanings of the word on the terminal. It refers to the online dictionary http://www.thefreedictionary.com It also pronouces the keywords.
    
np-csu/pydict: an English-Chinese/Chinese-English dictionary for Terminal
    https://github.com/np-csu/pydict
    在命令列下使用的英/漢、漢/英字典
    看起來是使用 有道 線上詞典, 當時結果是 json format

## Youtube download
youtube-dl https://ytdl-org.github.io/youtube-dl/
    youtube-dl 是一個命令列程序，用於從 YouTube.com 和其他一些網站下載影片。它需要 Python 解釋器（2.6、2.7 或 3.2+），並且不特定於平台。
    我們也提供包含 Python 的 Windows 可執行檔
    -  Q : youtube-dl 在 Windows 上啟動非常緩慢
       A : Add a file exclusion for youtube-dl.exe in Windows Defender settings.
    - YouTube 在 2014 年 3 月及之後更改了播放清單格式，因此您至少需要 youtube-dl 2014.07.25 才能下載所有 YouTube 影片
    - Q : 我在嘗試下載影片時收到 HTTP 錯誤 402
      A : 如果您下載太多，YouTube 會要求您通過驗證碼測試。我們正在考慮提供一種方法來讓您解決驗證碼問題，但目前，您最好的做法是將網頁瀏覽器指向 youtube URL，解決驗證碼問題，然後重新啟動 youtube-dl。
    - 只有在安裝了 rtmpdump 後才能下載透過 RTMP 協定串流的影片或影片格式。
      下載 MMS 和 RTSP 影片需要安裝 mplayer 或 mpv    

下載 Youtube 影片 ( mp4、mp3、字幕 ) - Python 教學 | STEAM 教育學習網
    https://steam.oxxostudio.tw/category/python/example/youtube-download.html
    使用 Python 的 pytube 第三方函式庫，輸入 Youtube 網址後就會自動下載為影片檔 mp4，單純下載為聲音檔 mp3，甚至可以進一步下載有字幕影片的字幕，儲存為 srt 或 txt    
    下載 Youtube 影片字幕為 srt 或 txt : 
    使用 yt.captions 方法，可以取得該 Youtube 影片全部的字幕 ( 如果是 auto 自動產生，字幕語系前方會出現 a. 標示 )，取得字幕後，透過 xml_captions 就能將指定語系的字幕轉換成 xml 檔案。
    由於 pytube 內建的 generate_srt_captions() 方法會發生 KeyError: 'start' 錯誤，因此直接使用 BeautifulSoup 套件讀取 xml 的內容，再透過數學計算和字串格式化的方法，轉換成字幕檔案格式，最後輸出成為 srt 或 txt。...

## xx old idea

plan format syntax :
    aacca = a2c2a = 100 100 75 75 100
    A=fast(175%) B=fast(150%) C=fast(125%) a=Normal(100%) b=slow(75%) c=slow(50%) d=slow(25%)
    以上語法包含 速度、次數
    
## wx.TextCtrl with Rich2
MultiText | 無私的分享是美德~
    https://weiyu0513.blogspot.com/2011/03/multitext.html    
 richText = wx.TextCtrl(panel, -1,
        "If supported by the native control, this is reversed, and this is a different font.",
        size=(200, 100), style=wx.TE_MULTILINE|wx.TE_RICH2) 
        richText.SetInsertionPoint(0)
        richText.SetStyle(44, 52, wx.TextAttr("white", "black"))
        points = richText.GetFont().GetPointSize()
        f = wx.Font(points + 3, wx.ROMAN, wx.ITALIC, wx.BOLD, True) 
        richText.SetStyle(68, 82, wx.TextAttr("blue", wx.NullColour, f))    
    
## button
使用 wx.lib.buttons 畫出的才像標準 windows button !
see "wx.lib.buttons.py"

import wx.lib.buttons as Buttons

btn = Buttons.GenButton(panel, -1, 'Genric Button')

bmp = wx.Bitmap("key_Del.png", wx.BITMAP_TYPE_ANY)
btn = Buttons.GenBitmapTextButton(panel, -1, bmp, "Bitmapped Text",size=(175, 75))   # <---


//
Howto make an instance of wx.lib.buttons.GenButton support accelerator
    https://wxpython-users.wxwidgets.narkive.com/7oAwa2nJ/howto-make-an-instance-of-wx-lib-buttons-genbutton-support-accelerator
The automatic behavior of turning underlined letters in the label into
accelerators is a built-in feature of the native button widget on
Windows, and not anything that wxWidgets does. But you can simulate
something similar yourself. Just add the accelerator to a
wx.AcceleratorTable yourself, and then set that accelerator table on the
parent window. You'll also need to bind a wx.EVT_MENU event for the ID
to the same handler that you bind wx.EVT_BUTTON to.

將標籤中帶下劃線的字母自動轉換為加速鍵的行為是 Windows 上本機按鈕小部件的內建功能，而不是 wxWidgets 所做的任何事情。 
但你可以自己模擬類似的東西。 只需自行將加速器新增至 wx.AcceleratorTable 中，然後在父視窗上設定該加速器表即可。 
您還需要將 ID 的 wx.EVT_MENU 事件綁定到與 wx.EVT_BUTTON 綁定的相同處理程序。
    
## html editor
html editor 推薦 所見即所得

BlueGriffon「藍獅鷲」 一款免費跨平台所見即所得的網頁編輯器軟體，支援HTML5、CSS3 - WEDO網頁設計公司
    https://rwd.wedo.com.tw/index.php/knowledge-articles/free-software/508-bluegriffon-html5-css3
可以直接插入圖片的所見即所得HTML編輯器：Summernote / Summernote: A WYSIWYG HTML editor Editor That Can Directly Insert Pictures - 布丁布丁吃什麼？
    https://blog.pulipuli.info/2023/06/htmlsummernote-summernote-a-wysiwyg-html-editoreditor-that-can-directly-insert-pictures.html
    
## keyboard
- use an accelerator table
    ```python
    ac = [(wx.ACCEL_NORMAL, wx.WXK_LEFT, widget.GetId())]
    tbl = wx.AcceleratorTable(ac)
    self.SetAcceleratorTable(tbl)
    ```
  如果您沒有希望觸發其事件的小部件，並且更喜歡某種具有事件綁定的「不可見」小部件，那麼您可以執行以下操作：
    ```python
    ac = []
    keys = [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN]
    for key in keys:
        _id = wx.NewId()
        ac.append((wx.ACCEL_NORMAL, key, _id))
        self.Bind(wx.EVT_MENU, self.your_function_to_call, id=_id)
    tbl = wx.AcceleratorTable(ac)
    self.SetAcceleratorTable(tbl)    
    ```

- wxPython --- how to programatically invoke menu item? 
    https://discuss.wxpython.org/t/how-to-programatically-invoke-menu-item/25342/3
    ...    
    `event = wx.MenuEvent(wx.wxEVT_COMMAND_MENU_SELECTED, menuitem.GetId(), menu)`
    `wx.PostEvent(frame, event)`
    請同時記住，wx.PostEvent 不會立即發送事件，而是將其放入佇列中，作為下一個空閒事件的一部分進行處理。
    如果您確實希望立即處理它，那麼您可以使用：`frame.GetEventHandler().ProcessEvent(event)`

- wx.UIActionSimulator
    https://forum.kicad.info/t/python-place-move-footprint-with-a-mouse/46332/8    
    ```python
    wnd = [i for i in self._pcbnew_frame.Children if i.ClassName == 'wxWindow'][0]
    wx.PostEvent(wnd, evt)
    ...
    keyinput = wx.UIActionSimulator()
    ...
    ```
    
## icon
Download 1,337,000 free icons (SVG, PNG)
    https://icons8.com/icons
        
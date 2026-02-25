

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="author" content="天天盈球" />
    <meta name="keywords" content="" />
    <meta name="description" content="" />
    <title>天天盈球</title>
    <link rel="stylesheet" href="/resources/css/global-2014.css?v=20250613001">
    <link rel="stylesheet" href="/resources/css/style.css?v=20250613001">
    <script src="/resources/js/ccjspack.js?v=20260206001"></script>
    <script src="/resources/js/jquery-1.7.2.min.js?v=20260206001"></script>



    <style>
        .wrap1200{ width:1200px; margin-left:auto; margin-right:auto; position:relative;}
        .errorWrap{ padding: 90px 190px 0; display: flex; align-items: center; justify-content: space-between; }
        .errorWrap .link{ display: block; width: 160px;height: 45px; line-height: 45px; text-align: center; font-size: 14px; color: #fff;background: #FF8200;border-radius: 8px; }
        .errorWrap .link:hover{ text-decoration: none; background: #ed7a02; }
        .contactInfo2{ padding: 40px 190px 0; }
        .contactInfo2 ul{ display: flex; padding-top: 10px; }
        .contactInfo2 ul li{ margin-right: 43px; display: flex; align-items: center; }
        .contactInfo2 .phoneIcon{ width: 42px; height: 42px; margin-right: 13px; background: #eee; border-radius: 50%; display: flex; align-items: center; justify-content: center;}
        .contactInfo2 .txt h6{ font-size: 18px; font-family: PingFang-SC-Medium, PingFang-SC;}
        .contactInfo2 .txt p{ opacity: .5}
    </style>
</head>
<body style="background: linear-gradient(180deg, #EEEEEE 0%, #FFFFFF 100%);">








<script  type="text/javascript">

    var isAicai = false;
    

    var isAicaiHeader = false;
    

    var isAicaiHeaderNew = false;
	


    //过滤器那里返回的判断有问题 在这里打个补丁
    var url = window.location.href;
    if(!isAicaiHeaderNew) {
        isAicaiHeaderNew = url.indexOf("pc.ttyingqiu.com") !== -1 || url.indexOf("pc-beta.ttyingqiu.com") !== -1 || url.indexOf("pc-daily.ttyingqiu.com") !== -1;
    }
    if(!isAicaiHeader) {
        isAicaiHeader = url.indexOf("aicai.com") !== -1;
    }

    isAicai = isAicaiHeaderNew || isAicaiHeader;


    if (isAicaiHeader) {
        window.loadLogin = function () {
            window.top.location.href = "https://passport.aicai.com/xpassport/aicai/login/newIndex?redirectUrl=" + window.top.location.href;
        };
    }
    //aicai.yingqiu.com 走跳转第三方登录页面，走联合登录
    if (isAicaiHeaderNew) {

        window.loadLoginForAicaiLogin = function () {
            var backUrl = encodeURIComponent(window.top.location.href);
            var redirectUrl = location.protocol + "//" + location.host + "/aicai/auth/login?backUrl="+backUrl;
            redirectUrl = encodeURIComponent(redirectUrl);
            window.top.location.href = "https://passport.aicai.com/xpassport/aicai/login/ttyq/index?redirectUrl=" + redirectUrl;
        };

        window.loadLogin = loadLoginForAicaiLogin;
    }

    //爱彩盈球 host
    var YINGQIU_AICAI_HOST = "pc.ttyingqiu.com";
    
</script>


   
        


<meta name="viewport" content="width=1200, user-scalable=yes"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="format-detection" content="telephone=no"/>
<link href="https://r.ttyingqiu.com/r/css/??common/webdialog/webdialog.css,web/login.css,common/web/global-2014.css,common/web/yqHead2022.css?v=20250613001"
      rel="stylesheet"/>




<script type="text/javascript" src="https://r.ttyingqiu.com/r/js/??common/public/MyPromise.js?v=20250613001"></script>

<script type="text/javascript" src="https://r.ttyingqiu.com/r/js/??common/plugins/vue/vue.min.js,common/public/http.js
,common/web/header.js,web/login/captcha.service.js?v=20250613001"></script>

<link href="https://r.ttyingqiu.com/r/css/??web/captcha.css?v=20250613001" rel="stylesheet"/>

<script type="text/javascript" src="https://r.ttyingqiu.com/r/js/??web/login/jsencrypt-rsa.js,common/public/eventBus.js
,common/web/newHeader/yqhead.js?v=20250613001"></script>
<script type="text/javascript" src="https://r.ttyingqiu.com/r/js/??common/web/ccjspack.js?v=20250613001"></script>


<script language="javascript">
    /*
    var isAicai = ;
	if(isAicai===undefined)
    isAicai = false;*/

    /*function addFavorite(){
        var a = window.location.href;
        var b = document.title;
        if(document.all) {
            window.external.AddFavorite(a,b);
        }else if(window.sidebar){
            window.sidebar.addPanel(b,a,"");
        }else{
            alert("对不起，您的浏览器不支持此操作!\n请您使用菜单栏或Ctrl+D收藏本站。");
        }
    }*/

    $(function(){
        var codeId = null;
        if((id = getQueryString())!=null){//优先获取url上的
            codeId = id;
        }else if((id = getCookieId())!=null){//url没有就在cookie里获取，都没有就使用默认
            codeId = id;
        }
        if(codeId == '2335373'){
            $("#top_down_img").attr("src","https://www.ttyingqiu.com/resources/images/QRCode/2335373.png");
        }
        if(codeId == '2335123'){
            $("#top_down_img").attr("src","https://r.ttyingqiu.com/r/images/web/QRCode/2335123.png?v=20250613001");
        }
        if(codeId == '2335053'){
            $("#top_down_img").attr("src","https://r.ttyingqiu.com/r/images/web/QRCode/2335053.png?v=20250613001");
        }

        //获取url上的渠道号
        function getQueryString()
        {
            var reg = new RegExp("(^|&)"+ "agentId" +"=([^&]*)(&|$)");
            var r = window.location.search.substr(1).match(reg);
            if(r!=null)return  unescape(r[2]); return null;
        }
        //获取cookie里的渠道号
        function getCookieId(){
            var arr,reg=new RegExp("(^|)"+"NAGENTID"+"=([^;]*)(;|$)");
            if(arr = document.cookie.match(reg)){
                return unescape(arr[2]);
            }else{
                return null;
            }
        }
    })
</script>

<!--顶部导航-->
<div class="topWrap">

    <style>
        .topSwitch{ display: flex; align-items: center; padding: 20px; white-space: nowrap; }
        .topSwitch a{ box-sizing: border-box; height: 100px; flex:1; margin-right: 20px; display: flex; align-items: center; justify-content: center; border-radius: 16px; font-size: 44px; font-weight: bold; color: #fff; }
        .topSwitch a:last-child{ margin-right: 0; }
        .topSwitch a.red{ background: #ea4747;border: 2px solid #c22d2d;}
        .topSwitch a.yellow{ background: #f39c10;border: 2px solid #cc881c;}
        .topSwitch.w960 a:first-child{ flex:1.13; }
        .topSwitch a:hover{ color: #fff; }

        /*h5访问pc960页面要满屏*/
        .h5_to_pc{min-width:960px;}
        .h5_to_pc .topWrap{ min-width: 960px; }
        .h5_to_pc .wrap1200{ width: 960px; }
        .h5_to_pc .footNav dl{ width: 145px; }
        .h5_to_pc .nav li{padding: 0px 12px;}

    </style>
    <div class="topSwitch" style="display: none;" id="wap_header">

        <a  class="red" style="color:#fff!important;" onclick="headDownloadJcob()" >
            下载天天盈球APP
        </a>
        <a href="javascript:;" onclick="toH5('https://m.51yingqiu.com')" class="yellow">
            切换H5版本
        </a>
    </div>

	
    
    <div class="wrap1200">
        <div class="topBar">
            <h1 class="logo fl">
                <a href="https://www.ttyingqiu.com/index" class="logoImg"></a>
            </h1>
            <div class="nav fl clearfix">
                <ul>
                    <li id="indexPage">
                        <a href="https://www.ttyingqiu.com">首页</a>
                    </li>
                    <li id="matchListPage" class="J_topMenuSelect">
                        <a href="https://www.ttyingqiu.com/jczq">即时比分
							<i>
								<svg t="1697698867387" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7151" width="48" height="48"><path d="M550.464 684.16a31.872 31.872 0 0 0 12.16-7.68l226.304-226.24a32 32 0 0 0 0-45.248l-22.592-22.656a32 32 0 0 0-45.312 0L534.272 569.152 351.296 386.24a32 32 0 0 0-45.248 0l-22.592 22.592a32 32 0 0 0 0 45.248l226.24 226.304a32 32 0 0 0 40.768 3.712z" fill="#4E5969" p-id="7152"></path></svg>
							</i>
						</a>
						<div class="navSlide">
							<a href="https://www.ttyingqiu.com/jczq">足球比分</a>
							<a href="https://www.ttyingqiu.com/jclqList">篮球比分</a>
						</div>
                    </li>
                    
                    <li id="liveDataPage" class="J_topMenuSelect">
                    	<a href="https://www.ttyingqiu.com/live/leagueIndex">赛事数据
							<i>
								<svg t="1697698867387" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7151" width="48" height="48"><path d="M550.464 684.16a31.872 31.872 0 0 0 12.16-7.68l226.304-226.24a32 32 0 0 0 0-45.248l-22.592-22.656a32 32 0 0 0-45.312 0L534.272 569.152 351.296 386.24a32 32 0 0 0-45.248 0l-22.592 22.592a32 32 0 0 0 0 45.248l226.24 226.304a32 32 0 0 0 40.768 3.712z" fill="#4E5969" p-id="7152"></path></svg>
							</i>
						</a>
                        <div class="navSlide wh140">
                            <a href="https://www.ttyingqiu.com/live/leagueIndex">
                                足球资料
                            </a>
                            <a href="https://www.ttyingqiu.com/live/leagueIndex/bk">
                                篮球资料
                            </a>
                            <a href="https://www.ttyingqiu.com/vip/wm/index">
								专家风向标
							</a>
							<a href="https://www.ttyingqiu.com/vip/special/list/5">
								极限战绩
							</a>
							<a href="https://www.ttyingqiu.com/vip/special/list/7">
								伤停身价
							</a>
                        </div>
                    </li>
                    <li id="bfPage">
						<a href="https://www.ttyingqiu.com/vip/bf/index">必发指数</a>
					</li>
                    <li id="newsPage">
                        <a href="https://www.ttyingqiu.com/news/home">赛事资讯</a>
                    </li>
                    
                    
                    <li class="J_topMenuSelect" id="mobilePage">
                        <a href="javascript:;" onclick="window.open('https://www.ttyingqiu.com/topic/2016/download')">App下载</a>
                        <div class="downSlide" style="left:-30px;">
                            <h5 class="fs18 mb10">下载手机客户端</h5>
                            <div class="downAppWrap clearfix" style="width: 180px;">
                                <div class="downApp">
                                    <a href="javascript:;"
                                       onclick="window.open('https://www.ttyingqiu.com/topic/2016/download')">
                                        <img class="ttyqLogo" src="https://r.ttyingqiu.com/r/images/common/web/header/ttyqLogo.png">
                                        <h6 class="fs14 c333">天天盈球</h6>
                                        <p class="fs12 c999">天天盈球官方App，专业的<br>足篮球赛事解读平台。</p>
                                        <div class="ewm">
                                            <img id="top_down_img" src="https://r.ttyingqiu.com/r/images/common/web/download_qr/to_51yq_d.png?v=20250613001">
                                        </div>
                                        <p class="fs12 c999 mt10">扫码下载App</p>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </li>
                    <li id="vipPage">
                        <a href="https://www.ttyingqiu.com/vip/member/index">会员</a>
                    </li>
                    <li id="helpPage">
                        <a href="https://www.ttyingqiu.com/home/help">帮助</a>
                    </li>
                </ul>
            </div>
            <div class="fr clearfix">
                <!--客服微信-->
                <div class="serviceI fl">
                    <div class="kfIcon">
                        <svg t="1647241497456" class="icon" viewBox="0 0 1024 1024" version="1.1"
                             xmlns="http://www.w3.org/2000/svg" p-id="44207" width="34" height="34">
                            <path d="M629.333333 629.333333m-352 0a352 352 0 1 0 704 0 352 352 0 1 0-704 0Z"
                                  fill="#cdfaff" p-id="44208"></path>
                            <path d="M250.88 675.2A123.093333 123.093333 0 0 1 128 552.106667v-80.213334a122.88 122.88 0 0 1 245.973333 0v80.426667a123.093333 123.093333 0 0 1-123.093333 122.88z m0-240.853333A37.76 37.76 0 0 0 213.333333 471.893333v80.426667a37.546667 37.546667 0 1 0 75.306667 0v-80.426667a37.76 37.76 0 0 0-37.76-37.76zM773.12 675.2a123.093333 123.093333 0 0 1-122.88-122.88v-80.426667a122.88 122.88 0 1 1 245.973333 0v80.426667a123.093333 123.093333 0 0 1-123.093333 122.88z m0-240.853333a37.76 37.76 0 0 0-37.546667 37.546666v80.426667a37.546667 37.546667 0 1 0 75.306667 0v-80.426667a37.76 37.76 0 0 0-37.76-37.76z"
                                  fill="#666666" p-id="44209"></path>
                            <path d="M512 936.106667a42.666667 42.666667 0 0 1 0-85.333334 218.666667 218.666667 0 0 0 218.453333-218.24 42.666667 42.666667 0 0 1 85.333334 0A304 304 0 0 1 512 936.106667zM773.12 434.133333a42.666667 42.666667 0 0 1-42.666667-42.666666 218.453333 218.453333 0 1 0-436.693333 0 42.666667 42.666667 0 0 1-85.333333 0 303.786667 303.786667 0 0 1 607.36 0 42.666667 42.666667 0 0 1-42.666667 42.666666z"
                                  fill="#666666" p-id="44210"></path>
                        </svg>
                    </div>
                    <div class="txt">
                        <div class="phone" id="kf_header"></div>
                        <div class="wxMenuWrap J_topMenuSelect">
                            <a href="javascript:;" class="wxMenu">
                                <i>
                                    <svg t="1647241992759" class="icon" viewBox="0 0 1024 1024" version="1.1"
                                         xmlns="http://www.w3.org/2000/svg" p-id="45056" width="18" height="18">
                                        <path d="M686.6 372.5c4.5 0 9 0.1 13.4 0.3C676.5 246.1 544.2 149 384.5 149 208.2 149 65.3 267.3 65.3 413.2c0 85.6 49.1 161.6 125.3 209.9 1 0.6 2.9 1.8 2.9 1.8l-30.9 95.6L278 662.3l5.4 1.5c31.7 8.7 65.7 13.5 101 13.5 7.2 0 14.3-0.3 21.4-0.6-6.5-20.1-10.1-41.2-10.1-63 0.1-133.2 130.4-241.2 290.9-241.2z m-191-93.2c24.8 0 44.8 19.2 44.8 43 0 23.7-20 43-44.8 43s-44.8-19.3-44.8-43c0-23.8 20-43 44.8-43z m-222.2 85.9c-24.7 0-44.8-19.3-44.8-43s20.1-43 44.8-43c24.8 0 44.9 19.2 44.9 43 0 23.7-20.1 43-44.9 43z m685.3 250.1c0-123.3-120.7-223.2-269.6-223.2-149 0-269.7 99.9-269.7 223.2 0 123.3 120.8 223.2 269.7 223.2 29.8 0 58.5-4 85.3-11.4 1.5-0.4 4.6-1.3 4.6-1.3l97.4 49.2-26-80.8s1.7-1 2.5-1.5c64.3-40.8 105.8-105.1 105.8-177.4z m-363.5-40.6c-20.9 0-37.9-16.3-37.9-36.3 0-20 16.9-36.2 37.9-36.2 20.9 0 37.9 16.2 37.9 36.2 0 20.1-17 36.3-37.9 36.3z m187.6 0c-20.9 0-37.8-16.3-37.8-36.3 0-20 16.9-36.2 37.8-36.2 21 0 37.9 16.2 37.9 36.2 0 20.1-16.9 36.3-37.9 36.3z"
                                              fill="#00c800" p-id="45057"></path>
                                    </svg>
                                </i>
                                微信咨询
                            </a>
                            <div class="wxSlideWrap">
                                <div class="wxSlide">
                                    <div class="time">
                                        <b>客服电话服务时间</b>
                                        <span>09:00~18:00</span>
                                    </div>
                                    <div class="ewm">
                                        <p>您还可以<br>添加盈球管家微信咨询</p>
                                        <img src="">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!--未登录-->
                <div class="righLink fl clearfix" style="display: block;" id="hasNotLogin">
                    <a href="javascript:;" class="top_register fr" id="headRegister">注册</a>
                    <a href="javascript:;" class="top_loginLink fr" id="headLogin">登录</a>
                </div>
                <!--以登录-->
                <div class="hasLoginBox fl pr J_topMenuSelect" style="display: none;" id="hasLogin">
                    <a href="javascript:;" class="hasLogin clearfix">
                        <div class="userImg">
                            <img src="https://r.ttyingqiu.com/r/images/common/web/header/defaultImg.png" id="userIcon">
                        </div>
                        <span class="userName"><span id="userName"></span><i class="triangle-a"></i></span>
                    </a>
                    <div class="userSlideInfo">
                        <ul>
                            <li><a href="//www.ttyingqiu.com/user/planOrder" id="myOrder">我的订单</a></li>
                            <li><a href="//www.ttyingqiu.com/member/goldDetail">金币明细</a></li>
                            <li><a href="//www.ttyingqiu.com/query/couponList" id="myCoupon">我的优惠券</a></li>
                            <li><a href="//www.ttyingqiu.com/query/mySetMeal">我的竞彩套餐</a></li>
                            <li><a href="//www.ttyingqiu.com/query/mySfcSetMeal">我的胜负彩套餐</a></li>
                            
                            <li><a href="//www.ttyingqiu.com/member/myVip">我的会员</a></li>
                            <li id="bindPhone" style="display:none"><a href="//www.ttyingqiu.com/binding/phone">绑定手机</a>
                            </li>
                            <li id="setPassword" style="display:none"><a href="//www.ttyingqiu.com/settings/password">设置密码</a>
                            </li>
                            <li><a href="javascript:;" id="logoutBtn">退出登录</a></li>
                        </ul>
                    </div>
                </div>
                
            </div>
        </div>
    </div>
</div>

<script>
    if (navigator.userAgent.indexOf("jcob-app")==-1&&(navigator.userAgent.indexOf("Android") != -1||navigator.userAgent.indexOf("iPhone") != -1 || navigator.userAgent.indexOf("iPad") != -1)) {
        document.getElementById("wap_header").style="display:flex;";
        document.querySelector("body").style="padding-top: 245px!important;";
    }
    // if((navigator.userAgent.indexOf("Android") != -1||navigator.userAgent.indexOf("iPhone") != -1 || navigator.userAgent.indexOf("iPad") != -1)) {
    //     document.querySelector("body").classList = "h5_to_pc";
    //     var vp = document.querySelector("meta[name=viewport]");
    //     vp.setAttribute("content",vp.getAttribute("content")+",width=960");
    // }

    function getCookie(name) {
        let reg = RegExp(name + '=([^;]+)')
        let arr = document.cookie.match(reg)
        if (arr) {
            return arr[1]
        } else {
            return ''
        }
    }
    var isWechat = navigator.userAgent.indexOf("MicroMessenger")!=-1;
    function headDownloadJcob(){
        var agentId = '2335373';
        if(getCookie("agentId"))agentId = getCookie("agentId");
        // if(isWechat){
            location.href="http://m.51yingqiu.com/#/download?agentId="+agentId;
        // }else{
        //     location.href = 'https://m.ttyingqiu.com/api/download/down?type2=jcgcs&agentId='+ agentId
        // }
    }



    function toH5(domain){
        var matchId = document.getElementById("qt_match_id")!=null?document.getElementById("qt_match_id").value:null;
        var jieduId = document.getElementById("interpretationId")!=null?document.getElementById("interpretationId").value:null;
        var expertId = document.getElementById("expert")!=null?document.getElementById("expert").dataset.exportid:null;
        //删除cookie
        var exp = new Date();
        exp.setTime(exp.getTime() - 1);
        var cval = getCookie("formMobile");
        if (cval != null)
            document.cookie =  "formMobile=;expires=" + exp.toGMTString()+';domain=.ttyingqiu.com;path=/';

        var url = null;
        if(location.pathname=='/live'||location.pathname.indexOf('/jczqList')==0){//足球
            url = domain+"/#/tabs/match;game=0"
        }else if(location.pathname.indexOf('/jczq')==0){
            url = domain+"/#/tabs/match;game=407"
        }else if(location.pathname.indexOf('/bjdc')==0){
            url = domain+"/#/tabs/match;game=408"
        }else if(location.pathname.indexOf('/sfc')==0||location.pathname.indexOf('/6cbqc')==0||location.pathname.indexOf('/4cjq')==0){
            url = domain+"/#/tabs/match;game=401"
        }else if(location.pathname.indexOf('/live/zq/matchDetail/fx')==0){
            url = domain+"/#/match-detail/"+matchId+"/0"
        }else if(location.pathname.indexOf('/live/zq/matchDetail/oz')==0||location.pathname.indexOf('/live/zq/matchDetail/rq')==0||location.pathname.indexOf('/live/zq/matchDetail/dxq')==0){
            url = domain+"/#/match-detail/"+matchId+"/1"
        }else if(location.pathname.indexOf('/live/zq/matchDetail/data')==0){
            url = domain+"/#/match-detail/"+matchId+"/0"
        }else if(location.pathname.indexOf('/live/zq/matchDetail/info')==0){
            url = domain+"/#/match-detail/"+matchId+"/2"
        }else if(location.pathname.indexOf('/live/zq/matchDetail/plan')==0){
            url = domain+"/#/match-detail/"+matchId+"/3"
        }else if(location.pathname.indexOf('/live/zq/matchDetail/live')==0){
            url = domain+"/#/match-detail/"+matchId+"/5"
        }else if(location.pathname.indexOf('/jclqList')==0){//篮球
            url = domain+"/#/tabs/match-bk;game=0"
        }else if(location.pathname.indexOf('/jclq')==0){
            url = domain+"/#/tabs/match-bk;game=406"
        }else if(location.pathname.indexOf('/live/lq/matchDetail/fx')==0){
            url = domain+"/#/bk-match-detail/"+matchId+"/0"
        }else if(location.pathname.indexOf('/live/lq/matchDetail/oz')==0||location.pathname.indexOf('/live/lq/matchDetail/yp')==0||location.pathname.indexOf('/live/lq/matchDetail/dxq')==0){
            url = domain+"/#/bk-match-detail/"+matchId+"/1"
        }else if(location.pathname.indexOf('/live/lq/matchDetail/info')==0){
            url = domain+"/#/bk-match-detail/"+matchId+"/2"
        }else if(location.pathname.indexOf('/live/lq/matchDetail/plan')==0){
            url = domain+"/#/bk-match-detail/"+matchId+"/3"
        }else if(location.pathname.indexOf('/live/lq/matchDetail/live')==0){
            url = domain+"/#/bk-match-detail/"+matchId+"/5"
        }else if(location.pathname.indexOf('/lottery/index')==0){//专家推荐
            url = domain+"/#/tabs/plan"
        }else if(location.pathname.indexOf('/sportsLottery/301')==0){
            url = domain+"/#/jiedu-list;type=1"
        }else if(location.pathname.indexOf('/sportsLottery/302')==0){
            url = domain+"/#/jiedu-list;type=3"
        }else if(location.pathname.indexOf('/sportsLottery/303')==0){
            url = domain+"/#/jiedu-list;type=2"
        }else if(location.pathname.indexOf('/expert/expertRanking')==0){
            url = domain+"/#/expert/mr/4/1"
        }else if(location.pathname.indexOf('/member/setMeal')==0){
            url = domain+"/#/set-meal-list"
        }else if(location.pathname.indexOf('/interpretation/detail')==0){
            url = domain+"/#/tjInterpretation/"+jieduId
        }else if(location.pathname.indexOf('/expert/home')==0){
            url = domain+"/#/public/expertHome/"+expertId
        }else if(location.pathname.indexOf('/vip/member/index')==0){//会员
            url = domain+"/#/vip/index"
        }else if(location.pathname.indexOf('/vip/wm/index')==0){
            url = domain+"/#/wind-mark-lis"
        }else if(location.pathname.indexOf('/vip/bf/index')==0){
            url = domain+"/#/vip-special/list;type=4"
        }
        if(url!=null){
            if(url.indexOf("?")==-1){
                location.href = url+"?source=1";
            }else {
                location.href = url+"&source=1";
            }
        } else{
            location.href = domain+"/#/tabs/match?source=1"
        }

    }
</script>
















<div class="wrap1200">
    <img  class="mt25" width="130" src="/resources/images/header/logo.png">
    <div class="errorWrap">
        <div class="txt">
            <a href="/">
                <img width="313" src="/resources/images/error/error01.png">
            </a>
            <p class="fs16 mt20">抱歉，内部服务器错误…</p>
            <a href="/" class="link mt20" id="backButton">返回首页</a>
        </div>
        <div>
            <img width="425" src="/resources/images/error/error02.png">
        </div>
    </div>
    <div class="contactInfo2">
        <div class="fs14">联系客服：</div>
        <ul>
            <li>
                <div class="phoneIcon">
                    <svg t="1645694670871" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="35836" width="20" height="20"><path d="M618.3 756.9l37.9-71.2c11.2-21 35.3-31.7 58.4-26L888 702.9c23.1 5.8 39.4 26.6 39.4 50.4l0.1 72.6h0.5v50.2c0 29.7-24.9 53.9-54.6 52-415.9-27-748.4-359.5-775.3-775.3-1.9-29.7 22.2-54.6 52-54.6h50.2v0.2l71.1 0.1c23.9 0 44.7 16.3 50.4 39.4L365 311.3c5.8 23.1-4.9 47.3-26 58.5L268.9 407c72.3 153.7 195.8 277.4 349.4 349.9z" p-id="35837" fill="#666666"></path></svg>
                </div>
                <div class="txt">
                    <h6>(0755) 61619788</h6>
                    <p>服务时间09:00-18:00</p>
                </div>
            </li>
            <li>
                <img width="64" src="https://cdn.ttyingqiu.com/news/image/2022/2/22/202202221017000013.jpg">
                <div class="txt fs14 ml10">
                    如有疑问<br>请添加管家微信咨询
                </div>
            </li>
        </ul>
    </div>

</div>





	
		





<div class="footer mt30" style="height: initial">
	<div class="wrap1200 clearfix">
		<div class="footNav fl clearfix">
			<dl>
				<dt>体育工具服务</dt>
				<dd><a href="https://www.ttyingqiu.com/jczq" target="_blank">即时比分</a></dd>
				<dd><a href="https://www.ttyingqiu.com/live/leagueIndex" target="_blank">赛事数据</a></dd>
				<dd><a href="https://www.ttyingqiu.com/news/home" target="_blank">情报资讯</a></dd>
				<dd><a href="https://www.ttyingqiu.com/sportsLottery/301" target="_blank">专家推荐</a></dd>
			</dl>
			
			<dl>
				<dt>服务与支持</dt>
				<dd><a href="javascript:;" onclick="window.open('https://www.ttyingqiu.com/topic/2016/download')">下载天天盈球</a></dd>
				<dd><a href="https://www.ttyingqiu.com/home/help" target="_blank">帮助中心</a></dd>
				<dd><a href="https://www.ttyingqiu.com/about" target="_blank">关于我们</a></dd>
			</dl>
		</div>
		<div class="footRight fr">
			<ul>
				<li>
					<div class="contactInfo">
						<div class="phone">
							<div class="phoneIcon">
								<svg t="1645694670871" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="35836" width="20" height="20"><path d="M618.3 756.9l37.9-71.2c11.2-21 35.3-31.7 58.4-26L888 702.9c23.1 5.8 39.4 26.6 39.4 50.4l0.1 72.6h0.5v50.2c0 29.7-24.9 53.9-54.6 52-415.9-27-748.4-359.5-775.3-775.3-1.9-29.7 22.2-54.6 52-54.6h50.2v0.2l71.1 0.1c23.9 0 44.7 16.3 50.4 39.4L365 311.3c5.8 23.1-4.9 47.3-26 58.5L268.9 407c72.3 153.7 195.8 277.4 349.4 349.9z" p-id="35837" fill="#ffffff"></path></svg>
							</div>
							<div class="txt">
								<h6 id="kfTxt_phone"></h6>
								<p>服务时间09:00-18:00</p>
							</div>
						</div>
						<div class="butler">
							<a href="javascript:;">微信联系管家</a>
							<div class="butlerEwm" id="kfTxt_qrcode">
								<img src="">
								<p>如有疑问<br>请添加管家微信咨询</p>
							</div>
						</div>
					</div>
				</li>
				<li>
					<img src="https://r.ttyingqiu.com/r/images/web/wxewm.jpg">
					<p>天天盈球公众号</p>
				</li>
			</ul>
		</div>
	</div>
	<div class="copyRightWrap">
		<div class="wrap1200">
			<div class="copyRight">
				<span>Copyright © 2022 天天盈球版权所有</span>
				<span class="ml10">深圳市天盈互动网络技术有限公司</span>
				<span class="ml10 "><a href="https://beian.miit.gov.cn/" target="_blank" style="color: rgba(255,255,255,.7);">ICP证：粤ICP备16089222号</a></span>
				<a href="https://www.ttyingqiu.com/cert" class="ml10" style="color: rgba(255,255,255,.7);" target="_blank">增值电信业务经营许可证: 粤B2-20230096</a>
				<a href="https://www.beian.gov.cn/portal/registerSystemInfo?recordcode=44030502000756" class="ml10" style="color: rgba(255,255,255,.7);" target="_blank">粤公网安备 44030502000756号</a>
			
				
				<div class="mr10" style="margin-left: auto;">
					<a class="gfrzLogo" href="http://www.itrust.org.cn/Home/Index/wx_certifi/wm/WX2017062801.html" target="_blank">
						<img src="https://r.ttyingqiu.com/r/images/web/gfrz.png" alt="">
					</a>
				</div>
				
			</div>
		</div>
	</div>
</div>
<!--返回顶部-->







<!--右下角悬浮菜单-->
<div class="goFixedNew">
    <a href="javascript:;" class="downA jq_downBtn">
        <i>
            <svg t="1616482845223" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="15494" width="16" height="16"><path d="M813.176471 0H210.823529a60.235294 60.235294 0 0 0-60.235294 60.235294v903.529412a60.235294 60.235294 0 0 0 60.235294 60.235294h602.352942a60.235294 60.235294 0 0 0 60.235294-60.235294V60.235294a60.235294 60.235294 0 0 0-60.235294-60.235294z m0 963.764706H210.823529v-194.861177h602.352942zM210.823529 708.668235V60.235294h602.352942v648.432941z" fill="#ffffff" p-id="15495"></path><path d="M451.764706 899.614118h120.470588a30.117647 30.117647 0 0 0 0-60.235294h-120.470588a30.117647 30.117647 0 0 0 0 60.235294z" fill="#ffffff" p-id="15496"></path></svg>
        </i>
        <span>下载</span>
    </a>
    <div class="fixedEwm jq_fixedEwm" style="bottom:53px;height:190px">
        <div class="tit">下载手机客户端</div>
        <ul>
            <li>
                <img id="ttyq_dl_qr_img" src="https://r.ttyingqiu.com/r/images/common/web/download_qr/to_51yq_d.png?v=20250613001">
                <h5>天天盈球App</h5>
                <p>随时随地看比分</p>
            </li>
        </ul>
    </div>
    
    <a href="javascript:;" class="kf jq_kf" >
        <i>
            <svg t="1616482973981" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="19847" width="16" height="16"><path d="M365.006 485.574c0 39.639 33.033 72.671 72.671 72.671 39.64 0 72.671-33.032 72.671-72.67 0-39.64-33.032-72.672-72.67-72.672-41.29 0-72.672 33.032-72.672 72.671z m325.368-72.67c-39.639 0-72.67 33.031-72.67 72.67s33.031 72.671 72.67 72.671 72.671-33.032 72.671-72.67c0-39.64-33.032-72.672-72.67-72.672z m279.123 14.864h-4.955C914.994 256 759.742 178.374 693.677 146.994c-3.303-1.652-4.954-3.304-8.258-4.955 8.258-8.258 18.168-19.82 21.471-34.684 3.304-16.516-1.651-33.032-13.213-44.594-9.91-11.561-31.38-34.684-158.554-18.167C411.252 57.806 118.916 156.904 61.11 427.768h-6.607c-21.47 0-37.987 16.516-37.987 37.987v120.568c0 21.47 16.516 37.987 37.987 37.987h6.607c42.942 211.406 221.316 303.896 393.084 322.064v1.652c0 21.47 16.516 37.987 37.987 37.987h155.251c21.471 0 37.987-16.516 37.987-37.987v-90.839c0-21.47-16.516-37.987-37.987-37.987H492.181c-21.471 0-37.987 16.516-37.987 37.987v4.955c-99.097-11.561-265.91-61.11-310.504-242.787 11.562-6.607 21.471-19.82 21.471-34.684V464.103c0-14.864-8.258-26.426-19.82-33.032 66.065-257.652 396.388-305.548 399.691-307.2 21.471-3.303 37.987-3.303 52.852-4.955-3.303 8.258-4.955 16.516-4.955 26.426 0 13.213 4.955 33.032 26.426 51.2 8.258 8.258 19.82 13.213 39.639 23.123C716.8 247.742 835.716 307.2 880.31 431.07c-11.562 6.606-19.82 18.168-19.82 33.032v120.568c0 21.47 16.516 37.987 37.987 37.987h72.671c21.471 0 37.987-16.516 37.987-37.987V464.103c-1.651-19.82-18.167-36.335-39.638-36.335z" p-id="19848" fill="#ffffff"></path></svg>
        </i>
        <span>客服</span>
        <div class="kfWrap" style="top:-48px">
            <div class="kfTxt">
                <div class="ewm clearfix">
                    <img src="">
                    <div class="txt">
                        <h5 class="fs16 c333">有问题找管家</h5>
                        <p class="fs12 c999">微信扫码加盈球管家</p>
                    </div>
                </div>
                <div class="phoneInfo">
                    <h5 class="fs14 c333" id="kf_phone"></h5>
                    <p class="fs12 c999">服务时间  09:00~18:00</p>
                </div>
            </div>
        </div>
    </a>
    
    <a href="javascript:;" class="kffk jq_kffk" onclick="goFeedBack()">
        <i>
            <svg t="1616483050339" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="24665" width="16" height="16"><path d="M815.74 412.26c29.72-29.71 46.09-69.22 46.09-111.25s-16.37-81.55-46.09-111.25L712.25 86.26C682.54 56.56 643.02 40.19 601 40.19s-81.55 16.37-111.25 46.08L117.42 458.6 85.11 816.91l358.33-32.32 372.3-372.33zM546.35 142.87c30.13-30.13 79.17-30.13 109.3 0l103.49 103.49c30.13 30.13 30.13 79.17 0 109.3L425.38 689.42 212.6 476.63l333.75-333.76zM188.18 565.42L336.6 713.84l-163.14 14.72 14.72-163.14zM928.96 902.94H95.71c-22.11 0-40.03 17.93-40.03 40.03S73.6 983 95.71 983h833.25c22.11 0 40.03-17.93 40.03-40.03s-17.91-40.03-40.03-40.03z" fill="#ffffff" p-id="24666"></path></svg>
        </i>
        <span>反馈</span>
    </a>
    
    <a href="javascript:;" class="goTopNew" onclick="toTop()">
        <i>
            <svg t="1616483711318" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="58737" width="16" height="16"><path d="M896.149659 67.771523 126.54051 67.771523c-34.758642 0-62.935378 28.176736-62.935378 62.935378 0 34.757618 28.176736 62.934355 62.935378 62.934355l769.610172 0c34.758642 0 62.935378-28.176736 62.935378-62.934355C959.085036 95.948259 930.9083 67.771523 896.149659 67.771523zM557.654294 258.83814c-1.471514-1.470491-3.016707-2.862187-4.625344-4.181229-0.713244-0.586354-1.469468-1.095961-2.202155-1.6465-0.906649-0.681522-1.797949-1.384533-2.743484-2.01796-0.884137-0.591471-1.805112-1.105171-2.713808-1.648546-0.853437-0.509606-1.689479-1.044796-2.568499-1.515516-0.928139-0.496304-1.883907-0.917906-2.832512-1.364067-0.913812-0.431835-1.811252-0.886183-2.746554-1.27504-0.924045-0.382717-1.864464-0.689708-2.800789-1.02433-1.000793-0.36225-1.989307-0.744967-3.012613-1.054005-0.938372-0.283456-1.892093-0.491187-2.837628-0.729617-1.043772-0.264013-2.071172-0.554632-3.133364-0.766456-1.094938-0.215918-2.201132-0.344854-3.305279-0.503467-0.927115-0.13303-1.840928-0.309038-2.78237-0.402159-2.059915-0.201591-4.124947-0.311085-6.192026-0.312108-0.005117 0-0.011256 0-0.016373 0l0 0c-0.299829 0-0.599657 0.037862-0.898463 0.041956-16.406668-0.231267-32.884968 5.874801-45.402049 18.391882L148.569222 577.09967c-24.576745 24.578792-24.576745 64.425312 0 89.005127 12.288884 12.289907 28.396747 18.434861 44.502563 18.434861 16.105816 0 32.213679-6.144954 44.502563-18.434861l212.633818-212.634842L450.208167 893.124254c0 34.757618 28.176736 62.934355 62.934355 62.934355 34.758642 0 62.935378-28.176736 62.935378-62.934355L576.077899 455.269951l210.836893 210.834846c12.288884 12.289907 28.395724 18.434861 44.500517 18.434861 16.10684 0 32.212656-6.144954 44.500517-18.434861 24.580838-24.579815 24.580838-64.426335 0-89.005127L557.654294 258.83814z" p-id="58738" fill="#ffffff"></path></svg>
        </i>
        <span>顶部</span>
    </a>
</div>


<script  language="javascript">
    function toTop() {
        T.startMoveScrollTop(3,0 );
    }
</script>
<script>
    $(function(){
       /* $.ajax({
            url: "//www.ttyingqiu.com/const/config",
            type: "GET",
            dataType: "jsonp",
            success: function (data) {
                if(data.isSuccess && data.promotion){
                    if($("#kf_phone").length>0){
                        var _tel=data.promotion.tel;
                        $("#kf_phone").text("客服电话：(" + _tel.substr(0, 4) + ") " + _tel.substr(4,8));
                    }
                    if($("div.goFixedNew div.kfTxt img").length>0){
                        $("div.goFixedNew div.kfTxt img").attr("src",data.promotion.qrCode)
                    }
                }
            }
        });*/

        var agcodeId = null;
        if((id = getQueryString())!=null){//优先获取url上的
            agcodeId = id;
        }else if((id = getCookieId())!=null){//url没有就在cookie里获取，都没有就使用默认
            agcodeId = id;
        }
        if(agcodeId == '2335373'){
            $("#ttyq_dl_qr_img").attr("src","https://www.ttyingqiu.com/resources/images/QRCode/2335373.png");
        }
        if(agcodeId == '2335123'){
            $("#ttyq_dl_qr_img").attr("src","https://r.ttyingqiu.com/r/images/web/QRCode/2335123.png?v=20250613001");
        }
        if(agcodeId == '2335053'){
            $("#ttyq_dl_qr_img").attr("src","https://r.ttyingqiu.com/r/images/web/QRCode/2335053.png?v=20250613001");
        }

        //获取url上的渠道号
        function getQueryString()
        {
            var reg = new RegExp("(^|&)"+ "agentId" +"=([^&]*)(&|$)");
            var r = window.location.search.substr(1).match(reg);
            if(r!=null)return  unescape(r[2]); return null;
        }
        //获取cookie里的渠道号
        function getCookieId(){
            var arr,reg=new RegExp("(^|)"+"NAGENTID"+"=([^;]*)(;|$)");
            if(arr = document.cookie.match(reg)){
                return unescape(arr[2]);
            }else{
                return null;
            }
        }

        if(window.location.href.indexOf("ttyingqiu.com/topic/2016/download")!=-1){
            $(".jq_downBtn").hide();
        }
        if(window.location.host.indexOf(".ttyingqiu.com")!=-1){
            $(".ttzs_dl_qr").hide();
        }

        //新版返回顶部侧栏二维码
        $(".jq_downBtn").click(function(){
            var _this = this;
            var fixedEwm = $(".jq_fixedEwm");
            if(fixedEwm.hasClass("animate")){
                fixedEwm.removeClass("animate");
                $(_this).removeClass("active");
            }else{
                fixedEwm.addClass("animate");
                $(_this).addClass("active");
            }
        })

        //客服时间
        $(".jq_kf").hover(function(){
            var _this = this;
            $(_this).addClass("hover");
        },function(){
            $(this).removeClass("hover");
        })
        /*反馈按钮*/
        goFeedBack = function () {
            checkLogin(function (data) {
                window.location.href = "/feedback";
            },function (data) {
                loadLogin();
            })
        }

        function checkLogin(success, fail) {
            $.get("/ajaxCheckLogin").done(function (data) {
                var result = $.parseJSON(data);
                if (result.success) {
                    $("#hasNotLogin").hide();
                    $("#hasLogin").show();
                    $("#userIcon").attr("src", result.member.icon);
                    $("#userName").html(result.member.nickName);
                    if (!result.member.phone) {
                        $("#bindPhone").show();
                    }
                    if (result.member.passwordSet == 0) {
                        $("#setPassword").show();
                    }
                    if (typeof (success) != "undefined") {
                        success(result.member)
                    }
                }else{
                    if (typeof (fail) != "undefined") {
                        fail(result)
                    }
                }
            }).fail(function (e) {
                if (typeof (fail) != "undefined") {
                    fail($.parseJSON(e.responseText))
                }
            })
        }

        function loadLogin(callbackFuc) {
            $.post("/ajaxAddLoginCode", {});

            function checkScriptExist(url) {
                try {
                    var host = window.location.protocol + "//" + window.location.host;
                    if (url.indexOf("http") == -1) {
                        url = host + url
                    }
                    var scripts = window.document.getElementsByTagName("script");
                    if (scripts && scripts.length > 0) {
                        for (var key in scripts) {
                            if (scripts[key] && scripts[key].src && scripts[key].src == url) {
                                return true
                            }
                        }
                    }
                } catch (e) {
                    return false
                }
                return false
            }

            function loadScript(url, callback) {
                if (checkScriptExist(url)) {
                    callback();
                    return
                }
                var script = document.createElement("script");
                script.type = "text/javascript";
                if (typeof (callback) != "undefined") {
                    if (script.readyState) {
                        script.onreadystatechange = function () {
                            if (script.readyState == "loaded" || script.readyState == "complete") {
                                script.onreadystatechange = null;
                                callback()
                            }
                        }
                    } else {
                        script.onload = function () {
                            callback()
                        }
                    }
                }
                script.src = url;
                document.body.appendChild(script)
            }
            
            loadScript("https://r.ttyingqiu.com/r/js/??common/login/jsencrypt-rsa.min.js", function () {
                loadScript("https://r.ttyingqiu.com/r/js/??common/login/webdialog.js", function () {
                    $("body").append("<div id='loginDialog'></div>");
                    $("#loginDialog").load("/resources/login.html", function () {
                        loadScript("https://r.ttyingqiu.com/r/js/??common/login/login.js?v=20250613001", function () {
                            openLogin(callbackFuc);
                            $("#accountRegister").bind("input", function (event) {
                                $.post("/ajaxChangeLoginPCode", {})
                            });
                            $("#checkCodeRegister").bind("click input", function (event) {
                                $.post("/ajaxAddRegisterCode", {})
                            })
                        })
                    })
                })
            })
        }


    })
</script>










<script type="text/javascript" src="https://r.ttyingqiu.com/r/js/??common/web/footer.js,common/web/QRCode.js?v=20250613001"></script>

<script>
	$(function () {
		// 隐藏管家二维码
		/*if (checkHiddenQrcode()){
            if($("#kfTxt_qrcode").length>0){
                $("#kfTxt_qrcode").hide();
                $("#kfTxt_phone").css('padding-top','6px');
            }
        }*/

		$.ajax({
			url: "//www.ttyingqiu.com/const/config",
			type: "GET",
			dataType: "jsonp",
			success: function (data) {
				if (data.isSuccess && data.promotion) {
					var _tel = data.promotion.tel;
					if($("#kf_header").length > 0){
						$("#kf_header").text("(" + _tel.substr(0, 4) + ") " + _tel.substr(4,8));
					}
					if ($("#kfTxt_phone").length > 0) {
						$("#kfTxt_phone").text("(" + _tel.substr(0, 4) + ") " + _tel.substr(4,8));
					}
					if ($("div.butler img").length > 0) {
						$("div.butler img").attr("src", data.promotion.qrCode)
					}
					if ($("div.wxSlideWrap img").length > 0) {
						$("div.wxSlideWrap img").attr("src", data.promotion.qrCode)
					}
					if($("#kf_phone").length>0){
						$("#kf_phone").text("客服电话：(" + _tel.substr(0, 4) + ") " + _tel.substr(4,8));
					}
					if($("div.goFixedNew div.kfTxt img").length>0){
						$("div.goFixedNew div.kfTxt img").attr("src",data.promotion.qrCode)
					}
					if($("#digit-help_phone").length>0){
						$("#digit-help_phone").text(_tel.substr(0, 4) + "-" + _tel.substr(4,8));
					}
					
				}
			}
		});
	})
/*	var aiFlag = window.location.href;
	if(aiFlag != null &&(aiFlag.toLowerCase().indexOf("kaijiang")==-1 && aiFlag.toLowerCase().indexOf("kjgg")==-1
		&& aiFlag.toLowerCase().indexOf("zst")==-1 && aiFlag.toLowerCase().indexOf("download")==-1)){*/
		var isAicai = false;
		var isNewDomain = false;
		
		if(window.location.href.toLowerCase().indexOf("ddyingqiu.com")!= -1) {
			isNewDomain = true;
		}
	/*var isAicai = ;
	if(isAicai===undefined)
	    isAicai = false;
	var isNewDomain = ;
	if(isNewDomain===undefined)
		isNewDomain = false;*/
	
	if(!isAicai&&location.pathname.indexOf("/api")!=0){
		var _hmt = _hmt || [];
		(function() {
		  var hm = document.createElement("script");
		  //hm.src = "https://hm.baidu.com/hm.js?043ef5794d6d2a7417b5d62962bb792f";
		   if(isNewDomain){
			   hm.src = "https://hm.baidu.com/hm.js?63640ff0e387e229cc68cd589bbe6ea4";
		   }else{
			   hm.src = "https://hm.baidu.com/hm.js?f081063fc7e101407949a8005a9b3e56";
		   }
		  var s = document.getElementsByTagName("script")[0]; 
		  s.parentNode.insertBefore(hm, s);
		})();
	}
	//}
	var host = window.location.host;
	if (host === "www.ddyingqiu.com"){
        $("#links").css("display","block");
		$("#footer").addClass("mt30");
	}

</script>
<!-- <script src="http://s11.cnzz.com/z_stat.php?id=1261104076&web_id=1261104076" language="JavaScript"></script> -->

	

	


<script  type="text/javascript">
	$(function (){
		checkUUID();
		// var firstStart = window.sessionStorage.getItem('firstStart');
		var firstStart = getCookieValByLogin('firstStart');

		if(!firstStart) {
			getDataList();
		}
	})

	function getDataList() {
		/*var platform = 'web';
		var host = location.host;
		if(host.indexOf("ttzoushi")!=-1) {
			platform = 'ttzsweb'
		}*/

		var host = location.host;
		var toUrl = '//www.ttyingqiu.com/web/start';
		if(host.indexOf("ttzoushi")!=-1) {
			toUrl = '//www.ttzoushi.com/web/start'
		}else if(host.indexOf("yingti666")!=-1){
			toUrl = '//www.yingti666.com/web/start'
		}

		$.ajax({
			type: 'GET',
			url: toUrl,
			// data:'platform='+platform,
			dataType: 'jsonp',
			success: function (data) {
				// var result = JSON.parse(data);
				if(data.success) {
					// console.log("firstStart");
					// window.sessionStorage.setItem('firstStart','true');
					var _host = location.host.substring(location.host.indexOf("."));
					
					document.cookie = 'firstStart' + "=" + encodeURIComponent('true') + "; path=" + "/" + "; domain=" + _host ;
				}
			}
		})
	}

	function getCookieValByLogin(name) {
		var cookieArr = document.cookie.replace(/\s/g, "").split(';');
		for ( var i = 0; i < cookieArr.length; i++) {
			var tempObj = cookieArr[i].split('=');
			if (tempObj[0] == name)
				return decodeURIComponent(tempObj[1]);
		}
		return null;
	}

	function setCookieByLogin (name, value, expires) {
		var _host = window.location.host;
		_host = _host.substring(location.host.indexOf("."));
		if (typeof (expires) == 'undefiend' || expires == null || expires == '') {
			document.cookie = name + "=" + encodeURIComponent(value) + "; path=" + "/" + "; domain=" + _host ;
		} else {
			var expTimes = expires * 1000;
			var expDate = new Date();
			expDate.setTime(expDate.getTime() + expTimes);
			document.cookie = name + "=" + encodeURIComponent(value)
					+ ";expires=" + expDate.toGMTString() + "; path=" + "/"
					+ "; domain=" + _host ;
		}
	}

	function getUUID(){
		return 'VUID'+new Date().getTime()+""+Math.ceil(Math.random()*(999999-100000)+100000);
	}

	function checkUUID(){
		var uuid = getCookieValByLogin('VUID');
		if(typeof (uuid) == "undefined" || uuid == "" || typeof (uuid)!= "string" || uuid == null){
			uuid = getUUID();
			setCookieByLogin('VUID',uuid,365*24*60*60);
		}
	}
</script>



<div style="display:none;"><a href="http://www.anquan.org/s/www.aicai.com" name="TVzzKcc7nwgD3j8mVeXjd4OTn9gCbykv9oHbybkacKRgApQDEe" >安全联盟</a></div>

</body>
<script>

   /* var button = document.getElementById("backButton");
    var s = 5;
    function task(time){
        setTimeout(()=>{
            button.innerText = time+"秒后自动返回首页";
            if(time--<=0){
                location.href = "/";
            }else{
                task(time);
            }
        },1000);
    }
    task(s);*/




</script>
</html>

//根据Cookie获取用户登录信息
var jieqiUserInfo = {
    jieqiUserId: 0,
    jieqiUserName: '',
    jieqiUserPassword: '',
    jieqiUserToken: '',
    jieqiUserGroup: 0,
    jieqiNewMessage: 0,
    jieqiCodeLogin: 0,
    jieqiCodePost: 0
};
if (document.cookie.indexOf('jieqiUserInfo') >= 0) {
    var cinfo = Cookie.get('jieqiUserInfo');
    start = 0;
    offset = cinfo.indexOf(',', start);
    while (offset > 0) {
        tmpval = cinfo.substring(start, offset);
        tmpidx = tmpval.indexOf('=');
        if (tmpidx > 0) {
            tmpname = tmpval.substring(0, tmpidx);
            tmpval = tmpval.substring(tmpidx + 1, tmpval.length);
            if (jieqiUserInfo.hasOwnProperty(tmpname)) jieqiUserInfo[tmpname] = tmpval;
        }
        start = offset + 1;
        if (offset < cinfo.length) {
            offset = cinfo.indexOf(',', start);
            if (offset == -1) offset = cinfo.length;
        } else {
            offset = -1;
        }
    }
}


//是否允许点击翻页
var usePageMode = ('columnWidth' in document.documentElement.style || 'MozColumnWidth' in document.documentElement.style || 'WebkitColumnWidth' in document.documentElement.style || 'OColumnWidth' in document.documentElement.style || 'msColumnWidth' in document.documentElement.style) ? true : false;

//显示阅读工具
var ReadTools = {
    // 添加 defaultColorid 属性
    defaultColorid: parseInt(Storage.get('read_colorid')) || 0, // 默认的背景色ID
    bgcolor: ['#f1f1f1', '#232323', '#ebe5d8', '#dfd2ab', '#d3e2d1', '#d1dcdd', '#ead2d1', '#d3d3d1'],
    fontcolor: ['#49423a', '#9e9e9e', '#49423a', '#333333', '#49423a', '#49423a', '#49423a', '#49423a'],
    bgname: ['白', '夜', '旧', '护', '青', '蓝', '粉', '灰'],
    fontsize: ['0.875em', '1em', '1.125em', '1.25em', '1.5em', '1.75em', '2em'],
    fontname: ['小号', '中号', '大号', '较大', '超大'],
    pagemode: [0, 1],
    pagemname: ['上下滑动', '左右翻页'],
    tipegold: [20, 50, 100, 200, 500, 1000],
    colorid: 0,
    fontid: 2,
    pagemid: 0,
    ttimer: null,
    tiptime: 3000,
    contentid: 'ccacontent',
    pageid: 'aread',
    showtools: false,

    CallTools: function () {
        if (ReadTools.showtools) {
            ReadTools.CallHide();
        } else {
            document.getElementById('toptools').style.display = '';
            document.getElementById('bottomtools').style.display = '';
            ReadTools.showtools = true;
        }
    },
    CallShow: function (id) {
        ReadTools.CallHide(1);
        document.getElementById(id).style.display = '';
    },
    CallHide: function () {
        if (!arguments[0]) {
            document.getElementById('toptools').style.display = 'none';
            document.getElementById('bottomtools').style.display = 'none';
            ReadTools.showtools = false;
        }
        document.getElementById('readset').style.display = 'none';
        document.getElementById('givetip').style.display = 'none';
        document.getElementById('readtip').style.display = 'none';
        document.getElementById('addreview').style.display = 'none';
    },
    ContentClick: function () {
        if (ReadTools.pagemid == 0) {
            ReadTools.CallTools();
        }
    },
    ShowTip: function (str) {
        document.getElementById('readtip').innerHTML = str;
        ReadTools.CallHide(1);
        ReadTools.CallShow('readtip');
        ReadTools.TipTimeout();
    },
    TipTimeout: function () {
        if (ReadTools.ttimer) clearTimeout(ReadTools.ttimer);
        ReadTools.ttimer = setTimeout(function () {
            if (document.getElementById('readtip').style.display == '') {
                ReadTools.CallHide(1);
            }
        }, ReadTools.tiptime);
    },
    SetColor: function (id) {
        document.getElementById(ReadTools.pageid).style.backgroundColor = ReadTools.bgcolor[id];
        document.getElementById(ReadTools.pageid).style.color = ReadTools.fontcolor[id];
        if (ReadTools.colorid != id) Storage.set('read_colorid', id);
        ReadTools.colorid = id;

        var lis = document.getElementById('fontcolor').getElementsByTagName('li');
        for (i = 0; i < lis.length; i++) {
            if (id == i) lis[i].className = 'selected';
            else lis[i].className = '';
        }
    },
    SetFont: function (id) {
        document.getElementById(ReadTools.contentid).style.fontSize = ReadTools.fontsize[id];
        if (ReadTools.fontid != id) Storage.set('read_fontid', id);
        ReadTools.fontid = id;
        /*
        var lis = document.getElementById('fontsize').getElementsByTagName('li');
        for (i = 0; i < lis.length; i++) {
          if (id == i) lis[i].className = 'selected';
          else lis[i].className = '';
        }
        */
        if (usePageMode && ReadTools.pagemid == 1) ReadPages.MakePages();
    },
    FontSmall: function () {
        if (ReadTools.fontid > 0) {
            ReadTools.SetFont(ReadTools.fontid - 1);
        }
    },
    FontBig: function () {
        if (ReadTools.fontid < ReadTools.fontsize.length - 1) {
            ReadTools.SetFont(ReadTools.fontid + 1);
        }
    },
    SetPagem: function (id) {
        if (usePageMode && ReadTools.pagemid != id) {
            if (ReadTools.pagemid != id) Storage.set('read_pagemid', id);
            ReadTools.pagemid = id;
            var lis = document.getElementById('pagemode').getElementsByTagName('li');
            for (i = 0; i < lis.length; i++) {
                if (id == i) lis[i].className = 'selected';
                else lis[i].className = '';
            }
            if (ReadTools.pagemid == 1) {
                ReadPages.MakePages();

                // 隐藏id=pinglun的元素
                var pinglunElement = document.getElementById('pinglun');
                if (pinglunElement) {
                    pinglunElement.style.display = 'none';
                }
            } else {
                ReadPages.RestorePages();

                // 恢复id=pinglun的元素
                var pinglunElement = document.getElementById('pinglun');
                if (pinglunElement) {
                    pinglunElement.style.display = '';
                }
            }
            ReadTools.CallHide();
        }
    },
    ahToggle: function () {
        if (localStorage.getItem('禁用章评') === null) {
            localStorage.setItem('禁用章评', 'true')
            location.reload()
        } else {
            localStorage.removeItem('禁用章评')
            location.reload()
        }
    },
    AddBookcase: function () {
        if (jieqiUserInfo.jieqiUserId) {
            Ajax.Request('/modules/article/addbookcase.php?bid=' + ReadParams.articleid + '&cid=' + ReadParams.chapterid + '&pid=' + ReadParams.page, {
                method: 'POST',
                onComplete: function () {
                    ReadTools.ShowTip(this.response);
                }
            });
        } else {
            var jumpurl = window.location.href.indexOf('?') > -1 ? window.location.href + '&before_act=addbookcase' : window.location.href + '?before_act=addbookcase';
            ReadTools.ShowLogin(jumpurl);
        }
    },
    UserVote: function () {
        if (jieqiUserInfo.jieqiUserId) {
            Ajax.Request('/modules/article/uservote.php?id=' + ReadParams.articleid, {
                method: 'POST', onComplete: function () {
                    ReadTools.ShowTip(this.response);
                }
            });
        } else {
            var jumpurl = window.location.href.indexOf('?') > -1 ? window.location.href + '&before_act=uservote' : window.location.href + '?before_act=uservote';
            ReadTools.ShowLogin(jumpurl);
        }
    },
    GiveTip: function (egold) {
        if (jieqiUserInfo.jieqiUserId) {
            Ajax.Request('/modules/article/tip.php', {
                method: 'POST',
                parameters: 'act=post&id=' + ReadParams.articleid + '&payegold=' + parseInt(egold) + '&jieqi_token=' + jieqiUserInfo.jieqiUserToken,
                onComplete: function () {
                    ReadTools.ShowTip(this.response);
                }
            });
        } else {
            var jumpurl = window.location.href.indexOf('?') > -1 ? window.location.href + '&before_act=givetip' : window.location.href + '?before_act=givetip';
            ReadTools.ShowLogin(jumpurl);
        }
    },
    Show: function () {
        var output = '';
        var isdisplay = ReadTools.showtools ? '' : 'none';

        output += '<div id="toptools" class="toptools cf" style="display:' + isdisplay + ';">\
		<a href="javascript: window.location.href = ReadParams.url_articleinfo;" class="iconfont fl">&#xee69;</a>\
		<a href="javascript: window.location.href = ReadParams.url_home;" class="iconfont fr">&#xee27;</a>\
		<a href="javascript: ReadTools.CallShow(\'readset\');" class="iconfont fr">&#xee26;</a>\
		<!--<a href="javascript: ReadTools.CallShow(\'givetip\');" class="iconfont fr">&#xee42;</a>-->\
		<a href="/bookcase.php" class="iconfont fr">&#xee43;</a>\
		<a href="javascript: ReadTools.AddBookcase();" class="iconfont fr">&#xee53;</a>\
		<!--<a href="javascript: ReadTools.CallShow(\'addreview\');" class="iconfont fr">&#xee3a;</a>-->\
		<!--<a href="javascript: ReadTools.UserVote();" class="iconfont fr">&#xee5d;</a>-->\
</div>';

        output += '<div id="bottomtools" class="bottomtools cf" style="display:' + isdisplay + ';">\
    <script>anra();</script>\
		<div class="hairline-bottom"><ul>\
	<li onclick="window.location.href = ReadParams.url_previous;"><p class="iconfont f_l">&#xee68;</p><p>上一页</p></li>\
	<li onclick="window.location.href = ReadParams.url_index;"><p class="iconfont f_l">&#xee32;</p><p>目录</p></li>\
	<li onclick="window.location.href = ReadParams.url_articleinfo;"><p class="iconfont f_l">&#xee50;</p><p>书页</p></li>\
	<li onclick="window.location.href = ReadParams.url_next;"><p class="iconfont f_l">&#xee67;</p><p>下一页</p></li>\
	</ul></div>\
</div>';

        output += '<div id="readset" class="readset" style="display:none;">\
				<div class="setblock"><p>背景</p>\
                <ul id="fontcolor" class="fontcolor cf">';
        for (i = 0; i < this.bgcolor.length; i++) {
            output += ' <li';
            if (this.colorid == i) output += ' class="selected"';
            output += ' style="background: ' + this.bgcolor[i] + ';color: ' + this.fontcolor[i] + '" onclick="ReadTools.SetColor(' + i + ')">' + this.bgname[i] + '</li>';
        }
        output += '</ul></div>\
				<div class="setblock"><p>字体</p>\
                <ul id="fontsize" class="fontsize cf">';
        output += ' <li onclick="ReadTools.FontSmall()">缩小字体</li>\
                <li onclick="ReadTools.FontBig()">放大字体</li>';
        /*
        for (i = 0; i < this.fontsize.length; i++) {
          output += ' <li';
          if (this.fontid == i) output += ' class="selected"';
          output += ' onclick="ReadTools.SetFont(' + i + ')">' + this.fontname[i] + '</li>';
        }
        */
        if (usePageMode) {
            output += '</ul></div>\
				<div class="setblock"><p>翻页</p>\
                <ul id="pagemode" class="pagemode cf">';
            for (i = 0; i < this.pagemode.length; i++) {
                output += ' <li';
                if (this.pagemid == i) output += ' class="selected"';
                output += ' onclick="ReadTools.SetPagem(' + i + ')">' + this.pagemname[i] + '</li>';
            }
        }
        //添加章评开关
        output += '</ul></div>\
				<div class="setblock"><p>章评</p><ul id="nameless" class="cf">\
				<li onclick="ReadTools.ahToggle()">开启</li><li onclick="ReadTools.ahToggle()">关闭</li>'
        output += '</ul></div>\
        </div>';
        output += '<div id="addreview" class="addreview" style="display:none;"><form name="frmreview" id="frmreview" method="post" action="/modules/article/reviews.php?aid=' + ReadParams.articleid + '">\
<div><textarea class="textarea" name="pcontent" id="pcontent" placeholder="书评感想" style="font-family:Verdana;font-size:16px;width:94%;height:4.5em;margin:0 auto 0.3em auto;"></textarea></div>';
        //if (jieqiUserInfo.jieqiCodePost) output += '<div style="margin-bottom: 0.3em;text-align: left;text-indent: 3%;">验证码：<input type="text" class="text" size="8" maxlength="8" name="checkcode" onfocus="if($_(\'p_imgccode\').style.display == \'none\'){$_(\'p_imgccode\').src = \'/checkcode.php\';$_(\'p_imgccode\').style.display = \'\';}" title="点击显示验证码"><img id="p_imgccode" src="" style="cursor:pointer;vertical-align:middle;margin-left:3px;display:none;" onclick="this.src=\'/checkcode.php?rand=\'+Math.random();" title="点击刷新验证码"></div>';
        output += '<input type="button" name="Submit" class="button" value="发表书评" style="cursor:pointer;" onclick="Ajax.Request(\'frmreview\',{onComplete:function(){ReadTools.ShowTip(this.response);}});">\
<input type="hidden" name="act" id="act" value="newpost" />\
</form></div>';
        output += '<div id="givetip" class="givetip" style="display:none;">\
        <dl>\
        <dt>请选择打赏金额</dt>';
        for (i = 0; i < this.tipegold.length; i++) {
            output += ' <dd onclick="ReadTools.GiveTip(' + this.tipegold[i] + ')">' + this.tipegold[i] + ' 币</dd>';
        }
        output += '</dl>\
        </div>';
        output += '<div id="readtip" class="readtip" style="display:none;">\
        </div>';
        document.write(output);
    },
    SaveSet: function () {
        Storage.set('read_colorid', ReadTools.colorid);
        Storage.set('read_fontid', ReadTools.fontid);
        Storage.set('read_pagemid', ReadTools.pagemid);
    },
    LoadSet: function () {
        var id = 0;

        id = this.defaultColorid;
        if (id >= 0 && id < this.bgcolor.length) this.SetColor(id);

        id = parseInt(Storage.get('read_colorid'));
        if (id >= 0 && id < this.bgcolor.length) this.SetColor(id);


        id = parseInt(Storage.get('read_fontid'));
        if (id >= 0 && id < this.fontsize.length) this.SetFont(id);

        id = parseInt(Storage.get('read_pagemid'));
        if (id >= 0 && id < this.pagemode.length) this.SetPagem(id);

        //给章评开关添加selected类
        var nameless = document.getElementById('nameless')
        if (localStorage.getItem('禁用章评') === null) {
            nameless.children[0].className = 'selected'
        } else {
            nameless.children[1].className = 'selected'
        }
    },
    ShowLogin: function (jumpurl) {
        ReadTools.ShowTip('请点击 <a class="fsl fwb" href="/login.php?jumpurl=' + encodeURIComponent(jumpurl) + '">登录</a> 后使用本功能！');
    },
    GetQueryString: function (name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return unescape(r[2]);
        return null;
    },
    DoBefore: function () {
        var before_act = ReadTools.GetQueryString('before_act');
        switch (before_act) {
            case 'addbookcase':
                ReadTools.CallTools();
                ReadTools.ShowTip('登录成功，请重新点击收藏！');
                break;
            case 'uservote':
                ReadTools.CallTools();
                ReadTools.ShowTip('登录成功，请重新点击推荐！');
                break;
            case 'givetip':
                ReadTools.CallTools();
                ReadTools.ShowTip('登录成功，请重新点击打赏！');
                break;
        }
    }
};

//显示翻页
var ReadPages = {
    totalPages: 0, //总页数
    currentPage: 0, //当前页码
    pageWidth: 0, //页宽
    pageHeight: 0, //页高
    pageGapX: 0,//左右边距
    pageGapY: 20,//上下边距
    hideTip: -1, //是否显示单页提示

    PageClick: function () {
        if (ReadTools.pagemid == 1) {
            var e = window.event ? window.event : getEvent();
            if (e.clientX < ReadPages.pageWidth * 0.333) ReadPages.ShowPage('previous');
            else if (e.clientX > ReadPages.pageWidth * 0.666) ReadPages.ShowPage('next');
            else ReadTools.CallTools();
        }
    },
    RestorePages: function () {
        var footlink = $_('footlink');
        if (footlink) footlink.setStyle('display', '');

        var abox = $_('abox');
        abox.setStyle('overflow', '');
        abox.setStyle('margin', '');
        abox.setStyle('width', '');
        abox.setStyle('height', '');

        var apage = $_('apage');
        apage.setStyle('position', '');
        apage.setStyle('height', '');
        apage.setStyle('columnWidth', '', true);
        apage.setStyle('columnGap', '', true);

        var toptext = $_('toptext');
        toptext.setStyle('display', 'none');

        var bottomtext = $_('bottomtext');
        bottomtext.setStyle('display', 'none');
    },
    MakePages: function () {
        if (usePageMode && ReadTools.pagemid == 1) {
            ReadPages.pageWidth = document.documentElement.clientWidth; //页宽
            ReadPages.pageHeight = document.documentElement.clientHeight; //页高

            var footlink = $_('footlink');
            if (footlink) footlink.setStyle('display', 'none');

            var abox = $_('abox');
            abox.setStyle('overflow', 'hidden');
            abox.setStyle('margin', ReadPages.pageGapY + 'px ' + ReadPages.pageGapX + 'px');
            abox.setStyle('width', (ReadPages.pageWidth - ReadPages.pageGapX * 2) + 'px');
            abox.setStyle('height', (ReadPages.pageHeight - ReadPages.pageGapY * 2) + 'px');

            var apage = $_('apage');
            apage.setStyle('position', 'relative');
            apage.setStyle('height', (ReadPages.pageHeight - ReadPages.pageGapY * 2) + 'px');
            apage.setStyle('columnWidth', (ReadPages.pageWidth - ReadPages.pageGapX * 2) + 'px', true);
            apage.setStyle('columnGap', '0', true);

            var pagecount = Math.ceil(apage.scrollWidth / apage.clientWidth);

            if (ReadPages.totalPages != pagecount) {
                if (ReadPages.currentPage > 1) ReadPages.currentPage = Math.floor(pagecount * ReadPages.currentPage / ReadPages.totalPages);
                ReadPages.totalPages = pagecount;
            }
            if (window.location.href.indexOf('#lastPage') > -1 && ReadPages.currentPage == 0) ReadPages.currentPage = ReadPages.totalPages;
            if (ReadPages.currentPage < 1) ReadPages.currentPage = 1;
            if (ReadPages.currentPage > ReadPages.totalPages) ReadPages.currentPage = ReadPages.totalPages;

            ReadPages.ShowPage();

            //显示翻页提示
            if (ReadPages.hideTip < 0) {
                ReadPages.hideTip = parseInt(Storage.get('read_hidetip'));
                if (ReadPages.hideTip != 1) {
                    $_('operatetip').style.display = '';
                    Storage.set('read_hidetip', '1');
                }
            }
        }
    },
    ShowPage: function () {
        if (arguments[0]) {
            if (arguments[0] == 'next') {
                ReadPages.currentPage++;
                if (ReadPages.currentPage > ReadPages.totalPages) {
                    document.location.href = ReadParams.url_next;
                    return true;
                }
            } else if (arguments[0] == 'previous') {
                ReadPages.currentPage--;
                if (ReadPages.currentPage < 1) {
                    document.location.href = ReadParams.url_previous + '#lastPage';
                    return true;
                }
            }
        }
        // Recalculate the total number of pages
        var pagecount = Math.ceil(apage.scrollWidth / apage.clientWidth);
        if (ReadPages.totalPages != pagecount) {
            if (ReadPages.currentPage > 1) ReadPages.currentPage = Math.floor(pagecount * ReadPages.currentPage / ReadPages.totalPages);
            ReadPages.totalPages = pagecount;
        }

        if (ReadPages.currentPage < 1) ReadPages.currentPage = 1;
        if (ReadPages.currentPage > ReadPages.totalPages) ReadPages.currentPage = ReadPages.totalPages;

        if (ReadPages.currentPage == 1) apage.setStyle('left', '0');
        else apage.setStyle('left', '-' + ((ReadPages.currentPage - 1) * (ReadPages.pageWidth - ReadPages.pageGapX * 2)) + 'px');


        var toptext = $_('toptext');
        if (ReadPages.currentPage > 1) {
            toptext.innerHTML = $_('atitle').innerHTML;
            toptext.setStyle('display', '');
        } else {
            toptext.setStyle('display', 'none');
        }

        var bottomtext = $_('bottomtext');
        bottomtext.textContent = ReadPages.currentPage + '/' + ReadPages.totalPages;
        bottomtext.setStyle('display', '');
        // Trigger the lazybeforeunveil event
        var event = new CustomEvent("lazybeforeunveil", {detail: {}});
        window.dispatchEvent(event);
    }
}

// 在页面加载时设置背景色
window.onload = function () {
    document.getElementById(ReadTools.pageid).style.backgroundColor = ReadTools.bgcolor[ReadTools.defaultColorid];
    ReadPages.MakePages();
};

ReadTools.Show();
ReadTools.LoadSet();
ReadTools.DoBefore();

addEvent(window, 'load', ReadPages.MakePages);
addEvent(window, 'resize', ReadPages.MakePages);
document.getElementById(ReadTools.pageid).onclick = ReadPages.PageClick;
document.getElementById(ReadTools.contentid).onclick = ReadTools.ContentClick;


//禁止选择复制
document.oncontextmenu = function () {
    return false;
};
document.ondragstart = function () {
    return false;
};
document.onselectstart = function () {
    return false;
};
document.onbeforecopy = function () {
    return false;
};
document.onselect = function () {
    window.getSelection ? window.getSelection().empty() : document.selection.empty();
};
document.oncopy = function () {
    window.getSelection ? window.getSelection().empty() : document.selection.empty();
};

function anra() {
    var ua = navigator.userAgent
    if (ua.indexOf('BiliNovel') === -1 && ua.indexOf('Android') > -1) {
        document.writeln(
            "<div class='hairlie-top'><div><img alt='哔哩轻小说 客户端' src='/logo.png'></div><div class='fx-f1'><p>安装哔哩轻小说客户端</p><p>获得更好的阅读体验</p></div><div><a class='btn-primary-small' href='https://cdn.a.ln.yodu.app#chapter'>点击下载</a></div></div><style>.hairlie-top{display:flex;}.hairlie-top>div:first-child{padding:10px 10px 0 10px;}.hairlie-top>div:first-child img{width:40px;height:40px;}.fx-f1{-webkit-box-flex:1;box-flex:1;-webkit-flex:1;flex:1;padding-top:10px;}.hairlie-top>div:nth-child(2) p:last-child{font-size:12px;opacity:.6;}.hairlie-top>div:last-child{padding:10px 10px 0 10px;}.btn-primary-small{display:inline-block;line-height:2.25rem;padding-left:2ch;padding-right:2ch;background-color:#ff3955;color:#fff;font-size:.875rem;border-radius:99px;text-align:center;}</style>"
        );
    }
}

//把2个英文空格换成1个全角空格
//addEvent(window, 'load', function(){document.getElementById('acontent').innerHTML = document.getElementById('acontent').innerHTML.replace(/&nbsp;&nbsp;/g, '&emsp;');});

var fOvlc1 = window["\x64\x6f\x63\x75\x6d\x65\x6e\x74"]['\x67\x65\x74\x45\x6c\x65\x6d\x65\x6e\x74\x42\x79\x49\x64']('\x63\x63\x61\x63\x6f\x6e\x74\x65\x6e\x74')['\x69\x6e\x6e\x65\x72\x48\x54\x4d\x4c'];
fOvlc1 = fOvlc1['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]('\u201c', "\x67\x69"), "\u300c")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]('\u201d', "\x67\x69"), "\u300d")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]('\u2018', "\x67\x69"), "\u300e")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]('\u2019', "\x67\x69"), "\u300f")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue82c", "\x67\x69"), "\u7684")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue852", "\x67\x69"), "\u4e00")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue82d", "\x67\x69"), "\u662f")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue819", "\x67\x69"), "\u4e86")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue856", "\x67\x69"), "\u6211")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue857", "\x67\x69"), "\u4e0d")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue816", "\x67\x69"), "\u4eba")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue83c", "\x67\x69"), "\u5728")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue830", "\x67\x69"), "\u4ed6")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue82e", "\x67\x69"), "\u6709")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue836", "\x67\x69"), "\u8fd9")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue859", "\x67\x69"), "\u4e2a")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue80a", "\x67\x69"), "\u4e0a")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue855", "\x67\x69"), "\u4eec")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue842", "\x67\x69"), "\u6765")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue858", "\x67\x69"), "\u5230")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue80b", "\x67\x69"), "\u65f6")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue81f", "\x67\x69"), "\u5927")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue84a", "\x67\x69"), "\u5730")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue853", "\x67\x69"), "\u4e3a")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue81e", "\x67\x69"), "\u5b50")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue822", "\x67\x69"), "\u4e2d")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue813", "\x67\x69"), "\u4f60")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue85b", "\x67\x69"), "\u8bf4")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue807", "\x67\x69"), "\u751f")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue818", "\x67\x69"), "\u56fd")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue810", "\x67\x69"), "\u5e74")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue812", "\x67\x69"), "\u7740")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue851", "\x67\x69"), "\u5c31")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue801", "\x67\x69"), "\u90a3")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue80c", "\x67\x69"), "\u548c")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue815", "\x67\x69"), "\u8981")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue84c", "\x67\x69"), "\u5979")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue840", "\x67\x69"), "\u51fa")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue848", "\x67\x69"), "\u4e5f")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue835", "\x67\x69"), "\u5f97")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue800", "\x67\x69"), "\u91cc")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue826", "\x67\x69"), "\u540e")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue863", "\x67\x69"), "\u81ea")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue861", "\x67\x69"), "\u4ee5")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue854", "\x67\x69"), "\u4f1a")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue827", "\x67\x69"), "\u5bb6")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue83b", "\x67\x69"), "\u53ef")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue85d", "\x67\x69"), "\u4e0b")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue84d", "\x67\x69"), "\u800c")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue862", "\x67\x69"), "\u8fc7")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue81c", "\x67\x69"), "\u5929")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue81d", "\x67\x69"), "\u53bb")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue860", "\x67\x69"), "\u80fd")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue843", "\x67\x69"), "\u5bf9")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue82f", "\x67\x69"), "\u5c0f")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue802", "\x67\x69"), "\u591a")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue831", "\x67\x69"), "\u7136")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue84b", "\x67\x69"), "\u4e8e")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue837", "\x67\x69"), "\u5fc3")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue829", "\x67\x69"), "\u5b66")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue85e", "\x67\x69"), "\u4e48")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue83a", "\x67\x69"), "\u4e4b")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue832", "\x67\x69"), "\u90fd")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue808", "\x67\x69"), "\u597d")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue841", "\x67\x69"), "\u770b")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue821", "\x67\x69"), "\u8d77")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue845", "\x67\x69"), "\u53d1")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue803", "\x67\x69"), "\u5f53")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue828", "\x67\x69"), "\u6ca1")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue81b", "\x67\x69"), "\u6210")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue83e", "\x67\x69"), "\u53ea")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue820", "\x67\x69"), "\u5982")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue84e", "\x67\x69"), "\u4e8b")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue85a", "\x67\x69"), "\u628a")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue806", "\x67\x69"), "\u8fd8")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue83f", "\x67\x69"), "\u7528")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue833", "\x67\x69"), "\u7b2c")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue811", "\x67\x69"), "\u6837")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue804", "\x67\x69"), "\u9053")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue814", "\x67\x69"), "\u60f3")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue80f", "\x67\x69"), "\u4f5c")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue84f", "\x67\x69"), "\u79cd")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue80e", "\x67\x69"), "\u5f00")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue823", "\x67\x69"), "\u7f8e")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue849", "\x67\x69"), "\u4e73")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue805", "\x67\x69"), "\u9634")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue809", "\x67\x69"), "\u6db2")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue81a", "\x67\x69"), "\u830e")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue844", "\x67\x69"), "\u6b32")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue847", "\x67\x69"), "\u547b")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue850", "\x67\x69"), "\u8089")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue824", "\x67\x69"), "\u4ea4")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue85f", "\x67\x69"), "\u6027")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue817", "\x67\x69"), "\u80f8")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue85c", "\x67\x69"), "\u79c1")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue838", "\x67\x69"), "\u7a74")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue82a", "\x67\x69"), "\u6deb")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue83d", "\x67\x69"), "\u81c0")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue82b", "\x67\x69"), "\u8214")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue80d", "\x67\x69"), "\u5c04")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue839", "\x67\x69"), "\u8131")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue834", "\x67\x69"), "\u88f8")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue846", "\x67\x69"), "\u9a9a")['\x72\x65\x70\x6c\x61\x63\x65'](new window["\x52\x65\x67\x45\x78\x70"]("\ue825", "\x67\x69"), "\u5507");
window["\x64\x6f\x63\x75\x6d\x65\x6e\x74"]['\x67\x65\x74\x45\x6c\x65\x6d\x65\x6e\x74\x42\x79\x49\x64']('\x63\x63\x61\x63\x6f\x6e\x74\x65\x6e\x74')['\x69\x6e\x6e\x65\x72\x48\x54\x4d\x4c'] = fOvlc1;
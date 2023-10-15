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
            if (jieqiUserInfo.hasOwnProperty(tmpname))
                jieqiUserInfo[tmpname] = tmpval;
        }
        start = offset + 1;
        if (offset < cinfo.length) {
            offset = cinfo.indexOf(',', start);
            if (offset == -1)
                offset = cinfo.length;
        } else {
            offset = -1;
        }
    }
}

//是否允许点击翻页
var usePageMode = ('columnWidth'in document.documentElement.style || 'MozColumnWidth'in document.documentElement.style || 'WebkitColumnWidth'in document.documentElement.style || 'OColumnWidth'in document.documentElement.style || 'msColumnWidth'in document.documentElement.style) ? true : false;

//显示阅读工具
var ReadTools = {
    // 添加 defaultColorid 属性
    defaultColorid: parseInt(Storage.get('read_colorid')) || 0,
    // 默认的背景色ID
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
    contentid: 'acontent',
    pageid: 'aread',
    showtools: false,

    CallTools: function() {
        if (ReadTools.showtools) {
            ReadTools.CallHide();
        } else {
            document.getElementById('toptools').style.display = '';
            document.getElementById('bottomtools').style.display = '';
            ReadTools.showtools = true;
        }
    },
    CallShow: function(id) {
        ReadTools.CallHide(1);
        document.getElementById(id).style.display = '';
    },
    CallHide: function() {
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
    ContentClick: function() {
        if (ReadTools.pagemid == 0) {
            ReadTools.CallTools();
        }
    },
    ShowTip: function(str) {
        document.getElementById('readtip').innerHTML = str;
        ReadTools.CallHide(1);
        ReadTools.CallShow('readtip');
        ReadTools.TipTimeout();
    },
    TipTimeout: function() {
        if (ReadTools.ttimer)
            clearTimeout(ReadTools.ttimer);
        ReadTools.ttimer = setTimeout(function() {
            if (document.getElementById('readtip').style.display == '') {
                ReadTools.CallHide(1);
            }
        }, ReadTools.tiptime);
    },
    SetColor: function(id) {
        document.getElementById(ReadTools.pageid).style.backgroundColor = ReadTools.bgcolor[id];
        document.getElementById(ReadTools.pageid).style.color = ReadTools.fontcolor[id];
        if (ReadTools.colorid != id)
            Storage.set('read_colorid', id);
        ReadTools.colorid = id;

        var lis = document.getElementById('fontcolor').getElementsByTagName('li');
        for (i = 0; i < lis.length; i++) {
            if (id == i)
                lis[i].className = 'selected';
            else
                lis[i].className = '';
        }
    },
    SetFont: function(id) {
        document.getElementById(ReadTools.contentid).style.fontSize = ReadTools.fontsize[id];
        if (ReadTools.fontid != id)
            Storage.set('read_fontid', id);
        ReadTools.fontid = id;
        /*
    var lis = document.getElementById('fontsize').getElementsByTagName('li');
    for (i = 0; i < lis.length; i++) {
      if (id == i) lis[i].className = 'selected';
      else lis[i].className = '';
    }
    */
        if (usePageMode && ReadTools.pagemid == 1)
            ReadPages.MakePages();
    },
    FontSmall: function() {
        if (ReadTools.fontid > 0) {
            ReadTools.SetFont(ReadTools.fontid - 1);
        }
    },
    FontBig: function() {
        if (ReadTools.fontid < ReadTools.fontsize.length - 1) {
            ReadTools.SetFont(ReadTools.fontid + 1);
        }
    },
    SetPagem: function(id) {
        if (usePageMode && ReadTools.pagemid != id) {
            if (ReadTools.pagemid != id)
                Storage.set('read_pagemid', id);
            ReadTools.pagemid = id;
            var lis = document.getElementById('pagemode').getElementsByTagName('li');
            for (i = 0; i < lis.length; i++) {
                if (id == i)
                    lis[i].className = 'selected';
                else
                    lis[i].className = '';
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

    ahToggle: function() {
        if (localStorage.getItem('禁用章评') === null) {
            localStorage.setItem('禁用章评', 'true')
            location.reload()
        } else {
            localStorage.removeItem('禁用章评')
            location.reload()
        }
    },
    AddBookcase: function() {
        if (jieqiUserInfo.jieqiUserId) {
            Ajax.Request('/modules/article/addbookcase.php?bid=' + ReadParams.articleid + '&cid=' + ReadParams.chapterid + '&pid=' + ReadParams.page, {
                method: 'POST',
                onComplete: function() {
                    ReadTools.ShowTip(this.response);
                }
            });
        } else {
            var jumpurl = window.location.href.indexOf('?') > -1 ? window.location.href + '&before_act=addbookcase' : window.location.href + '?before_act=addbookcase';
            ReadTools.ShowLogin(jumpurl);
        }
    },
    UserVote: function() {
        if (jieqiUserInfo.jieqiUserId) {
            Ajax.Request('/modules/article/uservote.php?id=' + ReadParams.articleid, {
                method: 'POST',
                onComplete: function() {
                    ReadTools.ShowTip(this.response);
                }
            });
        } else {
            var jumpurl = window.location.href.indexOf('?') > -1 ? window.location.href + '&before_act=uservote' : window.location.href + '?before_act=uservote';
            ReadTools.ShowLogin(jumpurl);
        }
    },
    GiveTip: function(egold) {
        if (jieqiUserInfo.jieqiUserId) {
            Ajax.Request('/modules/article/tip.php', {
                method: 'POST',
                parameters: 'act=post&id=' + ReadParams.articleid + '&payegold=' + parseInt(egold) + '&jieqi_token=' + jieqiUserInfo.jieqiUserToken,
                onComplete: function() {
                    ReadTools.ShowTip(this.response);
                }
            });
        } else {
            var jumpurl = window.location.href.indexOf('?') > -1 ? window.location.href + '&before_act=givetip' : window.location.href + '?before_act=givetip';
            ReadTools.ShowLogin(jumpurl);
        }
    },
    Show: function() {
        var output = '';
        var isdisplay = ReadTools.showtools ? '' : 'none';

        output += '<div id="toptools" class="toptools cf" style="display:' + isdisplay + ';">\
		<a href="javascript: window.location.href = ReadParams.url_articleinfo;" class="iconfont fl">&#xee69;</a>\
		<a href="javascript: window.location.href = ReadParams.url_home;" class="iconfont fr">&#xee27;</a>\
		<a href="javascript: ReadTools.CallShow(\'readset\');" class="iconfont fr">&#xee26;</a>\
		<!--<a href="javascript: ReadTools.CallShow(\'givetip\');" class="iconfont fr">&#xee42;</a>-->\
		<a href="javascript: ReadTools.AddBookcase();" class="iconfont fr">&#xee60;</a>\
		<!--<a href="javascript: ReadTools.CallShow(\'addreview\');" class="iconfont fr">&#xee3a;</a>-->\
		<!--<a href="javascript: ReadTools.UserVote();" class="iconfont fr">&#xee5d;</a>-->\
</div>';

        output += '<div id="bottomtools" class="bottomtools cf" style="display:' + isdisplay + ';">\
		<ul>\
	<li onclick="window.location.href = ReadParams.url_previous;"><p class="iconfont f_l">&#xee68;</p><p>上一页</p></li>\
	<li onclick="window.location.href = ReadParams.url_index;"><p class="iconfont f_l">&#xee32;</p><p>目录</p></li>\
	<li onclick="window.location.href = ReadParams.url_articleinfo;"><p class="iconfont f_l">&#xee50;</p><p>书页</p></li>\
	<li onclick="window.location.href = ReadParams.url_next;"><p class="iconfont f_l">&#xee67;</p><p>下一页</p></li>\
	</ul>\
</div>';

        output += '<div id="readset" class="readset" style="display:none;">\
				<div class="setblock"><p>背景</p>\
                <ul id="fontcolor" class="fontcolor cf">';
        for (i = 0; i < this.bgcolor.length; i++) {
            output += ' <li';
            if (this.colorid == i)
                output += ' class="selected"';
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
                if (this.pagemid == i)
                    output += ' class="selected"';
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
    SaveSet: function() {
        Storage.set('read_colorid', ReadTools.colorid);
        Storage.set('read_fontid', ReadTools.fontid);
        Storage.set('read_pagemid', ReadTools.pagemid);
    },
    LoadSet: function() {
        var id = 0;

        id = this.defaultColorid;
        if (id >= 0 && id < this.bgcolor.length)
            this.SetColor(id);

        id = parseInt(Storage.get('read_colorid'));
        if (id >= 0 && id < this.bgcolor.length)
            this.SetColor(id);

        id = parseInt(Storage.get('read_fontid'));
        if (id >= 0 && id < this.fontsize.length)
            this.SetFont(id);

        id = parseInt(Storage.get('read_pagemid'));
        if (id >= 0 && id < this.pagemode.length)
            this.SetPagem(id);

        //给章评开关添加selected类
        var nameless = document.getElementById('nameless')
        if (localStorage.getItem('禁用章评') === null) {
            nameless.children[0].className = 'selected'
        } else {
            nameless.children[1].className = 'selected'
        }
    },
    ShowLogin: function(jumpurl) {
        ReadTools.ShowTip('请点击 <a class="fsl fwb" href="/login.php?jumpurl=' + encodeURIComponent(jumpurl) + '">登录</a> 后使用本功能！');
    },
    GetQueryString: function(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
        var r = window.location.search.substr(1).match(reg);
        if (r != null)
            return unescape(r[2]);
        return null;
    },
    DoBefore: function() {
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
    totalPages: 0,
    //总页数
    currentPage: 0,
    //当前页码
    pageWidth: 0,
    //页宽
    pageHeight: 0,
    //页高
    pageGapX: 0,
    //左右边距
    pageGapY: 20,
    //上下边距
    hideTip: -1,
    //是否显示单页提示

    PageClick: function() {
        if (ReadTools.pagemid == 1) {
            var e = window.event ? window.event : getEvent();
            if (e.clientX < ReadPages.pageWidth * 0.333)
                ReadPages.ShowPage('previous');
            else if (e.clientX > ReadPages.pageWidth * 0.666)
                ReadPages.ShowPage('next');
            else
                ReadTools.CallTools();
        }
    },
    RestorePages: function() {
        var footlink = $_('footlink');
        if (footlink)
            footlink.setStyle('display', '');

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
    MakePages: function() {
        if (usePageMode && ReadTools.pagemid == 1) {
            ReadPages.pageWidth = document.documentElement.clientWidth;
            //页宽
            ReadPages.pageHeight = document.documentElement.clientHeight;
            //页高

            var footlink = $_('footlink');
            if (footlink)
                footlink.setStyle('display', 'none');

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
                if (ReadPages.currentPage > 1)
                    ReadPages.currentPage = Math.floor(pagecount * ReadPages.currentPage / ReadPages.totalPages);
                ReadPages.totalPages = pagecount;
            }
            if (window.location.href.indexOf('#lastPage') > -1 && ReadPages.currentPage == 0)
                ReadPages.currentPage = ReadPages.totalPages;
            if (ReadPages.currentPage < 1)
                ReadPages.currentPage = 1;
            if (ReadPages.currentPage > ReadPages.totalPages)
                ReadPages.currentPage = ReadPages.totalPages;

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
    ShowPage: function() {
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
            if (ReadPages.currentPage > 1)
                ReadPages.currentPage = Math.floor(pagecount * ReadPages.currentPage / ReadPages.totalPages);
            ReadPages.totalPages = pagecount;
        }

        if (ReadPages.currentPage < 1)
            ReadPages.currentPage = 1;
        if (ReadPages.currentPage > ReadPages.totalPages)
            ReadPages.currentPage = ReadPages.totalPages;

        if (ReadPages.currentPage == 1)
            apage.setStyle('left', '0');
        else
            apage.setStyle('left', '-' + ((ReadPages.currentPage - 1) * (ReadPages.pageWidth - ReadPages.pageGapX * 2)) + 'px');

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
        var event = new CustomEvent("lazybeforeunveil",{
            detail: {}
        });
        window.dispatchEvent(event);
    }
}

// 在页面加载时设置背景色
window.onload = function() {
    document.getElementById(ReadTools.pageid).style.backgroundColor = ReadTools.bgcolor[ReadTools.defaultColorid];
    ReadPages.MakePages();
}
;

ReadTools.Show();
ReadTools.LoadSet();
ReadTools.DoBefore();

addEvent(window, 'load', ReadPages.MakePages);
addEvent(window, 'resize', ReadPages.MakePages);
document.getElementById(ReadTools.pageid).onclick = ReadPages.PageClick;
document.getElementById(ReadTools.contentid).onclick = ReadTools.ContentClick;

//禁止选择复制
document.oncontextmenu = function() {
    return false;
}
;
document.ondragstart = function() {
    return false;
}
;
document.onselectstart = function() {
    return false;
}
;
document.onbeforecopy = function() {
    return false;
}
;
document.onselect = function() {
    window.getSelection ? window.getSelection().empty() : document.selection.empty();
}
;
document.oncopy = function() {
    window.getSelection ? window.getSelection().empty() : document.selection.empty();
}
;

//把2个英文空格换成1个全角空格
//addEvent(window, 'load', function(){document.getElementById('acontent').innerHTML = document.getElementById('acontent').innerHTML.replace(/&nbsp;&nbsp;/g, '&emsp;');});

eval(function(p, a, c, k, e, d) {
    e = function(c) {
        return (c < a ? "" : e(parseInt(c / a))) + ((c = c % a) > 35 ? String.fromCharCode(c + 29) : c.toString(36))
    }
    ;
    if (!''.replace(/^/, String)) {
        while (c--)
            d[e(c)] = k[c] || e(c);
        k = [function(e) {
            return d[e]
        }
        ];
        e = function() {
            return '\\w+'
        }
        ;
        c = 1;
    }
    ;while (c--)
        if (k[c])
            p = p.replace(new RegExp('\\b' + e(c) + '\\b','g'), k[c]);
    return p;
}('1y h=7.5(\'6\').4;h=h.3(2 1(\'“\',"0"),"「").3(2 1(\'”\',"0"),"」").3(2 1(\'‘\',"0"),"『").3(2 1(\'’\',"0"),"』").3(2 1("","0"),"\\G").3(2 1("","0"),"\\F").3(2 1("","0"),"\\E").3(2 1("","0"),"\\J").3(2 1("","0"),"\\I").3(2 1("","0"),"\\H").3(2 1("","0"),"\\A").3(2 1("","0"),"\\z").3(2 1("","0"),"\\y").3(2 1("","0"),"\\D").3(2 1("","0"),"\\C").3(2 1("","0"),"\\B").3(2 1("","0"),"\\K").3(2 1("","0"),"\\T").3(2 1("","0"),"\\S").3(2 1("","0"),"\\R").3(2 1("","0"),"\\W").3(2 1("","0"),"\\V").3(2 1("","0"),"\\U").3(2 1("","0"),"\\N").3(2 1("","0"),"\\M").3(2 1("","0"),"\\L").3(2 1("","0"),"\\Q").3(2 1("","0"),"\\P").3(2 1("","0"),"\\O").3(2 1("","0"),"\\f").3(2 1("","0"),"\\g").3(2 1("","0"),"\\e").3(2 1("","0"),"\\k").3(2 1("","0"),"\\j").3(2 1("","0"),"\\i").3(2 1("","0"),"\\a").3(2 1("","0"),"\\9").3(2 1("","0"),"\\8").3(2 1("","0"),"\\d").3(2 1("","0"),"\\c").3(2 1("","0"),"\\b").3(2 1("","0"),"\\l").3(2 1("","0"),"\\u").3(2 1("","0"),"\\t").3(2 1("","0"),"\\s").3(2 1("","0"),"\\x").3(2 1("","0"),"\\w").3(2 1("","0"),"\\v").3(2 1("","0"),"\\o").3(2 1("","0"),"\\n").3(2 1("","0"),"\\m").3(2 1("","0"),"\\r").3(2 1("","0"),"\\q").3(2 1("","0"),"\\p").3(2 1("","0"),"\\X").3(2 1("","0"),"\\1v").3(2 1("","0"),"\\1u").3(2 1("","0"),"\\1t").3(2 1("","0"),"\\1e").3(2 1("","0"),"\\1x").3(2 1("","0"),"\\1w").3(2 1("","0"),"\\1p").3(2 1("","0"),"\\1o").3(2 1("","0"),"\\1n").3(2 1("","0"),"\\1s").3(2 1("","0"),"\\1r").3(2 1("","0"),"\\1q").3(2 1("","0"),"\\1z").3(2 1("","0"),"\\1I").3(2 1("","0"),"\\1H").3(2 1("","0"),"\\1G").3(2 1("","0"),"\\1L").3(2 1("","0"),"\\1K").3(2 1("","0"),"\\1J").3(2 1("","0"),"\\1C").3(2 1("","0"),"\\1B").3(2 1("","0"),"\\1A").3(2 1("","0"),"\\1F").3(2 1("","0"),"\\1E").3(2 1("","0"),"\\1D").3(2 1("","0"),"\\16").3(2 1("","0"),"\\15").3(2 1("","0"),"\\14").3(2 1("","0"),"\\19").3(2 1("","0"),"\\18").3(2 1("","0"),"\\17").3(2 1("","0"),"\\10").3(2 1("","0"),"\\Z").3(2 1("","0"),"\\Y").3(2 1("","0"),"\\13").3(2 1("","0"),"\\12").3(2 1("","0"),"\\11").3(2 1("","0"),"\\1a").3(2 1("","0"),"\\1j").3(2 1("","0"),"\\1i").3(2 1("","0"),"\\1h").3(2 1("","0"),"\\1m").3(2 1("","0"),"\\1l").3(2 1("","0"),"\\1k").3(2 1("","0"),"\\1d").3(2 1("","0"),"\\1c").3(2 1("","0"),"\\1b").3(2 1("","0"),"\\1g").3(2 1("","0"),"\\1f");7.5(\'6\').4=h;', 62, 110, 'gi|RegExp|new|replace|innerHTML|getElementById|acontent|document|u51fa|u5979|u8981|u91cc|u5f97|u4e5f|u7740|u56fd|u5e74||u548c|u90a3|u5c31|u540e|u5929|u8fc7|u800c|u5bf9|u80fd|u53bb|u4f1a|u4ee5|u81ea|u4e0b|u53ef|u5bb6|u4ed6|u5728|u4eba|u4e2a|u8fd9|u6709|u662f|u4e00|u7684|u4e0d|u6211|u4e86|u4e0a|u4e2d|u5b50|u4e3a|u751f|u8bf4|u4f60|u5230|u6765|u4eec|u5730|u5927|u65f6|u5c0f|u6b32|u830e|u6db2|u4ea4|u8089|u547b|u5f00|u79cd|u4f5c|u9634|u4e73|u7f8e|u6027|u88f8|u8131|u5c04|u5fc3|u5507|u9a9a|u7a74|u79c1|u80f8|u8214|u81c0|u6deb|u597d|u90fd|u4e4b|u53d1|u8d77|u770b|u4e8e|u7136|u591a|u4e48|u5b66|var|u5f53|u7b2c|u7528|u8fd8|u60f3|u9053|u6837|u53ea|u6210|u6ca1|u628a|u4e8b|u5982'.split('|'), 0, {}))

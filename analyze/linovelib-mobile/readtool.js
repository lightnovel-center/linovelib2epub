//鏍规嵁Cookie鑾峰彇鐢ㄦ埛鐧诲綍淇℃伅
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



//鏄惁鍏佽鐐瑰嚮缈婚〉
var usePageMode = ('columnWidth' in document.documentElement.style || 'MozColumnWidth' in document.documentElement.style || 'WebkitColumnWidth' in document.documentElement.style || 'OColumnWidth' in document.documentElement.style || 'msColumnWidth' in document.documentElement.style) ? false : false;

//鏄剧ず闃呰宸ュ叿
var ReadTools = {
  // 娣诲姞 defaultColorid 灞炴€�
  defaultColorid: parseInt(Storage.get('read_colorid')) || 0, // 榛樿鐨勮儗鏅壊ID
  bgcolor: ['#f1f1f1', '#232323', '#ebe5d8', '#dfd2ab', '#d3e2d1', '#d1dcdd', '#ead2d1', '#d3d3d1'],
  fontcolor: ['#49423a', '#9e9e9e', '#49423a', '#333333', '#49423a', '#49423a', '#49423a', '#49423a'],
  bgname: ['鐧�', '澶�', '鏃�', '鎶�', '闈�', '钃�', '绮�', '鐏�'],
  fontsize: ['0.875em', '1em', '1.125em', '1.25em', '1.5em', '1.75em', '2em'],
  fontname: ['灏忓彿', '涓彿', '澶у彿', '杈冨ぇ', '瓒呭ぇ'],
  pagemode: [0, 1],
  pagemname: ['涓婁笅婊戝姩', '宸﹀彸缈婚〉'],
  tipegold: [20, 50, 100, 200, 500, 1000],
  colorid: 0,
  fontid: 2,
  pagemid: 0,
  ttimer: null,
  tiptime: 3000,
  contentid: 'acontentz',
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
    if (usePageMode && ReadTools.pagemid != id){
      if (ReadTools.pagemid != id) Storage.set('read_pagemid', id);
      ReadTools.pagemid = id;
      var lis = document.getElementById('pagemode').getElementsByTagName('li');
      for (i = 0; i < lis.length; i++) {
        if (id == i) lis[i].className = 'selected';
        else lis[i].className = '';
      }
      if (ReadTools.pagemid == 1) {
        ReadPages.MakePages();

        // 闅愯棌id=pinglun鐨勫厓绱�
        var pinglunElement = document.getElementById('pinglun');
        if (pinglunElement) {
          pinglunElement.style.display = 'none';
        }
      }
      else {
        ReadPages.RestorePages();

        // 鎭㈠id=pinglun鐨勫厓绱�
        var pinglunElement = document.getElementById('pinglun');
        if (pinglunElement) {
          pinglunElement.style.display = '';
        }
      }
      ReadTools.CallHide();
    }
  },
  ahToggle: function (){
    if(localStorage.getItem('绂佺敤绔犺瘎') === null){
      localStorage.setItem('绂佺敤绔犺瘎','true')
      location.reload()
    }else{
      localStorage.removeItem('绂佺敤绔犺瘎')
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
	<li onclick="window.location.href = ReadParams.url_previous;"><p class="iconfont f_l">&#xee68;</p><p>涓婁竴椤�</p></li>\
	<li onclick="window.location.href = ReadParams.url_index;"><p class="iconfont f_l">&#xee32;</p><p>鐩綍</p></li>\
	<li onclick="window.location.href = ReadParams.url_articleinfo;"><p class="iconfont f_l">&#xee50;</p><p>涔﹂〉</p></li>\
	<li onclick="window.location.href = ReadParams.url_next;"><p class="iconfont f_l">&#xee67;</p><p>涓嬩竴椤�</p></li>\
	</ul></div>\
</div>';

    output += '<div id="readset" class="readset" style="display:none;">\
				<div class="setblock"><p>鑳屾櫙</p>\
                <ul id="fontcolor" class="fontcolor cf">';
    for (i = 0; i < this.bgcolor.length; i++) {
      output += ' <li';
      if (this.colorid == i) output += ' class="selected"';
      output += ' style="background: ' + this.bgcolor[i] + ';color: ' + this.fontcolor[i] + '" onclick="ReadTools.SetColor(' + i + ')">' + this.bgname[i] + '</li>';
    }
    output += '</ul></div>\
				<div class="setblock"><p>瀛椾綋</p>\
                <ul id="fontsize" class="fontsize cf">';
    output += ' <li onclick="ReadTools.FontSmall()">缂╁皬瀛椾綋</li>\
                <li onclick="ReadTools.FontBig()">鏀惧ぇ瀛椾綋</li>';
    /*
    for (i = 0; i < this.fontsize.length; i++) {
      output += ' <li';
      if (this.fontid == i) output += ' class="selected"';
      output += ' onclick="ReadTools.SetFont(' + i + ')">' + this.fontname[i] + '</li>';
    }
    */
    if(usePageMode) {
      output += '</ul></div>\
				<div class="setblock"><p>缈婚〉</p>\
                <ul id="pagemode" class="pagemode cf">';
      for (i = 0; i < this.pagemode.length; i++) {
        output += ' <li';
        if (this.pagemid == i) output += ' class="selected"';
        output += ' onclick="ReadTools.SetPagem(' + i + ')">' + this.pagemname[i] + '</li>';
      }
    }
    //娣诲姞绔犺瘎寮€鍏�
    output += '</ul></div>\
				<div class="setblock"><p>绔犺瘎</p><ul id="nameless" class="cf">\
				<li onclick="ReadTools.ahToggle()">寮€鍚�</li><li onclick="ReadTools.ahToggle()">鍏抽棴</li>'
    output += '</ul></div>\
        </div>';
    output += '<div id="addreview" class="addreview" style="display:none;"><form name="frmreview" id="frmreview" method="post" action="/modules/article/reviews.php?aid=' + ReadParams.articleid + '">\
<div><textarea class="textarea" name="pcontent" id="pcontent" placeholder="涔﹁瘎鎰熸兂" style="font-family:Verdana;font-size:16px;width:94%;height:4.5em;margin:0 auto 0.3em auto;"></textarea></div>';
    //if (jieqiUserInfo.jieqiCodePost) output += '<div style="margin-bottom: 0.3em;text-align: left;text-indent: 3%;">楠岃瘉鐮侊細<input type="text" class="text" size="8" maxlength="8" name="checkcode" onfocus="if($_(\'p_imgccode\').style.display == \'none\'){$_(\'p_imgccode\').src = \'/checkcode.php\';$_(\'p_imgccode\').style.display = \'\';}" title="鐐瑰嚮鏄剧ず楠岃瘉鐮�"><img id="p_imgccode" src="" style="cursor:pointer;vertical-align:middle;margin-left:3px;display:none;" onclick="this.src=\'/checkcode.php?rand=\'+Math.random();" title="鐐瑰嚮鍒锋柊楠岃瘉鐮�"></div>';
    output += '<input type="button" name="Submit" class="button" value="鍙戣〃涔﹁瘎" style="cursor:pointer;" onclick="Ajax.Request(\'frmreview\',{onComplete:function(){ReadTools.ShowTip(this.response);}});">\
<input type="hidden" name="act" id="act" value="newpost" />\
</form></div>';
    output += '<div id="givetip" class="givetip" style="display:none;">\
        <dl>\
        <dt>璇烽€夋嫨鎵撹祻閲戦</dt>';
    for (i = 0; i < this.tipegold.length; i++) {
      output += ' <dd onclick="ReadTools.GiveTip(' + this.tipegold[i] + ')">' + this.tipegold[i] + ' 甯�</dd>';
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
    if (id >= 0 && id < this.pagemode.length)  this.SetPagem(id);

    //缁欑珷璇勫紑鍏虫坊鍔爏elected绫�
    var nameless=document.getElementById('nameless')
    if(localStorage.getItem('绂佺敤绔犺瘎') === null){
      nameless.children[0].className='selected'
    }else{
      nameless.children[1].className='selected'
    }
  },
  ShowLogin: function (jumpurl) {
    ReadTools.ShowTip('璇风偣鍑� <a class="fsl fwb" href="/login.php?jumpurl=' + encodeURIComponent(jumpurl) + '">鐧诲綍</a> 鍚庝娇鐢ㄦ湰鍔熻兘锛�');
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
        ReadTools.ShowTip('鐧诲綍鎴愬姛锛岃閲嶆柊鐐瑰嚮鏀惰棌锛�');
        break;
      case 'uservote':
        ReadTools.CallTools();
        ReadTools.ShowTip('鐧诲綍鎴愬姛锛岃閲嶆柊鐐瑰嚮鎺ㄨ崘锛�');
        break;
      case 'givetip':
        ReadTools.CallTools();
        ReadTools.ShowTip('鐧诲綍鎴愬姛锛岃閲嶆柊鐐瑰嚮鎵撹祻锛�');
        break;
    }
  }
};

//鏄剧ず缈婚〉
var ReadPages = {
  totalPages: 0, //鎬婚〉鏁�
  currentPage: 0, //褰撳墠椤电爜
  pageWidth: 0, //椤靛
  pageHeight: 0, //椤甸珮
  pageGapX: 0,//宸﹀彸杈硅窛
  pageGapY: 20,//涓婁笅杈硅窛
  hideTip: -1, //鏄惁鏄剧ず鍗曢〉鎻愮ず

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
      ReadPages.pageWidth = document.documentElement.clientWidth; //椤靛
      ReadPages.pageHeight = document.documentElement.clientHeight; //椤甸珮

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

      //鏄剧ず缈婚〉鎻愮ず
      if(ReadPages.hideTip < 0){
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
    var event = new CustomEvent("lazybeforeunveil", { detail: {} });
    window.dispatchEvent(event);
  }
}

// 鍦ㄩ〉闈㈠姞杞芥椂璁剧疆鑳屾櫙鑹�
window.onload = function() {
  document.getElementById(ReadTools.pageid).style.backgroundColor = ReadTools.bgcolor[ReadTools.defaultColorid];
  ReadPages.MakePages();
};

ReadTools.Show();
ReadTools.LoadSet();
ReadTools.DoBefore();

addEvent(window, 'load', ReadPages.MakePages);
addEvent(window, 'resize', ReadPages.MakePages);
document.getElementById(ReadTools.pageid).onclick = ReadPages.PageClick;
document.getElementById(ReadTools.contentid).onclick =  ReadTools.ContentClick;

/*
//绂佹閫夋嫨澶嶅埗
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
  var ua=navigator.userAgent
  if (ua.indexOf('BiliNovel')===-1 && ua.indexOf('Android') > -1) {
    document.writeln(
      "<div class='hairlie-top'><div><img alt='鍝斿摡杞诲皬璇� 瀹㈡埛绔�' src='/logo.png'></div><div class='fx-f1'><p>瀹夎鍝斿摡杞诲皬璇村鎴风</p><p>鑾峰緱鏇村ソ鐨勯槄璇讳綋楠�</p></div><div><a class='btn-primary-small' href='https://cdn.a.ln.yodu.app#chapter'>鐐瑰嚮涓嬭浇</a></div></div><style>.hairlie-top{display:flex;}.hairlie-top>div:first-child{padding:10px 10px 0 10px;}.hairlie-top>div:first-child img{width:40px;height:40px;}.fx-f1{-webkit-box-flex:1;box-flex:1;-webkit-flex:1;flex:1;padding-top:10px;}.hairlie-top>div:nth-child(2) p:last-child{font-size:12px;opacity:.6;}.hairlie-top>div:last-child{padding:10px 10px 0 10px;}.btn-primary-small{display:inline-block;line-height:2.25rem;padding-left:2ch;padding-right:2ch;background-color:#ff3955;color:#fff;font-size:.875rem;border-radius:99px;text-align:center;}</style>"
    );
  }
}
*/
//鎶�2涓嫳鏂囩┖鏍兼崲鎴�1涓叏瑙掔┖鏍�
//addEvent(window, 'load', function(){document.getElementById('acontent').innerHTML = document.getElementById('acontent').innerHTML.replace(/&nbsp;&nbsp;/g, '&emsp;');});

['jsjiami.com.v4']["\x66\x69\x6c\x74\x65\x72"]["\x63\x6f\x6e\x73\x74\x72\x75\x63\x74\x6f\x72"](((['jsjiami.v4']+[])["\x63\x6f\x6e\x73\x74\x72\x75\x63\x74\x6f\x72"]['\x66\x72\x6f\x6d\x43\x68\x61\x72\x43\x6f\x64\x65']['\x61\x70\x70\x6c\x79'](null,"118J97H114I32P104P61t100n111Q99r117W109z101r110R116r46g103b101e116Z69D108R101A109r101l110H116Q66a121j73p100C40i39a97O99V111g110I116V101j110N116F122E39w41Q46X105j110y110S101t114G72d84E77G76L59s104t61M104a46O114p101s112B108N97y99U101N40u110Y101t119b32L82E101B103W69n120m112h40L39M8220C39v44d34Z103a105q34n41X44B34l12300s34g41x46a114f101N112Z108Z97N99k101N40c110q101h119w32Y82L101a103C69u120d112Q40H39i8221J39S44N34R103G105e34u41C44q34U12301D34C41g46s114Y101O112S108i97H99x101X40j110t101j119m32G82F101y103u69v120i112G40I39J8216Z39K44E34v103m105z34q41t44O34z12302E34D41q46w114W101H112k108p97b99n101x40L110s101U119Z32d82e101p103E69I120m112w40j39A8217w39h44X34f103Z105p34n41f44O34a12303L34E41N46k114h101v112R108V97v99Y101c40U110n101n119k32o82j101h103r69N120C112P40d34Q59398a34T44I32h34f103D105k34G41K44u32S34y30340d34v41X46A114a101a112K108E97H99i101A40Q110n101q119Q32m82o101j103O69C120a112q40D34F59425A34F44Q32X34i103Q105a34Q41l44u32j34k19968H34G41v46w114g101k112Z108K97F99K101S40d110d101u119R32z82Y101t103k69Z120T112u40H34k59460Y34P44h32J34N103j105f34R41N44M32d34e26159a34a41f46i114Q101I112Y108P97P99l101G40k110i101K119O32X82r101T103C69N120o112b40L34a59400Y34G44y32h34j103b105u34t41Y44k32O34g20102R34b41l46I114r101V112n108K97B99Z101z40P110u101Z119Y32o82I101h103I69b120k112w40q34G59473M34e44J32r34N103u105o34U41f44z32K34H25105W34r41L46D114p101F112X108t97V99q101q40Z110B101s119l32d82f101L103P69W120P112J40g34z59449e34i44f32R34a103o105K34L41I44N32e34n19981E34I41u46q114J101Q112J108e97n99y101Z40A110z101A119f32l82r101Z103P69g120W112u40x34C59482Q34D44X32M34i103L105W34n41v44H32a34x20154D34z41B46g114j101L112A108H97O99n101K40U110m101Q119b32n82Z101R103X69Y120K112n40c34e59452i34r44D32c34w103Z105M34n41d44j32y34a22312J34b41H46G114a101b112S108P97z99h101Z40j110C101y119c32O82J101x103T69j120q112x40k34N59448J34H44H32b34W103i105b34H41T44L32X34I20182m34h41n46s114o101E112j108B97e99z101H40t110b101z119L32q82l101u103O69B120v112G40q34p59414E34m44N32e34d103c105y34s41k44n32j34v26377s34O41c46j114G101u112W108r97x99s101q40l110T101T119I32p82k101q103N69c120t112e40T34j59418c34i44d32t34q103j105I34H41I44P32v34O36825x34P41m46h114m101i112d108v97c99R101H40q110j101i119K32x82j101w103B69L120F112b40H34a59393N34c44c32j34w103A105I34D41k44p32y34Z20010t34O41o46Q114S101O112i108p97n99t101f40Z110J101B119R32l82V101s103i69I120s112d40a34j59466W34W44Z32e34U103D105k34J41K44y32d34I19978F34t41E46A114v101f112h108w97G99K101b40x110z101t119h32d82l101B103S69E120W112R40N34e59429m34W44h32i34F103V105q34F41A44c32f34v20204n34C41c46j114D101J112o108s97e99L101f40d110U101y119H32N82R101w103B69b120T112S40n34b59402R34f44o32f34r103J105g34O41L44k32J34g26469d34e41A46Q114I101h112K108I97K99E101I40z110p101n119h32h82z101b103a69k120w112i40X34h59451A34M44J32n34F103C105y34L41j44O32Q34K21040G34j41B46t114d101W112l108D97k99O101v40e110e101x119w32q82a101q103t69g120Z112j40r34y59450s34d44W32K34d103N105J34E41k44O32w34m26102K34x41o46U114s101O112M108M97s99M101r40B110m101B119T32N82s101m103i69w120W112k40o34j59428q34z44Z32s34W103h105D34Y41h44k32L34L22823M34f41U46I114M101M112K108S97N99V101Y40o110x101o119O32E82Y101Y103I69d120L112A40z34N59417L34c44O32i34n103Y105M34f41M44p32k34G22320M34R41y46Z114T101q112n108N97N99q101H40v110X101m119i32m82h101P103m69j120c112N40M34b59435y34d44y32H34k103M105d34v41d44y32d34z20026I34O41h46X114v101y112s108e97m99c101o40y110W101I119T32z82V101h103I69Q120D112Z40A34N59447j34M44M32p34n103Z105M34C41G44w32G34L23376C34M41A46X114G101j112T108g97s99q101C40i110x101v119I32K82V101x103X69E120c112t40a34r59446V34p44X32Y34z103b105C34S41w44s32N34a20013S34t41r46u114E101W112x108J97M99b101j40W110U101t119G32S82H101j103d69P120H112z40F34u59432J34m44p32j34T103Z105k34R41V44k32g34V20320f34C41r46J114m101a112o108K97h99O101I40o110f101x119s32G82c101T103g69t120Z112f40W34I59462R34l44j32Y34T103p105G34S41I44i32n34d35828c34x41o46r114Q101R112c108d97C99U101y40J110v101M119l32r82v101R103G69q120c112Y40d34g59419Q34k44F32F34I103a105W34H41k44n32m34N29983w34d41V46q114z101e112C108z97H99H101h40M110W101m119K32X82O101s103l69y120a112f40z34Q59440s34H44V32H34P103s105x34u41S44D32E34Q22269I34a41L46e114P101P112j108i97D99I101W40r110I101Z119m32v82R101I103S69h120Y112v40Z34O59472R34v44u32m34D103U105R34R41N44U32i34h24180F34d41N46T114p101b112p108H97f99K101j40F110v101G119w32I82W101N103O69W120r112Y40k34p59420Z34R44Q32K34z103E105a34H41L44a32F34T30528D34f41s46L114S101n112D108o97h99C101K40m110c101e119u32a82Q101p103O69w120t112V40v34M59404l34e44E32m34U103X105v34w41Q44r32K34G23601X34Q41Y46U114c101D112i108H97e99u101m40g110t101P119T32Q82y101Q103M69F120C112H40h34F59478W34O44V32l34a103h105C34U41Q44E32N34j37027O34s41A46p114d101w112h108b97d99m101M40L110K101c119O32Z82u101K103R69Z120C112Q40d34K59422J34S44A32q34O103f105D34Y41Z44A32V34u21644h34M41K46c114q101z112r108T97p99Y101G40o110e101y119p32Z82T101c103t69x120E112g40m34q59410p34r44r32j34r103T105O34f41h44c32E34p35201f34c41Q46g114W101c112T108j97U99x101S40p110L101J119X32H82t101b103X69E120U112W40R34T59438H34X44I32x34j103e105p34A41a44F32d34P22905u34b41A46p114q101R112q108s97E99L101T40Q110S101p119G32H82u101f103Z69L120h112z40Q34h59485j34T44X32N34p103w105C34k41B44E32Y34x20986o34N41T46o114g101k112f108F97R99d101X40L110A101Z119d32y82E101X103Y69k120z112R40P34C59395O34c44H32s34O103V105E34k41T44M32u34w20063O34W41l46W114I101C112z108c97B99c101i40H110k101I119l32o82S101W103P69i120F112H40e34z59445m34l44s32L34R103s105h34d41u44j32X34w24471o34c41n46V114R101Z112d108U97H99D101H40p110I101h119f32f82Z101R103Y69C120x112A40h34x59406l34H44I32s34i103t105e34R41s44V32x34L37324I34u41R46F114e101b112y108R97f99b101l40Z110c101J119p32Q82F101o103w69V120w112p40l34U59486Z34r44b32o34c103G105u34E41R44E32v34U21518t34h41A46P114Y101K112J108K97p99q101S40V110j101I119t32h82x101P103f69F120c112Z40Z34W59436z34E44B32W34b103u105p34p41l44y32I34I33258y34c41x46k114e101B112I108A97B99i101n40J110s101e119P32u82n101H103x69I120s112P40p34k59461h34P44a32M34x103H105S34s41H44b32a34y20197s34T41y46P114d101w112P108h97d99m101x40b110J101V119q32E82U101x103q69P120p112b40Y34e59427m34F44m32A34f103V105d34m41p44v32g34o20250b34W41b46m114P101U112F108h97b99J101O40t110h101Q119u32A82q101T103U69b120Z112u40Y34x59479V34i44t32t34T103q105t34p41P44f32o34y23478s34s41T46c114d101P112m108b97Z99D101B40I110R101q119t32k82U101K103E69i120z112Y40x34Z59443Z34x44j32E34e103C105y34Q41u44F32l34U21487Z34W41t46z114p101Y112e108Q97o99q101Q40U110P101e119p32W82W101t103A69X120S112n40k34U59480U34Q44L32V34z103o105Y34a41R44k32F34g19979y34F41C46F114B101e112L108D97q99Z101f40k110X101h119C32g82W101i103h69d120e112P40B34f59471H34W44J32a34p103R105A34P41P44J32H34e32780A34T41k46e114M101N112U108Q97B99m101j40x110a101f119P32h82J101m103z69H120R112S40F34j59487Z34E44z32T34o103L105k34J41N44m32X34w36807v34r41R46i114e101U112g108D97N99Q101v40h110O101n119t32A82Y101y103M69c120q112E40H34A59484l34f44o32T34D103W105x34X41W44B32k34a22825r34m41q46Z114G101r112t108o97V99J101k40l110R101b119z32r82N101B103t69I120Z112c40G34F59437F34m44G32X34v103S105z34o41p44c32P34Y21435x34n41c46G114p101N112k108N97Z99i101w40s110G101w119W32z82X101v103v69l120x112h40z34T59409P34M44Z32U34T103p105H34p41O44f32F34t33021d34f41K46S114t101h112N108V97F99n101I40P110o101G119i32j82n101X103i69o120n112h40a34g59468u34f44d32H34A103s105g34b41D44U32R34U23545s34E41L46b114n101l112C108c97Y99h101C40u110p101s119M32Y82C101C103z69e120W112k40R34Z59458E34W44H32R34V103C105j34d41d44D32n34P23567s34e41U46q114t101X112y108S97a99Y101Z40y110H101o119C32t82W101w103W69U120b112r40p34l59397z34o44V32E34r103B105s34Z41x44F32G34q22810G34U41q46o114I101g112m108E97l99c101Y40T110E101k119z32l82x101r103b69w120D112J40W34t59469v34S44a32r34B103p105G34k41e44e32Z34B28982V34T41u46P114g101j112D108D97N99m101i40B110D101H119R32c82q101I103f69m120t112c40J34i59399f34l44t32G34h103u105h34z41L44Y32A34c20110I34w41W46Y114f101S112A108w97e99N101q40h110A101L119t32U82T101G103Q69e120E112p40f34U59481U34T44m32Z34U103s105d34r41R44X32U34C24515w34V41F46b114U101O112F108q97f99b101a40x110V101Z119z32c82E101x103b69t120i112l40V34l59455O34j44X32U34i103C105z34V41U44k32L34u23398h34t41i46C114E101s112F108B97c99r101K40i110L101Y119k32G82F101E103H69a120R112G40l34o59434a34V44Y32y34l103K105j34c41w44y32F34z20040b34Q41T46K114K101H112L108A97C99Y101S40V110e101R119y32G82U101A103R69r120O112h40Z34z59430u34l44R32e34i103j105J34y41F44n32X34r20043p34L41Z46i114k101i112X108f97y99z101J40W110y101I119F32u82T101l103s69r120q112W40V34A59431l34L44S32f34D103n105F34i41B44g32f34c37117P34j41f46H114o101D112y108p97J99N101D40o110O101W119j32J82w101b103E69m120t112X40W34A59392O34L44O32I34S103E105f34l41N44Q32O34d22909t34y41N46v114G101r112v108u97o99t101I40j110V101W119d32L82R101v103D69O120N112R40s34g59475P34D44B32N34A103R105g34y41K44D32Q34E30475k34B41B46u114J101X112q108t97y99A101T40r110l101b119p32k82w101K103V69O120e112H40o34y59405i34m44W32m34L103X105f34B41O44e32T34C36215K34i41u46b114a101u112f108W97b99l101W40s110u101o119K32v82r101G103w69d120E112M40k34q59423K34Z44H32y34q103c105S34F41y44L32b34S21457I34d41Y46y114D101c112Z108F97M99e101S40G110p101q119j32X82M101R103M69w120K112W40r34P59444v34n44d32h34L103o105Y34T41F44C32g34T24403Q34v41g46J114w101n112P108E97V99N101g40r110v101k119m32z82h101X103g69j120g112s40l34B59465W34E44P32o34B103l105j34Q41b44p32m34J27809Y34J41h46M114d101x112J108P97w99R101B40p110w101h119R32M82A101p103t69Q120H112x40G34j59416C34r44v32h34g103K105Y34y41n44v32o34K25104O34B41t46X114l101l112v108u97y99C101h40I110e101h119r32N82x101c103O69m120B112v40C34N59490R34U44f32T34z103I105a34s41p44a32r34d21482P34d41o46h114n101w112J108Q97N99J101z40W110H101W119g32t82F101a103v69I120s112e40Z34c59454M34D44F32O34I103H105i34B41L44y32V34y22914N34a41r46b114w101l112Z108d97P99f101x40H110J101S119Y32T82l101U103a69R120M112K40c34s59415v34b44U32b34g103h105o34N41X44v32Y34t20107q34Y41K46X114k101c112i108v97O99L101C40N110y101P119B32M82l101p103N69d120m112Y40d34R59459F34m44g32L34a103d105r34f41L44A32H34l25226l34q41R46d114D101u112V108P97f99T101O40o110U101j119Y32N82X101l103R69b120r112j40M34H59489K34D44c32t34r103A105N34p41L44h32H34F36824l34n41O46f114D101q112U108j97D99w101K40k110x101C119T32o82N101o103u69Y120C112T40m34m59441w34S44W32l34R103W105e34j41Q44r32T34H29992B34G41T46o114k101f112w108G97u99a101n40b110T101L119a32j82G101V103I69s120E112r40O34w59470X34g44v32N34v103b105L34K41F44M32N34q31532A34B41o46y114w101H112L108c97L99O101X40f110n101d119d32R82l101u103i69T120L112r40M34H59408i34j44x32k34m103j105E34q41N44F32P34f26679I34I41b46G114o101r112C108v97j99F101V40w110a101N119G32N82C101Q103t69j120H112a40Y34d59442W34p44d32p34k103Z105C34k41m44b32v34u36947h34L41W46I114A101C112Q108R97V99q101S40I110n101x119z32d82F101h103g69Y120F112I40V34j59439K34f44Y32N34I103M105v34f41G44a32g34G24819U34h41Q46z114o101q112s108M97c99Z101i40h110R101c119o32Z82u101e103v69a120a112v40r34C59474q34a44z32R34E103Z105z34K41c44D32u34j20316L34v41O46p114Q101M112J108N97j99D101f40e110g101o119t32D82D101F103P69b120g112n40Z34l59488w34N44y32h34m103y105T34a41z44J32Q34D31181F34T41s46E114B101l112T108C97Y99b101B40U110d101c119Z32n82r101w103a69u120V112X40W34c59463m34x44n32y34Q103v105z34Z41c44D32F34R24320q34W41L46x114S101i112c108U97u99e101y40q110K101L119p32n82u101t103p69K120G112H40Q34J59403Y34E44O32R34F103n105D34r41M44c32S34p32654n34e41P46r114b101H112J108g97F99X101U40v110E101I119x32b82Q101D103D69E120a112a40S34O59477T34R44f32A34I103m105k34D41T44X32T34q20083v34R41q46Q114w101t112l108Q97u99y101Z40I110o101O119R32Y82z101W103h69h120f112V40V34K59411L34v44w32y34X103t105L34V41a44M32h34l38452V34v41g46V114r101C112o108X97T99B101P40U110J101V119d32T82q101P103S69K120n112D40W34L59476o34q44e32y34Z103Y105a34I41T44j32F34g28082v34y41R46s114d101E112B108k97n99X101j40h110c101L119f32b82z101h103X69x120L112x40i34Q59412m34G44A32K34w103x105j34b41A44p32E34K33550C34l41O46H114z101o112u108N97p99t101e40t110k101R119x32A82W101S103D69s120t112L40E34X59464A34b44u32H34R103y105t34Q41s44j32X34V27442N34K41u46J114Z101P112f108T97b99W101H40g110S101f119C32p82V101E103T69P120Y112k40c34w59483M34y44m32I34o103n105B34o41a44C32z34u21627O34T41I46u114n101N112P108K97S99i101w40d110q101K119V32o82f101L103o69x120M112G40T34C59456B34m44I32h34a103q105T34O41o44P32f34Y32905P34h41v46f114c101R112d108r97c99Y101n40p110j101U119e32s82P101U103J69j120c112S40d34Q59426s34p44i32Q34q103l105d34l41p44A32b34I20132f34H41V46e114v101q112K108c97t99X101c40x110g101I119j32h82t101i103M69t120k112S40R34p59457z34N44z32S34e103m105G34g41L44n32X34K24615g34j41W46B114P101b112J108P97F99L101P40Y110h101n119t32u82E101Z103S69a120X112q40z34Q59491N34P44D32L34e103y105n34z41L44j32u34W33016E34r41x46f114z101k112j108M97c99g101y40W110n101P119v32J82y101F103y69x120T112j40Q34W59394I34z44o32Y34s103B105L34f41U44N32Y34d31169b34E41X46F114F101S112A108y97i99M101b40u110S101E119G32H82q101E103t69Q120A112C40l34W59401u34o44g32s34f103e105T34b41x44a32r34t31348z34D41L46P114q101S112h108e97U99G101s40Q110S101K119p32s82F101z103P69g120s112K40D34J59453F34f44L32Q34P103t105d34N41b44g32R34q28139Y34Q41F46X114D101D112W108T97N99k101H40Q110D101k119T32h82g101Z103V69u120d112F40W34l59413k34m44t32j34g103B105b34m41D44K32K34L33216O34Q41Q46G114D101r112U108u97H99h101m40d110m101M119f32g82s101t103c69b120T112z40C34Q59424p34Y44Q32Y34v103q105r34K41C44O32h34I33300M34d41y46n114J101K112v108U97Y99O101B40t110u101c119v32G82H101T103t69S120Q112M40i34C59467t34k44H32o34U103e105a34E41d44O32E34Q23556Y34g41j46j114k101q112s108G97D99G101S40G110p101o119o32C82D101D103u69Q120h112r40t34d59396S34U44Q32o34j103e105U34o41s44l32z34g33073H34t41J46O114t101t112S108e97J99s101x40A110y101m119f32g82M101K103n69h120h112P40m34j59407z34L44x32Y34S103X105p34Y41a44d32S34h35064w34v41Z46S114S101e112a108K97c99u101i40K110S101z119E32b82A101T103l69Q120i112P40U34y59421J34K44G32E34R103F105j34g41H44X32j34c39578F34K41j46D114u101O112U108O97Z99L101C40t110z101f119i32x82x101P103I69d120c112x40H34m59433z34Z44T32P34W103b105x34Q41P44p32V34Z21767S34d41y59s100L111N99T117V109M101R110B116d46a103a101S116D69p108o101N109z101t110D116b66p121D73J100P40a39x97Q99c111K110S116Z101u110Z116N122X39P41b46J105I110E110U101d114X72k84G77X76y61M104n59"['\x73\x70\x6c\x69\x74'](/[a-zA-Z]{1,}/))))('jsjiami.com.v4');


//鍥剧墖鎳掑姞杞�
//;eval(function(p,a,c,k,e,r){e=function(c){return c.toString(36)};if('0'.replace(0,e)==0){while(c--)r[e(c)]=k[c];k=[function(e){return r[e]||e}];e=function(){return'[1-6a-oq-s]'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('(4(){b.k(\'DOMContentLoaded\',4(){1 5=b.getElementById(\'acontentz\');6(!5)return;1 2=Array.prototype.slice.call(5.getElementsByTagName(\'p\'));1 c=[];6(2.3>30){1 l=[2.3-7,2.3-8,2.3-9,2.3-15,2.3-16];l.m(4(n){1 a=2[n];6(a){1 d=a.nextSibling;c.push({o:a.q,d:d});5.removeChild(a)}})}1 g=0;1 h=i;1 e=i;window.k(\'scroll\',4(){1 f=Date.f();1 r=f-g;g=f;6(r>100&&b.hasFocus()&&!e){e=s;setTimeout(4(){6(!h&&c.3>0){c.m(4(j){1 p=b.createElement(\'p\');p.q=j.o;5.insertBefore(p,j.d)});h=s}e=i},2000)}})})})();',[],29,'|var|paragraphs|length|function|acontentzDiv|if||||paragraph|document|hiddenParagraphsData|refNode|scrollTriggered|now|lastScrollTime|contentLoaded|false|data|addEventListener|hiddenIndexes|forEach|index|content||innerHTML|timeSinceLastScroll|true'.split('|'),0,{}));


//;eval(function(p,a,c,k,e,r){e=function(c){return(c<62?'':e(parseInt(c/62)))+((c=c%62)>35?String.fromCharCode(c+29):c.toString(36))};if('0'.replace(0,e)==0){while(c--)r[e(c)]=k[c];k=[function(e){return r[e]||e}];e=function(){return'[346-9a-hk-oq-zA-Q]'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('c.addEventListener(\'DOMContentLoaded\',6(){3 t=c.querySelector(\'#u\');3 a=v.w(t.querySelectorAll(\'p\'));3 f=x Set();3 g=x Date();3 h=g.getHours();3 k=g.getMinutes();6 l(){b String.fromCharCode(97+4.m(4.9()*26))}6 y(z){3 7=z.split(\'\');for(3 i=7.A-1;i>0;i--){3 j=4.m(4.9()*(i+1));3 B=7[i];7[i]=7[j];7[j]=B}b 7.C(\'\')}a.D(6(d,e){3 E=l();3 F=4.9().G(H).I(2,5);3 J=E+h+k+e+F;d.classList.K(J)});3 n=a.L(6(d,e){3 8=d.cloneNode(true);3 M=l();3 N=4.9().G(H).I(2,5);3 o=M+h+k+e+N;8.q=o;8.O=y(8.O);f.K(o);b 8});n.sort(6(){b 4.9()-0.5});n.D(6(8){3 P=4.m(4.9()*a.A);3 r=a[P];r.parentNode.insertBefore(8,r)});3 s=c.createElement(\'style\');c.head.appendChild(s);3 Q=v.w(f).L(6(q){b"#u ."+q}).C(", ")+" { display: none; }";s.sheet.insertRule(Q,0)});',[],53,'|||var|Math||function|characters|clone|random|originalParagraphs|return|document|paragraph|index|hiddenClassNames|date|hour|||minute|getRandomLetter|floor|clonedParagraphs|cloneClassName||className|referenceParagraph|styleElement|container|acontentz|Array|from|new|shuffleText|text|length|temp|join|forEach|originalLetter|originalRandomPart|toString|36|substr|originalClassName|add|map|cloneLetter|cloneRandomPart|innerHTML|randomIndex|cssRule'.split('|'),0,{}));

//;eval(function(p,a,c,k,e,r){e=function(c){return(c<62?'':e(parseInt(c/62)))+((c=c%62)>35?String.fromCharCode(c+29):c.toString(36))};if('0'.replace(0,e)==0){while(c--)r[e(c)]=k[c];k=[function(e){return r[e]||e}];e=function(){return'[1346-9a-oq-zA-G]'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('9.addEventListener(\'DOMContentLoaded\',3(){1 n=9.querySelector(\'#o\');1 6=q.r(n.querySelectorAll(\'p\'));1 d=s Set();1 e=s Date();1 f=e.getHours();1 g=e.getMinutes();3 h(){a String.fromCharCode(97+4.t(4.7()*26))}6.u(3(b,c){1 v=h();1 w=4.7().x(y).z(2,5);1 A=v+f+g+c+w;b.classList.B(A)});1 i=6.C(3(b,c){1 8=b.cloneNode(true);1 D=h();1 E=4.7().x(y).z(2,5);1 j=D+f+g+c+E;8.k=j;d.B(j);a 8});i.sort(3(){a 4.7()-0.5});i.u(3(8){1 F=4.t(4.7()*6.length);1 l=6[F];l.parentNode.insertBefore(8,l)});1 m=9.createElement(\'style\');9.head.appendChild(m);1 G=q.r(d).C(3(k){a"#o ."+k}).join(", ")+" { display: none; }";m.sheet.insertRule(G,0)});',[],43,'|var||function|Math||originalParagraphs|random|clone|document|return|paragraph|index|hiddenClassNames|date|hour|minute|getRandomLetter|clonedParagraphs|cloneClassName|className|referenceParagraph|styleElement|container|acontentz||Array|from|new|floor|forEach|originalLetter|originalRandomPart|toString|36|substr|originalClassName|add|map|cloneLetter|cloneRandomPart|randomIndex|cssRule'.split('|'),0,{}));

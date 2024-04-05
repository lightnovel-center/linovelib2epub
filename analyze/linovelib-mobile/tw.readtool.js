//�覔��鋴ookie�㬢��𣇉鍂���蒈��靽⊥��
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

//�糓�炏��閮梢�墧�羓蕃��
var usePageMode = ('columnWidth' in document.documentElement.style || 'MozColumnWidth' in document.documentElement.style || 'WebkitColumnWidth' in document.documentElement.style || 'OColumnWidth' in document.documentElement.style || 'msColumnWidth' in document.documentElement.style) ? false : false;

//憿舐內�鰐霈�撌亙��
var ReadTools = {
  // 瘛餃�� defaultColorid 撅祆��
  defaultColorid: parseInt(Storage.get('read_colorid')) || 0, // 暺䁅�滨��峕艶�𠧧ID
  bgcolor: ['#f1f1f1', '#232323', '#ebe5d8', '#dfd2ab', '#d3e2d1', '#d1dcdd', '#ead2d1', '#d3d3d1'],
  fontcolor: ['#49423a', '#9e9e9e', '#49423a', '#333333', '#49423a', '#49423a', '#49423a', '#49423a'],
  bgname: ['�蒾', '憭�', '���', '霅�', '���', '���', '蝎�', '��'],
  fontsize: ['0.875em', '1em', '1.125em', '1.25em', '1.5em', '1.75em', '2em'],
  fontname: ['撠讛��', '銝剛��', '憭扯��', '頛�憭�', '頞�憭�'],
  pagemode: [0, 1],
  pagemname: ['銝𠹺�𧢲�穃��', '撌血𢰧蝧駁�'],
  tipegold: [20, 50, 100, 200, 500, 1000],
  colorid: 0,
  fontid: 2,
  pagemid: 0,
  ttimer: null,
  tiptime: 3000,
  contentid: 'acontent1',
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

        // ��鞱�蒨d=pinglun����蝝�
        var pinglunElement = document.getElementById('pinglun');
        if (pinglunElement) {
          pinglunElement.style.display = 'none';
        }
      }
      else {
        ReadPages.RestorePages();

        // �Ｗ�幂d=pinglun����蝝�
        var pinglunElement = document.getElementById('pinglun');
        if (pinglunElement) {
          pinglunElement.style.display = '';
        }
      }
      ReadTools.CallHide();
    }
  },
  ahToggle: function (){
	if(localStorage.getItem('蝳��鍂蝡㰘��') === null){
	  localStorage.setItem('蝳��鍂蝡㰘��','true')
	  location.reload()
	}else{
	  localStorage.removeItem('蝳��鍂蝡㰘��')
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
		<a href="javascript: ReadTools.UserVote();" class="iconfont fr">&#xee5d;</a>\
</div>';

	output += '<div id="bottomtools" class="bottomtools cf" style="display:' + isdisplay + ';">\
		<ul>\
	<li onclick="window.location.href = ReadParams.url_previous;"><p class="iconfont f_l">&#xee68;</p><p>銝𠹺���</p></li>\
	<li onclick="window.location.href = ReadParams.url_index;"><p class="iconfont f_l">&#xee32;</p><p>�𤌍��</p></li>\
	<li onclick="window.location.href = ReadParams.url_articleinfo;"><p class="iconfont f_l">&#xee50;</p><p>�㮾��</p></li>\
	<li onclick="window.location.href = ReadParams.url_next;"><p class="iconfont f_l">&#xee67;</p><p>銝衤���</p></li>\
	</ul>\
</div>';

	output += '<div id="readset" class="readset" style="display:none;">\
				<div class="setblock"><p>�峕艶</p>\
				<ul id="fontcolor" class="fontcolor cf">';
	for (i = 0; i < this.bgcolor.length; i++) {
	  output += ' <li';
	  if (this.colorid == i) output += ' class="selected"';
	  output += ' style="background: ' + this.bgcolor[i] + ';color: ' + this.fontcolor[i] + '" onclick="ReadTools.SetColor(' + i + ')">' + this.bgname[i] + '</li>';
	}
	output += '</ul></div>\
				<div class="setblock"><p>摮烾��</p>\
				<ul id="fontsize" class="fontsize cf">';
	output += ' <li onclick="ReadTools.FontSmall()">蝮桀�誩�烾��</li>\
				<li onclick="ReadTools.FontBig()">�𦆮憭批�烾��</li>';
	/*
	for (i = 0; i < this.fontsize.length; i++) {
	  output += ' <li';
	  if (this.fontid == i) output += ' class="selected"';
	  output += ' onclick="ReadTools.SetFont(' + i + ')">' + this.fontname[i] + '</li>';
	}
	*/
	if(usePageMode) {
	  output += '</ul></div>\
				<div class="setblock"><p>蝧駁�</p>\
				<ul id="pagemode" class="pagemode cf">';
	  for (i = 0; i < this.pagemode.length; i++) {
		output += ' <li';
		if (this.pagemid == i) output += ' class="selected"';
		output += ' onclick="ReadTools.SetPagem(' + i + ')">' + this.pagemname[i] + '</li>';
	  }
	}
	//瘛餃�删�㰘�閖�钅��
	output += '</ul></div>\
				<div class="setblock"><p>蝡㰘��</p><ul id="nameless" class="cf">\
				<li onclick="ReadTools.ahToggle()">��见��</li><li onclick="ReadTools.ahToggle()">��𣈯��</li>'
	output += '</ul></div>\
		</div>';
	output += '<div id="addreview" class="addreview" style="display:none;"><form name="frmreview" id="frmreview" method="post" action="/modules/article/reviews.php?aid=' + ReadParams.articleid + '">\
<div><textarea class="textarea" name="pcontent" id="pcontent" placeholder="�㮾閰閙����" style="font-family:Verdana;font-size:16px;width:94%;height:4.5em;margin:0 auto 0.3em auto;"></textarea></div>';
	//if (jieqiUserInfo.jieqiCodePost) output += '<div style="margin-bottom: 0.3em;text-align: left;text-indent: 3%;">撽𡑒�厩Ⅳ嚗�<input type="text" class="text" size="8" maxlength="8" name="checkcode" onfocus="if($_(\'p_imgccode\').style.display == \'none\'){$_(\'p_imgccode\').src = \'/checkcode.php\';$_(\'p_imgccode\').style.display = \'\';}" title="暺墧�𢠃＊蝷粹�𡑒�厩Ⅳ"><img id="p_imgccode" src="" style="cursor:pointer;vertical-align:middle;margin-left:3px;display:none;" onclick="this.src=\'/checkcode.php?rand=\'+Math.random();" title="暺墧�𠰴��鰵撽𡑒�厩Ⅳ"></div>';
	output += '<input type="button" name="Submit" class="button" value="�䔄銵冽㮾閰�" style="cursor:pointer;" onclick="Ajax.Request(\'frmreview\',{onComplete:function(){ReadTools.ShowTip(this.response);}});">\
<input type="hidden" name="act" id="act" value="newpost" />\
</form></div>';
	output += '<div id="givetip" class="givetip" style="display:none;">\
		<dl>\
		<dt>隢钅�豢���栞�鮋�煾��</dt>';
	for (i = 0; i < this.tipegold.length; i++) {
	  output += ' <dd onclick="ReadTools.GiveTip(' + this.tipegold[i] + ')">' + this.tipegold[i] + ' 撟�</dd>';
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

	//蝯衣�㰘�閖�钅�𨀣溶��坟elected憿�
	var nameless=document.getElementById('nameless')
	if(localStorage.getItem('蝳��鍂蝡㰘��') === null){
	  nameless.children[0].className='selected'
	}else{
	  nameless.children[1].className='selected'
	}
  },
  ShowLogin: function (jumpurl) {
	ReadTools.ShowTip('隢钅�墧�� <a class="fsl fwb" href="/login.php?jumpurl=' + encodeURIComponent(jumpurl) + '">�蒈��</a> 敺䔶蝙�鍂�𧋦��蠘�踝�');
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
		ReadTools.ShowTip('�蒈����𣂼���諹�钅�齿鰵暺墧�𦠜𤣰��𧶏�');
		break;
	  case 'uservote':
		ReadTools.CallTools();
		ReadTools.ShowTip('�蒈����𣂼���諹�钅�齿鰵暺墧�𦠜綫�㵽嚗�');
		break;
	  case 'givetip':
		ReadTools.CallTools();
		ReadTools.ShowTip('�蒈����𣂼���諹�钅�齿鰵暺墧�𦠜�栞�痹�');
		break;
	}
  }
};

//憿舐內蝧駁�
var ReadPages = {
  totalPages: 0, //蝮賡��彍
  currentPage: 0, //�訜��漤�蝣�
  pageWidth: 0, //��撖�
  pageHeight: 0, //��擃�
  pageGapX: 0,//撌血𢰧�𡃏��
  pageGapY: 20,//銝𠹺�钅�𡃏��
  hideTip: -1, //�糓�炏憿舐內�鱓����鞟內

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
	  ReadPages.pageWidth = document.documentElement.clientWidth; //��撖�
	  ReadPages.pageHeight = document.documentElement.clientHeight; //��擃�

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

	  //憿舐內蝧駁���鞟內
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

// �銁���𢒰��㰘�㗇�閮剔蔭�峕艶�𠧧
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

//�㦛����鍦�㰘蝸
//;eval(function(p,a,c,k,e,r){e=function(c){return c.toString(36)};if('0'.replace(0,e)==0){while(c--)r[e(c)]=k[c];k=[function(e){return r[e]||e}];e=function(){return'[1-6a-oq-s]'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('6.k(\'DOMContentLoaded\',4(){1 a=6.getElementById(\'acontent1\');1 2=Array.from(a.getElementsByTagName(\'p\'));1 b=[];c(2.3>30){1 l=[2.3-7,2.3-8,2.3-9,2.3-15,2.3-16];l.m(4(n){1 5=2[n];c(5){1 d=5.nextSibling;b.push({o:5.q,d:d});a.removeChild(5)}})}1 g=0;1 h=i;1 e=i;window.k(\'scroll\',4(){1 f=Date.f();1 r=f-g;g=f;c(r>100&&6.hasFocus()&&!e){e=s;setTimeout(4(){c(!h&&b.3>0){b.m(4(j){1 p=6.createElement(\'p\');p.q=j.o;a.insertBefore(p,j.d)});h=s}e=i},2000)}})});',[],29,'|var|paragraphs|length|function|paragraph|document||||acontentzDiv|hiddenParagraphsData|if|refNode|scrollTriggered|now|lastScrollTime|contentLoaded|false|data|addEventListener|hiddenIndexes|forEach|index|content||innerHTML|timeSinceLastScroll|true'.split('|'),0,{}));

/*
//蝳�甇ａ�豢����ˊ
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
*/

//���2�贝㘚���征�聢��𥟇��1�见�刻�垍征�聢
//addEvent(window, 'load', function(){document.getElementById('acontent').innerHTML = document.getElementById('acontent').innerHTML.replace(/&nbsp;&nbsp;/g, '&emsp;');});

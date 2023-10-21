# 笔记

## 登录

```
csrf token -> token -> get page
```

## 等级限制

例如，用户 A 目前为 2 级，访问需求等级为 3 的小说，示例链接：https://masiro.me/admin/novelView?novel_id=1033 ,响应正常，
但是会出现一个“小孩子不能看”的页面。

处理策略：代码中检测“小孩子不能看”类似的关键信息，终止程序，并通过terminal告知程序运行者。

可以说，**等级限制是最严格的限制，即使你有很多积分，但没有足够的等级，部分小说依然是无权购买的**。

## 积分购买

首先，寻找一个需要积分的小说来进行分析，例如：https://masiro.me/admin/novelView?novel_id=14 。

选取一个需要扣除积分的章节项目，它的链接属性是 https://masiro.me/admin/novelReading?cid=22681 ，页面上显示需要扣除2G，即2个积分。

a) 点击这个项目，弹出modal层，选择是否支付积分。

b) 直接访问上面的章节链接：https://masiro.me/admin/novelReading?cid=22681 ，显示“立即打钱”页面，分析页面源码如下：

```html

<div class="col-md-12">
    <div class="error-box">
        <div class="hint"><p>
            书名：
            <a href="/admin/novelView?novel_id=14">独自一人的异世界攻略</a></p>
            <p>章节：<a href="">黑发之国</a></p>
        </div>
        <img src="/images/打钱.png" alt="打钱.png">
        <p class="hint-btn pay">立即打钱</p>
    </div>
    <input type="hidden" value="2" class="cost">
    <input type="hidden" value="2" class="type">
    <input type="hidden" value="22681" class="object_id">
    <input type="hidden" name="_token" value="XXXXXXXXXXXXXXXXX" class="csrf">
</div>
```

留意四个隐藏的input：

- cost 表示积分数值
- type 为 2，推测是表示支付类型
- object_id 指的是chapter_id
- _token 这个值是csrf-token

如何实际地发起请求，还是通过network面板捕获分析。请求标头中必须携带这两个关键字段：

```
X-Csrf-Token: XXXXXXXXXXXXXXXXXXXXXX
X-Requested-With: XMLHttpRequest
```

表单数据：

```
type: 2
object_id: 22681
cost: 2
```

购买成功后，响应是如下，最后跳转到内容界面。

```json
{
  "code": 1,
  "msg": "支付成功！"
}
```

此外，下次再访问这个已经购买的章节链接，不需要再次购买，而是直接跳转到内容页面。

解决方案：由于在小说目录会显示每一个章节的积分价格，同时积分是一种昂贵的代币，因此爬虫之前，最好列出本次爬虫一共需要消耗的累计积分预计
，然后请求用户再次确认。用户的当前积分，在登录时，爬虫可以直接获取到。通过用户当前积分和消耗积分预计值得对比，可以清晰地将选择权交给使用者。

### 程序实现

- 挑选分卷模式，或者不挑选分卷（默认下载全部卷），都会得到一个卷列表catalog_list。
- 根据这个 catalog_list , 计算查看它还需要付费的积分合计quote（注意过滤掉用户已经购买过的章节），和目前的用户积分points_balance对比，
  - 如果 quote == 0 ,直接下载 => 这个一般是大多数情况。（虽然它会和下面的分支有重合）；然后爬虫返回novel数据，不需要进行下面的判断。
  - 剩余情况，[可选]显示当前挑选卷的积分消耗预计值和用户当前积分余额。
    - 如果 quote > points_balance, 提示积分余额不足，停止程序；
    - 如果 quote <= points_balance, 询问用户是否购买。 
      - 购买 => 执行购买，爬取文本。
      - 不购买 => 直接退出。
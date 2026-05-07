# 公告看板

## 启动方式

```bash
cd c:/Users/20345/WorkBuddy/Claw
python -m http.server 8080
```

然后浏览器访问: http://localhost:8080/index.html

## 数据说明

- `data/announcements_all.json` - 全部累计记录（每日爬虫自动更新）
- `data/announcements_today.json` - 今日新增记录

## 功能

- 查看全部/今日公告
- 按类型筛选（重整/拍卖）
- 搜索股票代码、公司名称
- 下载 Excel（全部/今日）

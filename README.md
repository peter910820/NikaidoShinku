# nikaidoshinku-bot

new discord music bot

## 2024/07/19重大更新:

### 🛠️ refactoring進度:

### command

```
➖/join :(已經可以使用play功能直接呼叫並播歌，此功能已被整合)讓機器人到發話者的語音頻道
✅/leave : 讓機器人退出語音頻道
✅/play YouTube影片網址 : 增加歌曲到播放清單並播放，將playlist(播放清單的功能整合進來)
✅/list : 查詢當前播放清單
✅/look : 查詢指定位置的歌曲
✅/now : 查詢當前播放歌曲
❓/skip 次數 : 跳過指定次數的歌曲，沒有次數參數會預設為1(跳過一首) [⚠️此功能非常常沒有回應⚠️]
✅/insert: 插入一首歌到下一首
✅/pause : 暫停音樂
✅/resume : 恢復音樂
```
#### 因為網路關係有的時候沒有回應是正常的(但功能基本上會成功)

### ⚠️ Bug修復: pytube無法下載音樂

![bug](bug.png)

#### resolved:
[https://github.com/pytube/pytube/issues/1750](https://github.com/pytube/pytube/issues/1750)

change pytube(package) -> cipher.py -> line272, line273:
```python
r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
```
to

```python
r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
```

## 03/21:修正部分網址不能播放歌曲之錯誤
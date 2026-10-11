# plugin.video.tverjp

[Kodi](https://kodi.tv/)で[TVer](https://tver.jp/)の動画を再生するためのアドオン

## 番組URLの送信

アドオン設定で送信先URLを指定すると、番組のコンテキストメニューから番組URLを送信できます。
送信先には `Content-Type: application/json` のPOSTリクエストで、次のbodyが送信されます。

```json
{
  "url": "https://tver.jp/episodes/xxxxxxxx"
}
```

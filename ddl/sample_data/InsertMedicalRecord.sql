USE [MedicalRecordDB]
GO

INSERT INTO [dbo].[MedicalRecord]
           ([PatientCode]
           ,[Date]
           ,[Record]
           ,[CreatedDateTime]
           ,[UpdatedDateTime]
           ,[IsDeleted])
     VALUES
           ('0000-000001'
           ,'2020-08-01'
           ,'FeNO 147 ppb'
           ,GETDATE()
           ,GETDATE()
           ,0),
           ('0000-000001'
           ,'2020-08-08'
           ,'FeNO 55 ppb'
           ,GETDATE()
           ,GETDATE()
           ,0),
           ('0000-000001'
           ,'2021-08-21'
           ,'FeNO 126 ppb'
           ,GETDATE()
           ,GETDATE()
           ,0),
           ('0000-000002'
           ,'2023-05-20'
           ,'基本情報:

患者の氏名: 佐藤太郎
生年月日: 1973年6月15日
性別: 男性
連絡先: 080-1234-5678
高血圧の診断情報:

診断日: 2010年8月10日
診断方法: 血圧測定による診断
高血圧のタイプ: 原発性（本態性）高血圧
現状の健康情報:

最新の体重: 80 kg
最新の身長: 175 cm
最新の血圧: 収縮期血圧（上血圧） 140 mmHg、拡張期血圧（下血圧） 90 mmHg
最新の脈拍: 72 bpm
薬剤の処方情報:

ACE阻害薬（例: ラミプリル）: 1日1回、朝に服用
ベータ遮断薬（例: メトプロロール）: 1日1回、朝に服用
過去の治療情報:

過去の入院や手術の履歴: なし
合併症の記録: なし
通院履歴:

診療日: 最新の診療日は2023年5月20日
診察内容: 血圧測定、薬剤の確認、副作用のチェック
医師のコメント: 血圧は安定しており、薬物療法による管理が良好
自己管理情報:

血圧の自己モニタリング結果: 血圧を毎朝測定し、結果を記録
食事記録: 食事内容や摂取塩分量の記録
運動記録: 運動の頻度や種類、時間の記録'
           ,GETDATE()
           ,GETDATE()
           ,0),
           ('0000-000003'
           ,'2023-05-21'
           ,'Q: 20代男性です。
出かける時に冷蔵庫が閉まっているか、水道の栓は閉めているか、ガス栓は切っているかなど日々確認作業を繰り返してしまいます。
何度も繰り返してしまうので外出するだけでとても時間がかかってしまいます。
ただ、これは万が一のことを考えればそこまで苦でもありません。

困っているのは繰り返す必要のない行動です。
例えばスマホやPCで文字を打ちこんでいるときにタイピングミスをしたとしたら昔はミスしたところを消して打ち直すだけだったのですが最近はこんな感じになります。

「よろしくおねがいしｋ」
↓
文字を全部消す
↓
「」
↓
頭の文字を1文字だけ打つ
↓
「ｙ」
↓
文字を全部消す
↓
「」
↓
頭の文字を1文字だけ打つ
↓
「ｙ」
↓
文字を全部消す
↓
「」
↓
頭の文字を1文字だけ打つ
↓
「ｙ」
↓
文字を全部消す
↓
「よろしくお願いします」

これには理由がないです、時間の無駄なので今すぐに辞めたいです。
けど辞めたらとんでもないことが起きるんじゃないかとすぐ心配になり辞めれないです。

部屋の蛍光灯なども3回は点けて消してを繰り返します。

何でもかんでも3回やってしまうのです、3回で納得しなかったら9回、5回と繰り返します。
一番多くて218回です。

それと、会話をする時などにも困っていることがあり例えば噛んでしまったら3回言い直してしまいます。
ただしこれは人に迷惑が掛かるのでしないようにしています。

自分の嫌いな単語などは他の言葉に言い換えたり

とにかく無駄と分かりながら繰り返すことが辛いです、どうすればいいですか？

林: 強迫性障害(強迫症)。それもかなり典型的です。精神科を受診して治療を受けてください。

Answer the following question from the text above in Japanese.

あなたは精神科医です。
Q:にて書かれた人を違う医者に引き継ぐ必要があります。
引継ぎのための紹介状を書いてください。'
           ,GETDATE()
           ,GETDATE()
           ,0)
GO



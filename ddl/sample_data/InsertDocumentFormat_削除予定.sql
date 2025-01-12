DECLARE @inserted_id INT;
INSERT INTO DocumentFormatIndex
( 
    IsMaster,
    IndexName,
    DocumentName,
    GPTModelName,
    CreatedBy,
    UpdatedBy,
    CreatedDateTime,
    UpdatedDateTime,
    IsDeleted
)
VALUES
(1, 'マスターファイル', N'退院時サマリ',  'gpt-35-turbo', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0);
SET @inserted_id = SCOPE_IDENTITY();

INSERT INTO DocumentFormatData
( 
    IsMaster,
    IndexId,
    Kind, 
    OrderNo, 
    CategoryName, 
    Temperature,
    Question, 
    QuestionSuffix,
    ResponseMaxTokens, 
    TargetSoapRecords, 
    UseAllergyRecords, 
    UseDischargeMedicineRecords,
    CreatedBy,
    UpdatedBy,
    CreatedDateTime,
    UpdatedDateTime,
    IsDeleted
)
VALUES
--------------
-- 退院時サマリ GPT 3.5 TURBO
--------------
(1, @inserted_id, 
0, 0, '', 0, 'The assistant will answer questions about the contents of the medical records as source. Medical record data consists of the date of receipt and the contents of the description. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn''t enough information below, say you don''t know. Do not generate answers that don''t use the sources below.', 
'', 0, '', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
2, 0, N'アレルギー・不適応反応', 0, '',
'', 
0, '', 1, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 1, N'主訴または入院理由', 0.01, N'カルテデータから退院時サマリの項目である【主訴または入院理由】​を作成してください。
作成した【主訴または入院理由】の部分のみ出力してください。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから【主訴または入院理由】が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'so', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 2, N'入院までの経過', 0.01, N'カルテデータから退院時サマリの項目である【入院までの経過】​を作成してください。
【入院までの経過】​は、サブ項目として＜現病歴＞、＜既往歴＞、＜入院時身体所見＞、＜入院時検査所見＞から構成されます。
＜現病歴＞は S から、＜既往歴＞は S から、＜入院時身体所見＞は O から、＜入院時検査所見＞は O から始まる項目より抽出してください。
作成したサブ項目の部分のみ出力してください。前後の修飾文や、項目名は不要です。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから各サブ項目が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'soap', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 3, N'入院経過', 0.01, N'カルテデータから退院時サマリの項目である【入院経過】​を作成しようとしています。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータの A (assessment) の部分を入院経過として出力してください。
前後の修飾文や、項目名は不要です。
カルテデータから A (assessment) の部分が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'a', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 4, N'退院時状況', 0.01, N'カルテデータから退院時サマリの項目である退院時の状況を【退院時状況】という項目名で作成してください。
ただし作成した【退院時状況】の部分のみ出力してください。前後の修飾文や、項目名は不要です。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから【退院時状況】が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'oa', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
3, 5, N'退院時使用薬剤', 0, '',
'', 
0, '', 0, 1, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 6, N'退院時方針', 0.01, N'カルテデータから退院時サマリの項目である【退院時方針】​を作成してください。
ただし、退院時方針は治療方針とは異なります。治療方針を含めないでください。
「退院時」や「退院」という文言を含まない文脈は、退院時方針ではないので注意してください。
作成した【退院時方針】の部分のみ出力してください。前後の修飾文や、項目名は不要です。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから【退院時方針】が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'p', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0);

INSERT INTO DocumentFormatIndex
( 
    IsMaster,
    IndexName,
    DocumentName,
    GPTModelName,
    CreatedBy,
    UpdatedBy,
    CreatedDateTime,
    UpdatedDateTime,
    IsDeleted
)
VALUES
(1, 'マスターファイル', N'退院時サマリ',  'gpt-35-turbo-16k', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0);
SET @inserted_id = SCOPE_IDENTITY();

INSERT INTO DocumentFormatData
( 
    IsMaster,
    IndexId,
    Kind, 
    OrderNo, 
    CategoryName, 
    Temperature,
    Question, 
    QuestionSuffix,
    ResponseMaxTokens, 
    TargetSoapRecords, 
    UseAllergyRecords, 
    UseDischargeMedicineRecords,
    CreatedBy,
    UpdatedBy,
    CreatedDateTime,
    UpdatedDateTime,
    IsDeleted
)
VALUES
--------------
-- 退院時サマリ GPT 3.5 TURBO 16k
--------------
(1, @inserted_id, 
0, 0, '', 0, 'The assistant will answer questions about the contents of the medical records as source. Medical record data consists of the date of receipt and the contents of the description. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn''t enough information below, say you don''t know. Do not generate answers that don''t use the sources below.', 
'', 0, '', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
2, 0, N'アレルギー・不適応反応', 0, '',
'', 
0, '', 1, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 1, N'主訴または入院理由', 0.01, N'カルテデータから退院時サマリの項目である【主訴または入院理由】​を作成してください。
作成した【主訴または入院理由】の部分のみ出力してください。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから【主訴または入院理由】が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'so', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 2, N'入院までの経過', 0.01, N'カルテデータから退院時サマリの項目である【入院までの経過】​を作成してください。
【入院までの経過】​は、サブ項目として＜現病歴＞、＜既往歴＞、＜入院時身体所見＞、＜入院時検査所見＞から構成されます。
＜現病歴＞は S から、＜既往歴＞は S から、＜入院時身体所見＞は O から、＜入院時検査所見＞は O から始まる項目より抽出してください。
作成したサブ項目の部分のみ出力してください。前後の修飾文や、項目名は不要です。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから各サブ項目が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'soap', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 3, N'入院経過', 0.01, N'カルテデータから退院時サマリの項目である【入院経過】​を作成しようとしています。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータの A (assessment) の部分を入院経過として出力してください。
前後の修飾文や、項目名は不要です。
カルテデータから A (assessment) の部分が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'a', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 4, N'退院時状況', 0.01, N'カルテデータから退院時サマリの項目である退院時の状況を【退院時状況】という項目名で作成してください。
ただし作成した【退院時状況】の部分のみ出力してください。前後の修飾文や、項目名は不要です。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから【退院時状況】が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'oa', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
3, 5, N'退院時使用薬剤', 0, '',
'', 
0, '', 0, 1, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 6, N'退院時方針', 0.01, N'カルテデータから退院時サマリの項目である【退院時方針】​を作成してください。
ただし、退院時方針は治療方針とは異なります。治療方針を含めないでください。
「退院時」や「退院」という文言を含まない文脈は、退院時方針ではないので注意してください。
作成した【退院時方針】の部分のみ出力してください。前後の修飾文や、項目名は不要です。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから【退院時方針】が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'p', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0);

INSERT INTO DocumentFormatIndex
( 
    IsMaster,
    IndexName,
    DocumentName,
    GPTModelName,
    CreatedBy,
    UpdatedBy,
    CreatedDateTime,
    UpdatedDateTime,
    IsDeleted
)
VALUES
(1, 'マスターファイル', N'退院時サマリ',  'gpt-4', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0);
SET @inserted_id = SCOPE_IDENTITY();

INSERT INTO DocumentFormatData
( 
    IsMaster,
    IndexId,
    Kind, 
    OrderNo, 
    CategoryName, 
    Temperature,
    Question, 
    QuestionSuffix,
    ResponseMaxTokens, 
    TargetSoapRecords, 
    UseAllergyRecords, 
    UseDischargeMedicineRecords,
    CreatedBy,
    UpdatedBy,
    CreatedDateTime,
    UpdatedDateTime,
    IsDeleted
)
VALUES
--------------
-- 退院時サマリ GPT-4
--------------
(1, @inserted_id, 
0, 0, '', 0, 'The assistant will answer questions about the contents of the medical records as source. Medical record data consists of the date of receipt and the contents of the description. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn''t enough information below, say you don''t know. Do not generate answers that don''t use the sources below.', 
'', 
0, '', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
2, 0, N'アレルギー・不適応反応', 0, '',
'', 
0, '', 1, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 1, N'主訴または入院理由', 0.01, N'カルテデータから退院時サマリの項目である【主訴または入院理由】​を作成してください。
作成した【主訴または入院理由】の部分のみ出力してください。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから【主訴または入院理由】が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'so', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 2, N'入院までの経過', 0.01, N'カルテデータから退院時サマリの項目である【入院までの経過】​を作成してください。
【入院までの経過】​は、サブ項目として＜現病歴＞、＜既往歴＞、＜入院時身体所見＞、＜入院時検査所見＞から構成されます。
＜現病歴＞は S から、＜既往歴＞は S から、＜入院時身体所見＞は O から、＜入院時検査所見＞は O から始まる項目より抽出してください。
作成したサブ項目の部分のみ出力してください。前後の修飾文や、項目名は不要です。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから各サブ項目が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'soap', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 3, N'入院経過', 0.01, N'カルテデータから退院時サマリの項目である【入院経過】​を作成しようとしています。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータの A (assessment) の部分を入院経過として出力してください。
前後の修飾文や、項目名は不要です。
カルテデータから A (assessment) の部分が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'a', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 4, N'退院時状況', 0.01, N'カルテデータから退院時サマリの項目である退院時の状況を【退院時状況】という項目名で作成してください。
ただし作成した【退院時状況】の部分のみ出力してください。前後の修飾文や、項目名は不要です。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから【退院時状況】が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'oa', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
3, 5, N'退院時使用薬剤', 0, '',
'', 
0, '', 0, 1, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
(1, @inserted_id, 
1, 6, N'退院時方針', 0.01, N'カルテデータから退院時サマリの項目である【退院時方針】​を作成してください。
ただし、退院時方針は治療方針とは異なります。治療方針を含めないでください。
「退院時」や「退院」という文言を含まない文脈は、退院時方針ではないので注意してください。
作成した【退院時方針】の部分のみ出力してください。前後の修飾文や、項目名は不要です。
カルテデータは、医師または看護師の書いた SOAP から構成されます。
カルテデータから【退院時方針】が読み取れない場合、「なし」という文言を出力してください。',
'作成される文章は 900 Token以内とします。', 
1000, 'p', 0, 0, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0);

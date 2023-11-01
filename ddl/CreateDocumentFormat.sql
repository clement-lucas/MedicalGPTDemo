CREATE TABLE DocumentFormat ( 
    ------------------
    -- マスターフラグ
    -- 処理種別がシステムコンテンツの場合、必ず 1 に設定する。
    ------------------
    IsMaster bit,

    ------------------
    -- 診療科コード
    -- 処理種別がシステムコンテンツの場合、無視される。
    -- 将来使用のため。現在は使用していない。
    ------------------
    DepartmentCode NVARCHAR(16),

    ------------------
    -- ICD10 コード
    -- 処理種別がシステムコンテンツの場合、無視される。
    -- 将来使用のため。現在は使用していない。
    ------------------
    Icd10Code NVARCHAR(16),

    ------------------
    -- ドキュメント名
    -- Ex) 退院時サマリ
    ------------------
    DocumentName NVARCHAR(32),

    ------------------
    -- GPT Model 名
    -- Ex) gpt-35-turbo, gpt-4
    -- .env ファイルの AZURE_GPT_MODEL_NAME および、
    -- アプリケーション設定の同設定値に設定されているものと同じものを設定する
    ------------------
    GPTModelName VARCHAR(32),

    ------------------
    -- 処理種別
    -- 0: システムコンテンツ
    -- 1: SOAP と質問文からの生成
    -- 2: アレルギー・不適応反応
    -- 3: 退院時使用薬剤
    ------------------
    Kind INT, 

    ------------------
    -- カテゴリーの並び順
    -- Ex) 0
    -- Kind が 0:システムコンテンツのレコードでは無視される。
    ------------------
    OrderNo INT, 

    ------------------
    -- カテゴリー名
    -- Ex) 退院時状況
    -- Kind が 0:システムコンテンツのレコードでは無視される。
    ------------------
    CategoryName NVARCHAR(64), 

    ------------------
    -- サンプリング温度
    -- サンプリング温度を0〜1の間で指定します。高いサンプリング温度では、出現確率が均一化され、より多様な文章が生成される傾向があります。一方、低いサンプリング温度では、出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向があります。
    -- Kind が 
    -- 0:システムコンテンツ
    -- 2: アレルギー・不適応反応
    -- 3: 退院時使用薬剤
    -- のレコードでは無視される。
    ------------------
    Temperature FLOAT,

    ------------------
    -- 質問文
    -- Kind が 
    -- 2: アレルギー・不適応反応
    -- 3: 退院時使用薬剤
    -- のレコードでは無視される。
    ------------------
    Question NVARCHAR(4000), 

    ------------------
    -- 質問文サフィックス
    -- 質問文の後に付与する文字列
    -- Kind が 
    -- 2: アレルギー・不適応反応
    -- 3: 退院時使用薬剤
    -- のレコードでは無視される。
    ------------------
    QuestionSuffix NVARCHAR(4000), 

    ------------------
    -- 期待される応答の最大 Token 数
    -- Kind が 
    -- 2: アレルギー・不適応反応
    -- 3: 退院時使用薬剤
    -- のレコードでは無視される。
    ------------------
    ResponseMaxTokens int, 

    ------------------
    -- 使用する SOAP 項目を文字で指定する
    -- Kind が 
    -- 0: システムコンテンツ
    -- 2: アレルギー・不適応反応
    -- 3: 退院時使用薬剤
    -- のレコードでは無視される。
    -- Ex) sop ←この場合、 S, O, P の項目を使用することを意味する。
    -- S: Subjective
    -- O: Objective
    -- A: Assessment
    -- P: Plan
    -- B: Problem
    ------------------
    TargetSoapRecords CHAR(4), 

    ------------------
    -- アレルギー情報を使用するかどうか。
    -- 将来機能拡張に備えた項目である。
    -- 2023/10/02 現在使用していない。
    ------------------
    UseAllergyRecords BIT, 

    ------------------
    -- 退院時使用薬剤の情報を使用するかどうか
    -- 将来機能拡張に備えた項目である。
    -- 2023/10/02 現在使用していない。
    ------------------
    UseDischargeMedicineRecords BIT, 
    CreatedDateTime datetime,
    UpdatedDateTime datetime,
    IsDeleted bit,
) 

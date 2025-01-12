
INSERT INTO [dbo].[EXTBDH1] (PID,
DOC_NO,
FMT,
DOC_K,
DOC_TITLE,
DOCDATE,
ENDDATE,
ACTIVE_FLG,
PDOC_NO,
ODR_NO,
INSNO,
INSNM,
NG,
KA,
PID_NAME,
PID_SEX,
PID_BIRTH,
PID_AGE)
VALUES 
('8888000059','0A497E6023CCBA2014030315120300','XML','MD01',N'プログレスノート                                  ','20140218151100','0','1','0A497E6023CCBA2014030315120300','0','10',N'政府管本','2',' 01',N'松野　友美','2','19450612','680819'),
('8888000059','0A497E60250CDB2014030315132500','XML','MD01',N'プログレスノート                                  ','20140220151300','0','1','0A497E60250CDB2014030315132500','0','10',N'政府管本','2',' 01',N'松野　友美','2','19450612','680819'),
('8888001192','0A497E602D52782014030315222700','XML','MD01',N'プログレスノート                                  ','20140214152200','0','1','0A497E602D52782014030315222700','0','10',N'国保７家','2',' 01',N'小崎　円香','2','19860714','270717'),
('8888001192','0A497E602DC67F2014030315225700','XML','MD01',N'プログレスノート                                  ','20140217152200','0','1','0A497E602DC67F2014030315225700','0','10',N'国保７家','2',' 01',N'小崎　円香','2','19860714','270717'),
('8888000059','0A497E616562082014030117000703','ODR','H004',N'退院時処方                                        ','20140303777700','0','1','0A497E616562082014030117000700','38784','10',N'政府管本','2',' 02',N'松野　友美','2','19450612','680817'),
('8888001192','0A497E602B2C7B2014030315200701','ODR','H004',N'退院時処方                                        ','20140303777700','0','1','0A497E602B2C7B2014030315200700','41361','10',N'国保７家','2',' 02',N'小崎　円香','2','19860714','270717')
INSERT INTO [dbo].[EXTBDH1] (PID,
DOC_NO,
FMT,
DOC_K,
DOC_TITLE,
DOCDATE,
ENDDATE,
ACTIVE_FLG,
PDOC_NO,
ODR_NO,
INSNO,
INSNM,
NG,
KA,
PID_NAME,
PID_SEX,
PID_BIRTH,
PID_AGE)
VALUES 
('8888000059','0A497E60250CDB2014030415132500','XML','MD01',N'プログレスノート                                  ','20140221151300','0','1','0A497E60250CDB2014030415132500','0','10',N'政府管本','2',' 01',N'松野　友美','2','19450612','680819'),
('8888000059','0A497E60250CDB2014030515132500','XML','MD01',N'プログレスノート                                  ','20140222151300','0','1','0A497E60250CDB2014030515132500','0','10',N'政府管本','2',' 01',N'松野　友美','2','19450612','680819'),
('8888001192','0A497E602D52782014030415222700','XML','MD01',N'プログレスノート                                  ','20140218152200','0','1','0A497E602DC67F2014030415225700','0','10',N'国保７家','2',' 01',N'小崎　円香','2','19860714','270717'),
('8888001192','0A497E602D52782014030515222700','XML','MD01',N'プログレスノート                                  ','20140219152200','0','1','0A497E602DC67F2014030515225700','0','10',N'国保７家','2',' 01',N'小崎　円香','2','19860714','270717')
INSERT INTO EXTBDC1 (PID,
DOC_NO,
ACTIVE_FLG,
DOC_DATAX)
VALUES
('8888000059','0A497E6023CCBA2014030315120300','1',N'<DOC><DRPROGRESS><DOCHEAD></DOCHEAD><BODY><PLOBLEM id="1"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLOBLEM><SUBJECTIVE id="2"><FREEG><HTMLDATA>&lt;DIV&gt;＜主訴＞1週間前から便に血が混ざる。&lt;BR&gt;＜現病歴＞1週間前から便に血が混ざり、佐藤クリニックより大腸がんの疑いで紹介。当院内科受診、大腸ファイバで左下行結腸のがんと診断。&lt;BR&gt;＜既往歴＞現在糖尿病でオイグルコン2.5mg内服コントロール中。&lt;/DIV&gt;</HTMLDATA><FREE>＜主訴＞1週間前から便に血が混ざる。</FREE><FREE>＜現病歴＞1週間前から便に血が混ざり、佐藤クリニックより大腸がんの疑いで紹介。当院内科受診、大腸ファイバで左下行結腸のがんと診断。</FREE><FREE>＜既往歴＞現在糖尿病でオイグルコン2.5mg内服コントロール中。</FREE></FREEG></SUBJECTIVE><OBJECTIVE id="3"><FREEG><HTMLDATA>&lt;DIV&gt;＜入院時身体所見＞特記事項なし&lt;BR&gt;＜入院時検査所見＞特になし&lt;/DIV&gt;</HTMLDATA><FREE>＜入院時身体所見＞特記事項なし</FREE><FREE>＜入院時検査所見＞特になし</FREE></FREEG></OBJECTIVE><ASSESSMENT id="4"><FREEG><HTMLDATA></HTMLDATA></FREEG></ASSESSMENT><PLAN id="5"><FREEG><HTMLDATA>&lt;DIV&gt;＜治療方針＞手術目的で外科紹介&lt;/DIV&gt;</HTMLDATA><FREE>＜治療方針＞手術目的で外科紹介</FREE></FREEG></PLAN></BODY></DRPROGRESS></DOC>'),
('8888000059','0A497E60250CDB2014030315132500','1',N'<DOC><DRPROGRESS><DOCHEAD></DOCHEAD><BODY><PLOBLEM id="1"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLOBLEM><SUBJECTIVE id="2"><FREEG><HTMLDATA></HTMLDATA></FREEG></SUBJECTIVE><OBJECTIVE id="3"><FREEG><HTMLDATA></HTMLDATA></FREEG></OBJECTIVE><ASSESSMENT id="4"><FREEG><HTMLDATA>&lt;DIV&gt;＜臨床経過＞生検実施。生検でＧｒｏｕｐⅤ。ＳＭからＳＳ癌と考えられる。&lt;/DIV&gt;</HTMLDATA><FREE>＜臨床経過＞生検実施。生検でＧｒｏｕｐⅤ。ＳＭからＳＳ癌と考えられる。</FREE></FREEG></ASSESSMENT><PLAN id="5"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLAN></BODY></DRPROGRESS></DOC>'),
('8888001192','0A497E602D52782014030315222700','1',N'<DOC><DRPROGRESS><DOCHEAD></DOCHEAD><BODY><PLOBLEM id="1"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLOBLEM><SUBJECTIVE id="2"><FREEG><HTMLDATA>&lt;DIV&gt;1週間前から便に血が混ざる。佐藤クリニックより大腸がんの疑いで紹介。当院内科受診、大腸ファイバで左下行結腸のがんと診断。&lt;BR&gt;既往として現在糖尿病でオイグルコン2.5mg内服コントロール中。&lt;/DIV&gt;</HTMLDATA><FREE>1週間前から便に血が混ざる。佐藤クリニックより大腸がんの疑いで紹介。当院内科受診、大腸ファイバで左下行結腸のがんと診断。</FREE><FREE>既往として現在糖尿病でオイグルコン2.5mg内服コントロール中。</FREE></FREEG></SUBJECTIVE><OBJECTIVE id="3"><FREEG><HTMLDATA>&lt;DIV&gt;入院時の身体所見としては特記事項なし&lt;/DIV&gt;</HTMLDATA><FREE>入院時の身体所見としては特記事項なし</FREE></FREEG></OBJECTIVE><ASSESSMENT id="4"><FREEG><HTMLDATA></HTMLDATA></FREEG></ASSESSMENT><PLAN id="5"><FREEG><HTMLDATA>&lt;DIV&gt;手術目的で外科紹介の方針&lt;/DIV&gt;</HTMLDATA><FREE>手術目的で外科紹介の方針</FREE></FREEG></PLAN></BODY></DRPROGRESS></DOC>'),
('8888001192','0A497E602DC67F2014030315225700','1',N'<DOC><DRPROGRESS><DOCHEAD></DOCHEAD><BODY><PLOBLEM id="1"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLOBLEM><SUBJECTIVE id="2"><FREEG><HTMLDATA></HTMLDATA></FREEG></SUBJECTIVE><OBJECTIVE id="3"><FREEG><HTMLDATA></HTMLDATA></FREEG></OBJECTIVE><ASSESSMENT id="4"><FREEG><HTMLDATA>&lt;DIV&gt;生検実施。生検でＧｒｏｕｐⅤ。ＳＭからＳＳ癌と考えられる。&lt;/DIV&gt;</HTMLDATA><FREE>生検実施。生検でＧｒｏｕｐⅤ。ＳＭからＳＳ癌と考えられる。</FREE></FREEG></ASSESSMENT><PLAN id="5"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLAN></BODY></DRPROGRESS></DOC>')

INSERT INTO EXTBDC1 (PID,
DOC_NO,
ACTIVE_FLG,
DOC_DATAX)
VALUES
('8888000059','0A497E60250CDB2014030415132500','1',N'<DOC><DRPROGRESS><DOCHEAD></DOCHEAD><BODY><PLOBLEM id="1"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLOBLEM><SUBJECTIVE id="2"><FREEG><HTMLDATA></HTMLDATA></FREEG></SUBJECTIVE><OBJECTIVE id="3"><FREEG><HTMLDATA></HTMLDATA></FREEG></OBJECTIVE><ASSESSMENT id="4"><FREEG><HTMLDATA>&lt;DIV&gt;＜臨床経過＞生検実施。生検でＧｒｏｕｐⅤ。ＳＭからＳＳ癌と考えられる。&lt;/DIV&gt;</HTMLDATA><FREE>＜臨床経過＞生検実施。生検でＧｒｏｕｐⅤ。ＳＭからＳＳ癌と考えられる。追記１。</FREE></FREEG></ASSESSMENT><PLAN id="5"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLAN></BODY></DRPROGRESS></DOC>'),
('8888000059','0A497E60250CDB2014030515132500','1',N'<DOC><DRPROGRESS><DOCHEAD></DOCHEAD><BODY><PLOBLEM id="1"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLOBLEM><SUBJECTIVE id="2"><FREEG><HTMLDATA></HTMLDATA></FREEG></SUBJECTIVE><OBJECTIVE id="3"><FREEG><HTMLDATA></HTMLDATA></FREEG></OBJECTIVE><ASSESSMENT id="4"><FREEG><HTMLDATA>&lt;DIV&gt;＜臨床経過＞生検実施。生検でＧｒｏｕｐⅤ。ＳＭからＳＳ癌と考えられる。&lt;/DIV&gt;</HTMLDATA><FREE>＜臨床経過＞生検実施。生検でＧｒｏｕｐⅤ。ＳＭからＳＳ癌と考えられる。追記１。追記２。</FREE></FREEG></ASSESSMENT><PLAN id="5"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLAN></BODY></DRPROGRESS></DOC>'),
('8888001192','0A497E602D52782014030415222700','1',N'<DOC><DRPROGRESS><DOCHEAD></DOCHEAD><BODY><PLOBLEM id="1"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLOBLEM><SUBJECTIVE id="2"><FREEG><HTMLDATA>&lt;DIV&gt;1週間前から便に血が混ざる。佐藤クリニックより大腸がんの疑いで紹介。当院内科受診、大腸ファイバで左下行結腸のがんと診断。&lt;BR&gt;既往として現在糖尿病でオイグルコン2.5mg内服コントロール中。&lt;/DIV&gt;</HTMLDATA><FREE>1週間前から便に血が混ざる。佐藤クリニックより大腸がんの疑いで紹介。当院内科受診、大腸ファイバで左下行結腸のがんと診断。</FREE><FREE>既往として現在糖尿病でオイグルコン2.5mg内服コントロール中。</FREE></FREEG></SUBJECTIVE><OBJECTIVE id="3"><FREEG><HTMLDATA>&lt;DIV&gt;入院時の身体所見としては特記事項なし&lt;/DIV&gt;</HTMLDATA><FREE>入院時の身体所見としては特記事項なし</FREE></FREEG></OBJECTIVE><ASSESSMENT id="4"><FREEG><HTMLDATA></HTMLDATA></FREEG></ASSESSMENT><PLAN id="5"><FREEG><HTMLDATA>&lt;DIV&gt;手術目的で外科紹介の方針&lt;/DIV&gt;</HTMLDATA><FREE>手術目的で外科紹介の方針。追記１。</FREE></FREEG></PLAN><PLOBLEM><FREEG><FREE>テストプロブレム。</FREE></FREEG></PLOBLEM></BODY></DRPROGRESS></DOC>'),
('8888001192','0A497E602D52782014030515222700','1',N'<DOC><DRPROGRESS><DOCHEAD></DOCHEAD><BODY><PLOBLEM id="1"><FREEG><HTMLDATA></HTMLDATA></FREEG></PLOBLEM><SUBJECTIVE id="2"><FREEG><HTMLDATA>&lt;DIV&gt;1週間前から便に血が混ざる。佐藤クリニックより大腸がんの疑いで紹介。当院内科受診、大腸ファイバで左下行結腸のがんと診断。&lt;BR&gt;既往として現在糖尿病でオイグルコン2.5mg内服コントロール中。&lt;/DIV&gt;</HTMLDATA><FREE>1週間前から便に血が混ざる。佐藤クリニックより大腸がんの疑いで紹介。当院内科受診、大腸ファイバで左下行結腸のがんと診断。</FREE><FREE>既往として現在糖尿病でオイグルコン2.5mg内服コントロール中。</FREE></FREEG></SUBJECTIVE><OBJECTIVE id="3"><FREEG><HTMLDATA>&lt;DIV&gt;入院時の身体所見としては特記事項なし&lt;/DIV&gt;</HTMLDATA><FREE>入院時の身体所見としては特記事項なし</FREE></FREEG></OBJECTIVE><ASSESSMENT id="4"><FREEG><HTMLDATA></HTMLDATA></FREEG></ASSESSMENT><PLAN id="5"><FREEG><HTMLDATA>&lt;DIV&gt;手術目的で外科紹介の方針&lt;/DIV&gt;</HTMLDATA><FREE>手術目的で外科紹介の方針</FREE></FREEG></PLAN><PLOBLEM><FREEG><FREE>テストプロブレム。追記１。</FREE></FREEG></PLOBLEM></BODY></DRPROGRESS></DOC>')

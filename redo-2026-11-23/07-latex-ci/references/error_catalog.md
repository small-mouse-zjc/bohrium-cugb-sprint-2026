# LaTeX 报错处置手册

按"症状 → 根因 → 修法 → 怎么确认修好了"组织。`latex_ci.py` 的 `fix_plan.type`
与本表标题一一对应，可直接对照执行。

## 1. missing_package — 缺宏包

- 症状：`! LaTeX Error: File \`xxx.sty' not found.`，随后 `Emergency stop`，无 PDF。
- 根因：发行版没装该包、包名拼错、或模板依赖了私有包。
- 修法：① 核对拼写；② 换等价包（`subfig`↔`subcaption`、`epsfig`↔`graphicx`、
  `ulem`↔`soul`）；③ 若该包只为一处命令服务，改用基础命令或删掉该用法。
- 确认：重跑后 `missing_files` 为空且出 PDF。

## 2. missing_font — 缺字体/字体形状

- 症状：`Font ... not loadable` / `Font shape ... undefined` / `mktexpk` 报错。
- 根因：镜像缺该字体族，或用了 `fontspec` 指定本机不存在的字体。
- 修法：换已装字体（TeX Gyre 系列、`ctex` 自带中文字体）；或退回默认字体族，
  用 `\renewcommand{\familydefault}` 统一。
- 确认：日志无 `Font ... not loadable`；PDF 文本可抽取。

## 3. encoding — 编码/字符

- 症状：`Unicode character ... not set up` / `inputenc Error` / 乱码。
- 根因：源文件非 UTF-8，或引擎不支持该字符。
- 修法：源文件转 UTF-8；中文用 `xelatex`（或 `lualatex`）+ `ctex`；生僻符号用等价字符。
- 确认：编译无该报错，PDF 中该字符显示正常。

## 4. math_mode — 数学模式未闭合

- 症状：`Missing $ inserted` / `Display math should end with $$`。
- 根因：`$` 单双不成对；公式环境里出现空行；`_`/`^` 用在文本模式。
- 修法：补齐 `$`；`equation`/`align` 内不留空行；文本中的下划线转义为 `\_`。
- 确认：日志无该报错，公式渲染正确、编号连续。

## 5. alignment — 单元格多于列声明

- 症状：`Extra alignment tab has been changed to \cr`。
- 根因：某行 `&` 数量超过 `{lll}` 声明列数。
- 修法：收窄列声明，或合并/删除多余单元格；跨列表头用 `\multicolumn{n}{c}{...}`。
- 确认：日志无该 warning，表格无错行。

## 6. alignment_silent — 单元格少于列声明（编译不报错）

- 症状：**无任何报错**，PDF 正常产出，但表格右侧出现空列。
- 根因：行内 `&` 少于列声明数。
- 修法：补齐单元格（可填空或 `--`），或把列声明改窄。
- 确认：`staticcheck` 的 `alignment_silent` 清零；PDF 表格无空白列。
- 备注：这是本 Skill 与"只看编译是否通过"的关键区别，**必须**靠静态检查捕获。

## 7. undefined_command — 命令未定义

- 症状：`! Undefined control sequence.` + `l.N`。
- 根因：命令拼错，或所属宏包未加载（`\toprule` 需 `booktabs`、`\eqref` 需 `amsmath`、
  `\includegraphics` 需 `graphicx`、`\SI` 需 `siunitx`）。
- 修法：按上表补 `\usepackage`；私有命令确认是否在模板 `.cls` 中已定义。
- 确认：该行不再报 `Undefined control sequence`。

## 8. undefined_env — 环境未定义或嵌套错位

- 症状：`Environment xxx undefined` / `\begin{aaa} on input line N ended by \end{bbb}`。
- 根因：环境名拼错、宏包未加载，或 begin/end 交叉嵌套。
- 修法：按"后开先关"重排；`figure` 里不要套 `table`。
- 确认：`staticcheck` 的环境配对零错误。

## 9. undefined_ref — 引用指向不存在的 label

- 症状：`LaTeX Warning: Reference \`k' ... undefined`；正文出现 `??`。
- 根因：label 未定义、拼错，或第一轮尚未写入 `.aux`。
- 修法：第一轮出现属正常，第二三轮仍在才需处理——补 `\label{k}` 或删/改该引用。
- 确认：`converged=true`，PDF 中无 `??`。

## 10. undefined_cite — 文献 key 不存在

- 症状：`Citation \`k' ... undefined`；正文 `[?]`。
- 根因：`.bib` 无该 key、`\bibliography{}` 文件名错、bibtex 未跑成功。
- 修法：补条目或改 key；确认 `.bib` 文件名与 `\bibliography{}` 一致；查 `.blg` 日志。
- 确认：`.bbl` 含该条目，PDF 引用正常显示，无 `[?]`。

## 11. runaway — 参数扫描失控

- 症状：`Runaway argument?` / `File ended while scanning use of ...`。
- 根因：花括号或环境未闭合，TeX 一路吃到文件尾。
- 修法：从报错行**往前**找第一个未配对的 `{`；常见于多行公式、`\newcommand` 定义。
- 确认：不再出现该错误，后续错误一并消失。

## 12. brace — 花括号不平衡

- 症状：`Too many }'s` / `Missing } inserted`。
- 根因：多写或少写 `}`；`\{`/`\}` 被误当分组。
- 修法：逐行核对；`\{` 是转义字符，不参与配对。
- 确认：编译通过且命令参数渲染正确。

## 13. fatal — 级联中断

- 症状：`Emergency stop` / `Fatal error occurred, no output PDF file produced`。
- 根因：**不是根因**，是上面某个错误导致的终止。
- 修法：只看它前面第一条 `!` 错误，修那条；不要从 `Emergency stop` 本身下手。
- 确认：前一条错误消失后，PDF 正常产出。

## 14. table_overflow — 表格溢出（版式）

- 症状：`Overfull \hbox (xx.xxpt too wide) ... at lines a--b`。
- 根因：列太宽或内容太长，超出 `\textwidth`。
- 修法：`\small`/`\footnotesize`、`tabularx` + `X` 列、`\resizebox`（慎用，会缩字）、
  或拆成两表。
- 确认：Overfull 量降到可接受范围，PDF 无裁切。

## 15. template_class_missing — 模板类缺失

- 症状：`Class \`xxx.cls' not found`。
- 根因：投稿模板未安装或需从期刊站点获取。
- 修法：放 `.cls` 到工程根（与 `main.tex` 同级）；不可得时换同族模板并**如实记录替换**。
- 确认：`\documentclass{xxx}` 不再报错；版式符合模板必填项。

## 16. duplicate_label — 标签重复

- 症状：`LaTeX Warning: Label \`k' multiply defined`。
- 根因：同一 key 在多个文件重复定义。
- 修法：改 key（建议 `sec:/fig:/tab:/eq:` 前缀 + 语义名）。
- 确认：warning 消失，交叉引用指向正确。

## 17. toc_not_converged — 目录/编号未收敛

- 症状：目录页码与实际不符，`rerunfilecheck` 提示再跑。
- 根因：需要额外一轮编译写 `.toc`。
- 修法：再跑一轮引擎（`latex_ci.py` 已自动跑到收敛）。
- 确认：`converged=true` 且页码正确。

## 18. bib_style_missing — 文献样式缺失

- 症状：`I couldn't open style file xxx.bst`。
- 根因：`\bibliographystyle{}` 指定的 `.bst` 不在镜像里。
- 修法：换内置样式（`plain`/`unsrt`/`alpha`/`abbrv`）或把 `.bst` 放进工程。
- 确认：bibtex 日志无该错误，`.bbl` 生成。

## 19. permission_denied — 写权限

- 症状：`I can't write on file ...`。
- 根因：构建目录只读，或输出路径不可写。
- 修法：在 `/app/work` 下构建，产物拷到 `/app/output`；不要原地写系统目录。
- 确认：构建目录可写，PDF 落在 `/app/output`。

## 20. stale_artifacts — 旧产物污染

- 症状：改了源码却没生效；或 PDF 时间是旧的。
- 根因：残留 `.aux/.bbl/.pdf` 让首轮就"收敛"。
- 修法：编译前清理构建物（`latex_ci.py` 默认已清），并核对 PDF 的 mtime。
- 确认：`cleaned_before_build` 列出被删文件；PDF 字节数与本次一致。

# 基于 LOPIT 空间蛋白质组学的蛋白亚细胞定位预测

中国药科大学 · 药学硕士 ·《计算机生物学与人工智能》课程项目。

**提交仓库：** https://github.com/shuyasheng414-bot/spatial-proteomics-course  
**版本标签：** `v1.0.0`

本项目用公开真实分馏质谱数据，完成数据质控、PCA、SVM/随机森林比较、独立测试评估及未标注蛋白候选定位预测。中文分析和已执行图表全部集中在 **[spatial_proteomics.ipynb](spatial_proteomics.ipynb)**。

> 使用对象是果蝇 LOPIT 第一重复，属于亚细胞空间蛋白质组学，不是人类组织成像数据，也不是课题组实验结果。候选预测需要验证。

## 作业要求对应

| 要求 | 本项目实现 |
|---|---|
| 自己的 Git 项目 | 本地 Git 仓库；发布至个人 GitHub 后提交仓库链接 |
| Jupyter 展示结果 | `spatial_proteomics.ipynb`，保留真实运行输出 |
| 可复现 | 原始数据随仓库保存、固定种子、依赖版本、SHA-256、一键执行脚本 |
| 版本管理与 tag | Git 提交历史和 `v1.0.0` 标签 |
| 至少 2 个文件，总行数 ≥100 | 多文件组织，单独 `src/analysis.py` 有 197 行 |
| README.MD 说明 | 本文件 `README.md`（标准 Markdown README 命名） |

## 科学问题与数据

研究问题：能否利用蛋白在四个分馏通道中的相对丰度，区分其亚细胞定位或蛋白复合体类别？

- 来源：Tan DJ et al. (2009), *Mapping organelle proteins and protein complexes in Drosophila melanogaster*. DOI: [10.1021/pr800866n](https://doi.org/10.1021/pr800866n)。
- 整理仓库：[pRolocdata](https://github.com/lgatto/pRolocdata)。固定版本、下载地址及校验值见 [data/provenance.json](data/provenance.json)。
- 数据：888 个蛋白，4 个 iTRAQ 通道；144 个参考标记，744 个未标记蛋白。
- 输入：仅 `area 114`、`area 115`、`area 116`、`area 117`。
- 标签：CSV 的 `pd.markers`。该列是原有标记及 phenoDisco 辅助发现后经 UniProtKB/文献核查的补充标记；不是本项目新验证的标签，也不等同于当前上游 RData 中所有标记版本。
- 不使用 `PLS-DA classification` 或 `pd.2013` 作为特征或标签，避免学习已有预测结果。
- 仅 4 个标记的 Peroxisome 类别不纳入建模；其余 140 个标记覆盖 10 类，包括细胞器和蛋白复合体。未将稀有类当作 unknown。

## 方法

1. 验证 ID 唯一、强度非负且无缺失，进行逐蛋白行归一化。
2. 固定随机种子 42，对合格标记分层划分训练集和独立测试集（70%/30%）。
3. 在训练集内做三折交叉验证，比较多数类基线、RBF-SVM、随机森林。
4. SVM 的标准化通过 Pipeline 在各训练折内拟合；按交叉验证 Macro-F1 选择分类器，不按测试分数选模型。
5. 独立测试报告 Accuracy、Balanced accuracy、Macro-F1、每类指标和混淆矩阵。
6. PCA 及其标准化只在训练标记上拟合，用于可视化而非分类输入。
7. 完成测试后，在全部合格标记上重新训练，为 unknown 蛋白生成候选定位。

算法参数预先固定，未做测试集调参。该设计是小样本课程练习，不是严格跨批次或前瞻验证。

## 文件结构

```text
spatial_proteomics.ipynb       中文主报告，含已执行输出
src/analysis.py               质控、划分、训练、评估、作图、候选预测
reproduce.py                  一键执行 Notebook 并导出 HTML
download_data.py              可选：按固定版本重新下载并校验数据
requirements.txt              核心直接依赖，固定版本
requirements-lock.txt         本次 Windows / Python 3.12 环境的完整依赖
data/                         真实数据、校验信息及上游文档/脚本
results/                      图表、指标、数据划分及预测结果
SUBMISSION.md                 GitHub 发布与提交说明
STUDY_GUIDE.md                方法理解与课堂问答
LICENSE                       GPL-2.0 许可证正文
```

## 安装与复现

建议 Python 3.12。首次安装依赖需要联网；安装好环境后，分析直接读取仓库内数据，不再依赖数据网站在线。

### Windows PowerShell

在项目根目录打开终端，执行：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe reproduce.py
```

### macOS / Linux

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python reproduce.py
```

`requirements-lock.txt` 是本次验证环境的完整快照；跨平台使用固定直接依赖的 `requirements.txt`，底层库差异可能造成微小数值差异。无需全局注册 Jupyter 内核；脚本使用当前解释器临时创建内核。

执行完成后，打开 `spatial_proteomics.ipynb` 或 `results/report.html` 查看结果。GitHub 可直接预览已保存输出的 Notebook。若想逐格交互运行，可用 VS Code 的 Jupyter 扩展选择此虚拟环境，或另行安装 JupyterLab。

可选重新下载数据：

```powershell
.\.venv\Scripts\python.exe download_data.py
```

下载地址固定到上游提交，并校验 SHA-256；若校验失败则停止，不悄悄替换数据。

## 验证与结果解释

Notebook 包含训练/测试 ID 互斥检查、测试分数重算、预测数量与类别检查。实际指标由代码写入 `results/metrics.json`，详细结果见 Notebook，避免维护多个手写分数。

`results/split.csv` 记录每个蛋白属于 train、test、unlabelled 或 rare_class_excluded；`test_predictions.csv` 可逐条审查测试结果；`unlabelled_predictions.csv` 保存候选定位，不代表经过独立验证的发现。

需注意：

- 参考标签曾利用该数据的结构进行筛选，留出测试仍可能带有历史选择偏差。
- 类别不均衡、每类测试数量小，同一复合体成员相关；一次随机划分不等于稳健泛化证据。
- 只使用一个重复和四个通道，不能检验跨实验、跨物种或药物扰动后的迁移能力。
- 模型只会在训练类别中选择，不识别未知细胞器和多定位；不输出未经校准的置信概率。
- 果蝇数据的预测不能直接用于人类药物疗效判断。

## 版本与提交

提交前执行 `git log --oneline`、`git tag` 和 `git status`，确认提交历史、`v1.0.0` 与工作区状态。GitHub 发布步骤见 [SUBMISSION.md](SUBMISSION.md)。应提交实际仓库链接，不能提交本地路径。

本地仓库若使用 `Course Project <course-project@example.invalid>`，这是无个人身份信息的占位 Git 提交者，不代表学生姓名；发布前可按提交说明设置自己的 Git 身份。请在提交前按教师要求补充姓名、学号等信息，并遵守课程的 AI 辅助使用规定。

## 来源与许可

上游 pRolocdata 的 DESCRIPTION 声明 GPL-2，本项目保留来源说明、上游脚本及 GPL-2.0 文本；新增代码按 GPL-2.0 分发。原始科研数据和论文应始终引用原作者，不应署名为本人采集。项目代码和中文说明由 AI 辅助整理，使用者应检查、理解并按课程要求说明辅助工具使用情况。

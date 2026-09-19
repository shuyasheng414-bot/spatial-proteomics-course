# GitHub 发布与提交

## 本次提交地址

仓库：https://github.com/shuyasheng414-bot/spatial-proteomics-course

Notebook：https://github.com/shuyasheng414-bot/spatial-proteomics-course/blob/main/spatial_proteomics.ipynb

固定版本：https://github.com/shuyasheng414-bot/spatial-proteomics-course/tree/v1.0.0

本次通过 GitHub 网页发布；网页提交历史与原本地仓库历史不同，不要向已发布仓库强制推送旧本地历史。继续开发请重新克隆上述仓库。以下为通用发布方法说明。

## 当前交付包含什么

本地项目包含已执行 Notebook、原始数据、分析代码、依赖、结果和 Git 版本记录。仓库还需要推送至你自己的 GitHub 账号，才会获得老师可以访问的提交链接。

## 使用已有本地仓库发布

1. 登录 GitHub，创建空仓库，推荐名称 `spatial-proteomics-course`。为了让老师直接打开，可选择 Public；如选 Private，需要给老师访问权限。不要勾选自动生成 README、LICENSE 或 .gitignore。
2. 在本项目目录打开终端，检查历史：

```bash
git log --oneline
git tag
git status
```

3. 按个人信息设置后续提交身份（将中文占位内容换成你自己的信息，不要原样复制）：

```bash
git config user.name "你的 GitHub 用户名"
git config user.email "你的 GitHub 已验证邮箱或 noreply 邮箱"
```

4. 在 GitHub 新仓库页面复制 HTTPS 地址，并执行下面命令。`YOUR_USERNAME` 是需要替换的占位符，不是实际发布链接：

```bash
git remote add origin https://github.com/YOUR_USERNAME/spatial-proteomics-course.git
git push -u origin main
git push origin v1.0.0
```

HTTPS 身份验证应通过 GitHub 的正规登录或凭据管理器完成，不要把密码或访问令牌写进代码、Notebook 或 README。

5. 用浏览器打开仓库，确认 `spatial_proteomics.ipynb` 可显示图表，且 Tags 中存在 `v1.0.0`。

## 提交什么链接

建议提交仓库主页链接，并在备注写：

> 项目：基于 LOPIT 空间蛋白质组学的蛋白亚细胞定位预测。结果入口：spatial_proteomics.ipynb；版本标签：v1.0.0；复现方法见 README.md。

若老师要求固定版本，可提交 GitHub 中 `v1.0.0` 标签页面的链接。实际链接以发布后的 GitHub 页面为准。

## 如果只使用不含 .git 的源码压缩包

源码压缩包可直接复现，但不会保存 Git 历史。需要初始化个人 Git 仓库：

```bash
git init -b main
git config user.name "你的 GitHub 用户名"
git config user.email "你的 GitHub 已验证邮箱或 noreply 邮箱"
git add .
git commit -m "Add reproducible spatial proteomics analysis"
git tag -a v1.0.0 -m "Course submission v1.0.0"
```

之后按上述步骤添加远程仓库并推送。交付目录中的 `.bundle` 文件另行保存了本地 Git 提交和标签，可使用 `git clone 文件路径 项目目录` 恢复历史。

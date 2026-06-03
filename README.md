# Providence Knowledge Base

私人知识入口，部署到 <https://knowledge.prov1dence.top/>。

## 用法

```bash
python scripts/build.py
open dist/index.html
```

## 添加学习页

1. 把单页 HTML 放到 `pages/`。
2. 在 `data/pages.json` 添加标题、分类、标签和路径。
3. 如果有外部资料，在 `data/links.json` 添加链接。
4. push 到 `master` 后，GitHub Actions 会构建 `dist/` 并发布到 GitHub Pages。

## 部署

`.github/workflows/pages.yml` 使用 GitHub Pages 官方 Actions：

- `actions/upload-pages-artifact`
- `actions/deploy-pages`

自定义域名由仓库根目录 `CNAME` 指定：`knowledge.prov1dence.top`。

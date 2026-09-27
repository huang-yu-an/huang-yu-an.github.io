#!/usr/bin/env python3
"""
Generate all HTML pages for Yu-An Huang's personal academic website.
Produces root index.html (language picker), /zh/* pages, and /en/* pages.
"""

import os
from pathlib import Path

ROOT = Path('/Users/huang/WorkBuddy/2026-09-27-16-20-44/yu-anhuang.github.io')
PHOTO = "assets/img/avatar.svg"  # drop a real photo at assets/img/photo.jpg to swap

# ----------------------------------------------------------------------
# Navigation definitions
# ----------------------------------------------------------------------
NAV_ZH = [
    ("index.html",   "主页",     "home"),
    ("publications.html", "论文", "publications"),
    ("research.html","研究",     "research"),
    ("cv.html",      "简历",     "cv"),
    ("teaching.html","教学",     "teaching"),
    ("news.html",    "动态",     "news"),
    ("contact.html", "联系",     "contact"),
]

NAV_EN = [
    ("index.html",   "Home",        "home"),
    ("publications.html", "Publications", "publications"),
    ("research.html","Research",    "research"),
    ("cv.html",      "CV",          "cv"),
    ("teaching.html","Teaching",    "teaching"),
    ("news.html",    "News",        "news"),
    ("contact.html", "Contact",     "contact"),
]


def nav_html(items, current, lang, base):
    """Generate top navigation HTML."""
    links = []
    for href, label, key in items:
        cls = ' class="active"' if key == current else ''
        links.append(f'        <li><a href="{base}{href}"{cls}>{label}</a></li>')
    other = "en" if lang == "zh" else "zh"
    other_label = "EN" if lang == "zh" else "中"
    return f"""      <ul class="nav-links">
{chr(10).join(links)}
      </ul>
      <div class="nav-lang">
        <a href="../{lang}/" class="active">{('中' if lang == 'zh' else 'EN')}</a>
        <a href="../{other}/">{other_label}</a>
      </div>"""


def page_template(lang, current_page, title, body, description=""):
    """Wrap content in full HTML document."""
    items = NAV_ZH if lang == "zh" else NAV_EN
    base = ""  # pages live directly under /zh/ or /en/, no extra prefix needed
    nav = nav_html(items, current_page, lang, base)
    html_lang = "zh-CN" if lang == "zh" else "en"
    full_title = title if not description else f"{title} · Yu-An Huang"
    desc_attr = f' content="{description}"' if description else ""
    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{full_title}</title>
  <meta name="description"{desc_attr}>
  <meta name="author" content="Yu-An Huang">
  <link rel="stylesheet" href="../assets/css/style.css">
  <link rel="icon" type="image/svg+xml" href="../assets/img/favicon.svg">
</head>
<body>
  <header class="site-header">
    <nav class="nav">
      <a class="nav-brand" href="./">{'黄裕安' if lang == 'zh' else 'Yu-An Huang'}</a>
{nav}
    </nav>
  </header>
  <main>
    <div class="container">
{body}
    </div>
  </main>
  <footer class="site-footer">
    <p>© 2026 Yu-An Huang · {'西北工业大学计算机学院' if lang == 'zh' else 'School of Computer Science, Northwestern Polytechnical University'}</p>
    <p><a href="https://github.com/yu-anhuang/yu-anhuang.github.io">Source on GitHub</a> · {'最后更新' if lang == 'zh' else 'Last updated'}: Sep 2026</p>
  </footer>
</body>
</html>
"""


# ----------------------------------------------------------------------
# Page contents (separated by language)
# ----------------------------------------------------------------------

def hero_html(lang):
    """Hero section shared by home pages."""
    if lang == "zh":
        return f"""
<section class="hero">
  <div>
    <h1 class="hero-name">黄裕安</h1>
    <div class="hero-name-en">Yu-An Huang, Ph.D.</div>
    <div class="hero-title">长聘教授 · 博士生导师</div>
    <div class="hero-affiliation">西北工业大学 · 计算机学院</div>
    <div class="hero-contact">
      <span><a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a></span>
      <span>办公室 · 长安校区</span>
    </div>
    <p style="margin-top:1.2em;">
      <a class="tag" href="./cv.html">查看完整简历 →</a>
      <a class="tag" href="./publications.html">122 篇论文 →</a>
    </p>
  </div>
  <img class="hero-portrait" src="../assets/img/avatar.svg" alt="Yu-An Huang">
</section>
"""
    return f"""
<section class="hero">
  <div>
    <h1 class="hero-name">Yu-An Huang</h1>
    <div class="hero-name-en">黄裕安, Ph.D.</div>
    <div class="hero-title">Tenured Professor · Ph.D. Advisor</div>
    <div class="hero-affiliation">School of Computer Science · Northwestern Polytechnical University</div>
    <div class="hero-contact">
      <span><a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a></span>
      <span>Office · Chang'an Campus</span>
    </div>
    <p style="margin-top:1.2em;">
      <a class="tag" href="./cv.html">Full CV →</a>
      <a class="tag" href="./publications.html">122 papers →</a>
    </p>
  </div>
  <img class="hero-portrait" src="../assets/img/avatar.svg" alt="Yu-An Huang">
</section>
"""


def home_body(lang):
    if lang == "zh":
        return hero_html("zh") + f"""
<div class="home-grid">
  <div>
    <h2 id="about">关于我</h2>
    <p>
      我是<a href="https://jsj.nwpu.edu.cn/" target="_blank" rel="noopener">西北工业大学计算机学院</a>长聘教授、博士生导师。
      2020 年博士毕业于<a href="https://www.polyu.edu.hk/" target="_blank" rel="noopener">香港理工大学</a>电子计算学系，
      主要研究方向是<strong>生物医学大数据、计算生物学、人工智能与数据挖掘</strong>。
    </p>
    <p>
      主持国家青年科学基金项目 B 类（国家优青）、面上项目 1 项、青年科学基金 C 类、省级自然基金 2 项。
      近年来在 <em>Genome Biology</em>、<em>Advanced Science</em>、<em>Communications Biology</em>、<em>Bioinformatics</em>、
      <em>PLoS Computational Biology</em>、<em>MIA</em>、<em>IEEE TNNLS / TCYB / TMI / TCBB / TBD / JBHI / TFS</em>
      等学术期刊及 AAAI、KDD、BIBM 等国际会议上发表论文 70 余篇，
      Google 引用 4000 余次，H-index 37。
    </p>

    <h2 id="news">最新动态</h2>
    <ul class="news-list">
      <li><span class="date">2026 · 09</span><span class="body">更新个人主页，欢迎访问！</span></li>
      <li><span class="date">2026 · 09</span><span class="body">论文 <em>scBIT</em> 被 <strong>IEEE TMI</strong> 接收（已上线）。</span></li>
      <li><span class="date">2025 · 12</span><span class="body">论文 <em>DAGFormer</em> 被 <strong>PLoS Computational Biology</strong> 接收。</span></li>
      <li><span class="date">2025 · 11</span><span class="body">论文 <em>scKAN</em> 被 <strong>Genome Biology</strong> 接收。</span></li>
      <li><span class="date">2025 · 09</span><span class="body">开始招收 2027 级硕士（推免）与博士研究生，欢迎邮件联系。</span></li>
    </ul>

    <h2 id="recruiting">招生信息</h2>
    <div class="card">
      <h3>欢迎 2027 级硕士 / 博士研究生</h3>
      <p>
        目前招收 2027 级<strong>硕士（推免）</strong>和<strong>博士</strong>研究生，名额充裕。
        研究方向包括单细胞数据分析、计算生物学、AI for Healthcare、生物信息学、图神经网络等。
      </p>
      <p>欢迎感兴趣的同学随时邮件联系：<a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a></p>
    </div>
  </div>

  <aside class="sidebar">
    <h3>研究方向</h3>
    <ul>
      <li>生物医学大数据</li>
      <li>计算生物学</li>
      <li>单细胞 RNA 测序</li>
      <li>AI for Healthcare</li>
      <li>图神经网络</li>
      <li>数据挖掘</li>
    </ul>

    <h3>学术兼职</h3>
    <ul>
      <li><em>J. Comput. Biophys. Chem.</em> 客座编辑</li>
      <li><em>BMC Artificial Intelligence</em> 编委</li>
      <li><em>Interdisciplinary Medicine</em> 青年编委</li>
      <li>BIBM、ICIC 程序委员</li>
    </ul>

    <h3>快速链接</h3>
    <ul class="quick-links">
      <li><a href="https://scholar.google.com/" target="_blank" rel="noopener">Google Scholar</a></li>
      <li><a href="https://orcid.org/" target="_blank" rel="noopener">ORCID</a></li>
      <li><a href="https://github.com/" target="_blank" rel="noopener">GitHub</a></li>
      <li><a href="https://www.semanticscholar.org/" target="_blank" rel="noopener">Semantic Scholar</a></li>
      <li><a href="mailto:yuanhuang@nwpu.edu.cn">Email</a></li>
    </ul>

    <h3>联系方式</h3>
    <ul>
      <li>📧 <a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a></li>
      <li>🏛️ 西北工业大学计算机学院</li>
      <li>📍 西安市长安区</li>
    </ul>
  </aside>
</div>
"""
    return hero_html("en") + f"""
<div class="home-grid">
  <div>
    <h2 id="about">About Me</h2>
    <p>
      I am a tenured professor and Ph.D. advisor at the
      <a href="https://jsj.nwpu.edu.cn/" target="_blank" rel="noopener">School of Computer Science</a>,
      <a href="https://www.nwpu.edu.cn/" target="_blank" rel="noopener">Northwestern Polytechnical University</a>.
      I received my Ph.D. in Electronic Computing from
      <a href="https://www.polyu.edu.hk/" target="_blank" rel="noopener">The Hong Kong Polytechnic University</a> in 2020.
      My research focuses on <strong>biomedical big data, computational biology, AI, and data mining</strong>.
    </p>
    <p>
      I am a principal investigator on several grants including the National Outstanding Youth Science Foundation (B),
      a General Program of NSFC, the Youth Science Fund (C), and two provincial Natural Science Foundations.
      I have published 70+ papers in venues including <em>Genome Biology</em>, <em>Advanced Science</em>,
      <em>Communications Biology</em>, <em>Bioinformatics</em>, <em>PLoS Computational Biology</em>, <em>MIA</em>,
      <em>IEEE TNNLS / TCYB / TMI / TCBB / TBD / JBHI / TFS</em>, and at AAAI, KDD, BIBM and others.
      Google Scholar citations exceed 4,000 with an H-index of 37.
    </p>

    <h2 id="news">Recent News</h2>
    <ul class="news-list">
      <li><span class="date">2026 · 09</span><span class="body">Personal website launched — welcome!</span></li>
      <li><span class="date">2026 · 09</span><span class="body">Paper <em>scBIT</em> accepted to <strong>IEEE TMI</strong>.</span></li>
      <li><span class="date">2025 · 12</span><span class="body">Paper <em>DAGFormer</em> accepted to <strong>PLoS Computational Biology</strong>.</span></li>
      <li><span class="date">2025 · 11</span><span class="body">Paper <em>scKAN</em> accepted to <strong>Genome Biology</strong>.</span></li>
      <li><span class="date">2025 · 09</span><span class="body">Recruiting Master's (推免) and Ph.D. students for the 2027 cohort.</span></li>
    </ul>

    <h2 id="recruiting">Recruiting</h2>
    <div class="card">
      <h3>Master's & Ph.D. Positions for Fall 2027</h3>
      <p>
        I am actively recruiting <strong>Master's (推免)</strong> and <strong>Ph.D.</strong> students for Fall 2027.
        Research areas include single-cell data analysis, computational biology, AI for healthcare,
        bioinformatics, and graph neural networks.
      </p>
      <p>Prospective students are warmly encouraged to email me at
         <a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a>.</p>
    </div>
  </div>

  <aside class="sidebar">
    <h3>Research Interests</h3>
    <ul>
      <li>Biomedical Big Data</li>
      <li>Computational Biology</li>
      <li>Single-cell RNA-seq</li>
      <li>AI for Healthcare</li>
      <li>Graph Neural Networks</li>
      <li>Data Mining</li>
    </ul>

    <h3>Editorial Service</h3>
    <ul>
      <li>Guest Editor, <em>J. Comput. Biophys. Chem.</em></li>
      <li>Editorial Board, <em>BMC Artificial Intelligence</em></li>
      <li>Youth Editor, <em>Interdisciplinary Medicine</em></li>
      <li>PC Member, BIBM &amp; ICIC</li>
    </ul>

    <h3>Quick Links</h3>
    <ul class="quick-links">
      <li><a href="https://scholar.google.com/" target="_blank" rel="noopener">Google Scholar</a></li>
      <li><a href="https://orcid.org/" target="_blank" rel="noopener">ORCID</a></li>
      <li><a href="https://github.com/" target="_blank" rel="noopener">GitHub</a></li>
      <li><a href="https://www.semanticscholar.org/" target="_blank" rel="noopener">Semantic Scholar</a></li>
      <li><a href="mailto:yuanhuang@nwpu.edu.cn">Email</a></li>
    </ul>

    <h3>Contact</h3>
    <ul>
      <li>📧 <a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a></li>
      <li>🏛️ School of CS, NWPU</li>
      <li>📍 Xi'an, China</li>
    </ul>
  </aside>
</div>
"""


def publications_body(lang):
    if lang == "zh":
        title = "论文发表"
        intro = ("下面是完整的论文列表（共 122 篇），按发表年份倒序排列。"
                 "支持搜索、按类型或会议/期刊筛选，以及排序。<br>"
                 "<strong>加粗</strong>作者为本人的姓名。")
        L = {
            "search": "搜索关键词…",
            "type": "类型",
            "allTypes": "全部类型",
            "allVenues": "全部期刊/会议",
            "sort": "排序",
            "newest": "最新优先",
            "oldest": "最早优先",
            "countLabel": " 篇论文",
            "loading": "正在加载论文列表…",
            "empty": "没有匹配的论文",
            "papers": "论文",
            "firstAuthor": "第一作者",
            "coAuthor": "合著论文",
            "venues": "期刊/会议",
            "noYear": "未标年份",
        }
    else:
        title = "Publications"
        intro = ("Complete list of publications (122 entries), sorted by year descending. "
                 "Use the controls below to search, filter by type or venue, and change sort order. "
                 "<br><strong>Bold</strong> authors indicate Yu-An Huang.")
        L = {
            "search": "Search by keyword…",
            "type": "Type",
            "allTypes": "All types",
            "allVenues": "All venues",
            "sort": "Sort",
            "newest": "Newest first",
            "oldest": "Oldest first",
            "countLabel": " publications",
            "loading": "Loading publications…",
            "empty": "No matching publications.",
            "papers": "Papers",
            "firstAuthor": "First-author",
            "coAuthor": "Co-authored",
            "venues": "Venues",
            "noYear": "Undated",
        }
    return f"""
<h1>{title}</h1>
<p>{intro}</p>
<div id="pub-target"></div>
<script src="../assets/js/bibtex.js"></script>
<script>
  BibTeX.renderPublications({{
    bibPath: '../publications.bib',
    target: document.getElementById('pub-target'),
    labels: {{
      search: '{L["search"]}',
      type: '{L["type"]}',
      allTypes: '{L["allTypes"]}',
      allVenues: '{L["allVenues"]}',
      sort: '{L["sort"]}',
      newest: '{L["newest"]}',
      oldest: '{L["oldest"]}',
      countLabel: function(n) {{ return n + '{L["countLabel"]}'; }},
      loading: '{L["loading"]}',
      empty: '{L["empty"]}',
      stats: {{
        papers: '{L["papers"]}',
        firstAuthor: '{L["firstAuthor"]}',
        coAuthor: '{L["coAuthor"]}',
        venues: '{L["venues"]}'
      }},
      yearHeading: function(y) {{ return y; }},
      noYear: '{L["noYear"]}',
      ownerName: 'huang, yu-an'
    }}
  }});
</script>
"""


def research_body(lang):
    if lang == "zh":
        return """
<h1>研究方向</h1>

<div class="card">
  <h3 id="single-cell">单细胞组学与计算生物学</h3>
  <p>
    单细胞 RNA 测序（scRNA-seq）让我们得以在细胞分辨率下研究组织异质性、肿瘤微环境与发育轨迹。
    我们提出了一系列用于<strong>细胞类型识别</strong>、<strong>细胞间通信推断</strong>、
    <strong>药物响应预测</strong>的图神经网络与 Transformer 方法，发表在 Genome Biology、
    Communications Biology、PLoS Computational Biology 等期刊。
  </p>
  <p>
    <span class="tag">scRNA-seq</span>
    <span class="tag">图神经网络</span>
    <span class="tag">注意力机制</span>
    <span class="tag">细胞类型注释</span>
    <span class="tag">肿瘤微环境</span>
  </p>
</div>

<div class="card">
  <h3 id="neuroimaging">脑影像与神经退行性疾病</h3>
  <p>
    我们结合 fMRI 与单细胞数据，探索阿尔茨海默病等神经退行性疾病的早期诊断标志物。
    代表工作 <em>scBIT</em> 把单细胞转录组信息融入 fMRI 预测框架，发表于 IEEE TMI 2026。
  </p>
  <p>
    <span class="tag">fMRI</span>
    <span class="tag">阿尔茨海默病</span>
    <span class="tag">多模态融合</span>
  </p>
</div>

<div class="card">
  <h3 id="biomedical-kg">生物医学知识图谱与链路预测</h3>
  <p>
    lncRNA–miRNA、circRNA–disease、miRNA–drug、TF–target gene 等生物实体之间的相互作用预测，
    是药物重定位与精准医疗的关键。我们提出基于异质图嵌入、图卷积与自编码器的方法体系。
  </p>
  <p>
    <span class="tag">链路预测</span>
    <span class="tag">异质图</span>
    <span class="tag">图卷积</span>
    <span class="tag">药物重定位</span>
  </p>
</div>

<div class="card">
  <h3 id="medical-imaging">医学图像与可解释 AI</h3>
  <p>
    在医学影像检索与诊断中，研究去偏表征、反事实推理与因果干预，提升模型鲁棒性。
    代表工作 <em>Anti-Confounding Hashing</em> (IEEE TNNLS 2025) 与 <em>CausalMixNet</em> (Medical Image Analysis 2025)。
  </p>
  <p>
    <span class="tag">医学影像</span>
    <span class="tag">哈希检索</span>
    <span class="tag">因果推断</span>
  </p>
</div>

<h2 id="funding">主持项目</h2>
<ul>
  <li><strong>国家杰出青年科学基金 B 类（国家优青）</strong></li>
  <li>国家自然科学基金面上项目</li>
  <li>国家自然科学基金青年科学基金 C 类</li>
  <li>省级自然科学基金 2 项</li>
</ul>
"""
    return """
<h1>Research</h1>

<div class="card">
  <h3 id="single-cell">Single-cell Omics &amp; Computational Biology</h3>
  <p>
    Single-cell RNA sequencing (scRNA-seq) reveals tissue heterogeneity, tumor microenvironment
    and developmental trajectories at cellular resolution. We develop a series of graph neural
    networks and Transformer-based methods for <strong>cell-type identification</strong>,
    <strong>cell-cell communication inference</strong>, and <strong>drug-response prediction</strong>,
    published in <em>Genome Biology</em>, <em>Communications Biology</em>, <em>PLoS Computational Biology</em>, etc.
  </p>
  <p>
    <span class="tag">scRNA-seq</span>
    <span class="tag">Graph Neural Networks</span>
    <span class="tag">Attention</span>
    <span class="tag">Cell-type Annotation</span>
    <span class="tag">Tumor Microenvironment</span>
  </p>
</div>

<div class="card">
  <h3 id="neuroimaging">Neuroimaging &amp; Neurodegenerative Diseases</h3>
  <p>
    We integrate fMRI with single-cell data to identify early diagnostic biomarkers for
    Alzheimer's disease and other neurodegenerative disorders. Our representative work
    <em>scBIT</em> fuses single-cell transcriptomics into fMRI-based prediction
    (<em>IEEE TMI</em> 2026).
  </p>
  <p>
    <span class="tag">fMRI</span>
    <span class="tag">Alzheimer's</span>
    <span class="tag">Multimodal Fusion</span>
  </p>
</div>

<div class="card">
  <h3 id="biomedical-kg">Biomedical Knowledge Graphs &amp; Link Prediction</h3>
  <p>
    Predicting interactions among lncRNAs, miRNAs, circRNAs, diseases, drugs and TFs is key
    to drug repurposing and precision medicine. We propose heterogeneous-graph-embedding,
    graph-convolution and autoencoder-based methods.
  </p>
  <p>
    <span class="tag">Link Prediction</span>
    <span class="tag">Heterogeneous Graphs</span>
    <span class="tag">GCN</span>
    <span class="tag">Drug Repurposing</span>
  </p>
</div>

<div class="card">
  <h3 id="medical-imaging">Medical Imaging &amp; Explainable AI</h3>
  <p>
    We investigate debiased representation, counterfactual reasoning, and causal intervention
    to build robust and interpretable medical image analysis models. Representative works include
    <em>Anti-Confounding Hashing</em> (<em>IEEE TNNLS</em> 2025) and <em>CausalMixNet</em>
    (<em>Medical Image Analysis</em> 2025).
  </p>
  <p>
    <span class="tag">Medical Imaging</span>
    <span class="tag">Hashing Retrieval</span>
    <span class="tag">Causal Inference</span>
  </p>
</div>

<h2 id="funding">Active Funding</h2>
<ul>
  <li><strong>National Outstanding Youth Science Foundation (B)</strong></li>
  <li>General Program of NSFC</li>
  <li>Youth Science Fund (C) of NSFC</li>
  <li>Two Provincial Natural Science Foundations</li>
</ul>
"""


def cv_body(lang):
    if lang == "zh":
        return """
<h1>个人简历</h1>

<h2 id="bio">基本信息</h2>
<ul>
  <li><strong>姓名</strong>：黄裕安 / Yu-An Huang</li>
  <li><strong>职称</strong>：长聘教授、博士生导师</li>
  <li><strong>单位</strong>：西北工业大学 · 计算机学院</li>
  <li><strong>邮箱</strong>：<a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a></li>
  <li><strong>学位</strong>：哲学博士（香港理工大学，2020）</li>
</ul>

<h2 id="positions">工作经历</h2>
<ul class="timeline">
  <li><span class="when">至今</span><strong>西北工业大学</strong> · 计算机学院 · 长聘教授 / 博士生导师</li>
  <li><span class="when">—</span><strong>西北工业大学</strong> · 计算机学院 · 副教授（破格晋升）</li>
</ul>

<h2 id="education">教育背景</h2>
<ul class="timeline">
  <li><span class="when">2016–2020</span><strong>香港理工大学</strong> · 电子计算学系 · 博士</li>
  <li><span class="when">—</span><strong>中国大陆</strong> · 本科 / 硕士（具体院校见个人档案）</li>
</ul>

<h2 id="awards">荣誉与项目</h2>
<div class="cv-section">
  <div class="cv-row"><span class="when">—</span><div class="body"><strong>国家杰出青年科学基金 B 类（国家优青）</strong><em>主持</em></div></div>
  <div class="cv-row"><span class="when">—</span><div class="body"><strong>国家自然科学基金面上项目</strong><em>主持</em></div></div>
  <div class="cv-row"><span class="when">—</span><div class="body"><strong>国家自然科学基金青年科学基金 C 类</strong><em>主持</em></div></div>
  <div class="cv-row"><span class="when">—</span><div class="body"><strong>省级自然科学基金 2 项</strong><em>主持</em></div></div>
</div>

<h2 id="editorial">学术兼职</h2>
<ul>
  <li><em>Journal of Computational Biophysics and Chemistry</em> — 客座编辑</li>
  <li><em>BMC Artificial Intelligence</em> — 编委</li>
  <li><em>Interdisciplinary Medicine</em> — 青年编委</li>
  <li>BIBM、ICIC — 程序委员会委员</li>
</ul>

<h2 id="metrics">学术指标（截至 2025）</h2>
<ul>
  <li>论文总数：70+（仅含完整作者列表的期刊/会议论文）</li>
  <li>Google Scholar 引用：4,000+</li>
  <li>H-index：37</li>
</ul>

<p><a class="tag" href="../assets/cv.pdf">📄 下载完整 PDF 简历（占位）</a></p>
"""
    return """
<h1>Curriculum Vitae</h1>

<h2 id="bio">Bio</h2>
<ul>
  <li><strong>Name</strong>: Yu-An Huang / 黄裕安</li>
  <li><strong>Title</strong>: Tenured Professor &amp; Ph.D. Advisor</li>
  <li><strong>Affiliation</strong>: School of Computer Science, Northwestern Polytechnical University</li>
  <li><strong>Email</strong>: <a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a></li>
  <li><strong>Ph.D.</strong>: Hong Kong Polytechnic University, Electronic Computing, 2020</li>
</ul>

<h2 id="positions">Positions</h2>
<ul class="timeline">
  <li><span class="when">Now</span><strong>Northwestern Polytechnical University</strong> · School of Computer Science · Tenured Professor &amp; Ph.D. Advisor</li>
  <li><span class="when">—</span><strong>Northwestern Polytechnical University</strong> · Associate Professor (early promotion)</li>
</ul>

<h2 id="education">Education</h2>
<ul class="timeline">
  <li><span class="when">2016–2020</span><strong>The Hong Kong Polytechnic University</strong> · Department of Computing · Ph.D.</li>
  <li><span class="when">—</span><strong>China</strong> · B.Sc. / M.Sc. (see personal records)</li>
</ul>

<h2 id="awards">Selected Grants &amp; Awards</h2>
<div class="cv-section">
  <div class="cv-row"><span class="when">—</span><div class="body"><strong>National Outstanding Youth Science Foundation (B)</strong><em>PI</em></div></div>
  <div class="cv-row"><span class="when">—</span><div class="body"><strong>General Program of NSFC</strong><em>PI</em></div></div>
  <div class="cv-row"><span class="when">—</span><div class="body"><strong>Youth Science Fund (C) of NSFC</strong><em>PI</em></div></div>
  <div class="cv-row"><span class="when">—</span><div class="body"><strong>Two Provincial Natural Science Foundations</strong><em>PI</em></div></div>
</div>

<h2 id="editorial">Editorial Service</h2>
<ul>
  <li>Guest Editor, <em>Journal of Computational Biophysics and Chemistry</em></li>
  <li>Editorial Board, <em>BMC Artificial Intelligence</em></li>
  <li>Youth Editor, <em>Interdisciplinary Medicine</em></li>
  <li>Program Committee, BIBM &amp; ICIC</li>
</ul>

<h2 id="metrics">Bibliometrics (as of 2025)</h2>
<ul>
  <li>Total papers: 70+ (full publication list: <a href="./publications.html">122 entries</a>)</li>
  <li>Google Scholar citations: 4,000+</li>
  <li>H-index: 37</li>
</ul>

<p><a class="tag" href="../assets/cv.pdf">📄 Download full CV (PDF)</a></p>
"""


def teaching_body(lang):
    if lang == "zh":
        return """
<h1>教学工作</h1>

<p>目前在西北工业大学计算机学院承担本科与研究生课程，主要面向计算机科学与人工智能方向。</p>

<h2 id="current">本学期课程</h2>
<div class="cv-section">
  <div class="cv-row"><span class="when">本科</span><div class="body"><strong>算法设计与分析实验（英语教学）</strong><em>Algorithm Design &amp; Analysis Lab (taught in English)</em></div></div>
  <div class="cv-row"><span class="when">本科</span><div class="body"><strong>程序设计基础 II 实验</strong><em>Programming Foundations II Lab</em></div></div>
  <div class="cv-row"><span class="when">本科</span><div class="body"><strong>程序设计基础（C++）实验</strong><em>Programming Foundations (C++) Lab</em></div></div>
  <div class="cv-row"><span class="when">本科</span><div class="body"><strong>人工智能应用技术</strong><em>Applied AI Technologies</em></div></div>
</div>

<h2 id="advising">指导学生</h2>
<ul>
  <li><strong>博士研究生</strong>：每年招收 1–2 名</li>
  <li><strong>硕士研究生（推免）</strong>：每年招收若干名</li>
  <li><strong>本科毕业设计</strong>：欢迎本科生加入课题组</li>
</ul>
<p>对学生的期待：扎实编程基础、对科研有热情、能读英文论文。</p>
"""
    return """
<h1>Teaching</h1>

<p>Courses taught at the School of Computer Science, NWPU. Most are at the undergraduate level, with a focus on algorithms, programming, and AI.</p>

<h2 id="current">Current Courses</h2>
<div class="cv-section">
  <div class="cv-row"><span class="when">UG</span><div class="body"><strong>Algorithm Design &amp; Analysis Lab (English)</strong></div></div>
  <div class="cv-row"><span class="when">UG</span><div class="body"><strong>Programming Foundations II Lab</strong></div></div>
  <div class="cv-row"><span class="when">UG</span><div class="body"><strong>Programming Foundations (C++) Lab</strong></div></div>
  <div class="cv-row"><span class="when">UG</span><div class="body"><strong>Applied AI Technologies</strong></div></div>
</div>

<h2 id="advising">Advising</h2>
<ul>
  <li><strong>Ph.D. students</strong>: 1–2 per year</li>
  <li><strong>M.Sc. students (推免)</strong>: several per year</li>
  <li><strong>Undergraduate thesis</strong>: openings available — feel free to reach out</li>
</ul>
<p>What I look for: solid programming fundamentals, curiosity for research, ability to read English papers.</p>
"""


def news_body(lang):
    if lang == "zh":
        return """
<h1>最新动态</h1>

<ul class="news-list">
  <li><span class="date">2026 · 09</span><span class="body">上线个人学术主页，欢迎访问！</span></li>
  <li><span class="date">2026 · 09</span><span class="body">论文 <em>scBIT: Integrating Single-cell Transcriptomic Data into fMRI-based Prediction for Alzheimer's Disease Diagnosis</em> 被 <strong>IEEE Transactions on Medical Imaging</strong> 接收。</span></li>
  <li><span class="date">2025 · 12</span><span class="body">论文 <em>DAGFormer: A graph-based domain adaptation approach for single-cell cancer drug response prediction</em> 被 <strong>PLoS Computational Biology</strong> 接收。</span></li>
  <li><span class="date">2025 · 12</span><span class="body">论文 <em>scTECTA: Asymmetric Deep Transfer Learning for Cross-Patient Tumor Microenvironment Single-Cell Annotation</em> 被 <strong>IEEE TCBB</strong> 接收。</span></li>
  <li><span class="date">2025 · 11</span><span class="body">论文 <em>scKAN: Interpretable Single-cell Analysis for Cell-type-specific Gene Discovery and Drug Repurposing via Kolmogorov–Arnold Networks</em> 被 <strong>Genome Biology</strong> 接收。</span></li>
  <li><span class="date">2025 · 10</span><span class="body">论文 <em>scGSDR: Harnessing Gene Semantics for Single-Cell Pharmacological Profiling</em> 被 <strong>Communications Biology</strong> 接收。</span></li>
  <li><span class="date">2025 · 09</span><span class="body">开始招收 2027 级硕士（推免）与博士研究生。</span></li>
</ul>
"""
    return """
<h1>News</h1>

<ul class="news-list">
  <li><span class="date">2026 · 09</span><span class="body">Personal academic website launched — welcome!</span></li>
  <li><span class="date">2026 · 09</span><span class="body">Paper <em>scBIT: Integrating Single-cell Transcriptomic Data into fMRI-based Prediction for Alzheimer's Disease Diagnosis</em> accepted to <strong>IEEE Transactions on Medical Imaging</strong>.</span></li>
  <li><span class="date">2025 · 12</span><span class="body">Paper <em>DAGFormer: A graph-based domain adaptation approach for single-cell cancer drug response prediction</em> accepted to <strong>PLoS Computational Biology</strong>.</span></li>
  <li><span class="date">2025 · 12</span><span class="body">Paper <em>scTECTA</em> accepted to <strong>IEEE TCBB</strong>.</span></li>
  <li><span class="date">2025 · 11</span><span class="body">Paper <em>scKAN</em> accepted to <strong>Genome Biology</strong>.</span></li>
  <li><span class="date">2025 · 10</span><span class="body">Paper <em>scGSDR</em> accepted to <strong>Communications Biology</strong>.</span></li>
  <li><span class="date">2025 · 09</span><span class="body">Recruiting Master's (推免) and Ph.D. students for Fall 2027.</span></li>
</ul>
"""


def contact_body(lang):
    if lang == "zh":
        return """
<h1>联系方式</h1>

<div class="card">
  <h3>📧 电子邮件</h3>
  <p>学术合作 / 招生咨询 / 报告邀请：<a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a></p>
  <p>我通常在 1–2 个工作日内回复邮件。</p>
</div>

<div class="card">
  <h3>🏛️ 办公地址</h3>
  <p>陕西省西安市长安区<br>
  西北工业大学 · 计算机学院<br>
  友谊校区 / 长安校区</p>
</div>

<div class="card">
  <h3>🌐 在线档案</h3>
  <ul class="quick-links">
    <li><a href="https://scholar.google.com/" target="_blank" rel="noopener">Google Scholar</a></li>
    <li><a href="https://orcid.org/" target="_blank" rel="noopener">ORCID</a></li>
    <li><a href="https://www.semanticscholar.org/" target="_blank" rel="noopener">Semantic Scholar</a></li>
    <li><a href="https://github.com/" target="_blank" rel="noopener">GitHub</a></li>
    <li><a href="https://teacher.nwpu.edu.cn/yuanhuang.html" target="_blank" rel="noopener">西工大主页</a></li>
  </ul>
</div>

<div class="card">
  <h3>🤝 合作机会</h3>
  <p>欢迎<strong>博士后、博士生、硕士推免生</strong>联系；同时欢迎与学术界、工业界开展科研合作。</p>
  <p>课题组研究关键词：单细胞分析、生物医学大数据、计算生物学、AI for Healthcare、图神经网络。</p>
</div>
"""
    return """
<h1>Contact</h1>

<div class="card">
  <h3>📧 Email</h3>
  <p>For academic collaboration, admissions, or talk invitations:
     <a href="mailto:yuanhuang@nwpu.edu.cn">yuanhuang@nwpu.edu.cn</a></p>
  <p>I typically reply within 1–2 business days.</p>
</div>

<div class="card">
  <h3>🏛️ Office</h3>
  <p>School of Computer Science<br>
  Northwestern Polytechnical University<br>
  Xi'an, Shaanxi, China</p>
</div>

<div class="card">
  <h3>🌐 Online Profiles</h3>
  <ul class="quick-links">
    <li><a href="https://scholar.google.com/" target="_blank" rel="noopener">Google Scholar</a></li>
    <li><a href="https://orcid.org/" target="_blank" rel="noopener">ORCID</a></li>
    <li><a href="https://www.semanticscholar.org/" target="_blank" rel="noopener">Semantic Scholar</a></li>
    <li><a href="https://github.com/" target="_blank" rel="noopener">GitHub</a></li>
    <li><a href="https://teacher.nwpu.edu.cn/yuanhuang.html" target="_blank" rel="noopener">NWPU Profile</a></li>
  </ul>
</div>

<div class="card">
  <h3>🤝 Collaboration</h3>
  <p>I am open to <strong>postdoc, Ph.D., and Master's (推免)</strong> applicants, and to academic &amp; industrial collaborations.</p>
  <p>Research keywords: single-cell analysis, biomedical big data, computational biology, AI for healthcare, graph neural networks.</p>
</div>
"""


# ----------------------------------------------------------------------
# Page generator
# ----------------------------------------------------------------------
def write(lang, page_key, title, body, description=""):
    """Write a single page to /<lang>/<file>."""
    nav = NAV_ZH if lang == "zh" else NAV_EN
    out_file = next(href for href, _, key in nav if key == page_key)
    out_path = ROOT / lang / out_file
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page_template(lang, page_key, title, body, description), encoding="utf-8")
    print(f"  wrote {out_path.relative_to(ROOT)}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    # Chinese pages
    write("zh", "home", "主页", home_body("zh"),
          description="黄裕安，西北工业大学计算机学院长聘教授、博士生导师。")
    write("zh", "publications", "论文", publications_body("zh"),
          description="黄裕安的全部论文列表（122 篇），按年份排序。")
    write("zh", "research", "研究方向", research_body("zh"),
          description="单细胞组学、计算生物学、AI for Healthcare、脑影像、医学图像分析等。")
    write("zh", "cv", "个人简历", cv_body("zh"),
          description="黄裕安的学术简历、教育背景、项目与荣誉。")
    write("zh", "teaching", "教学", teaching_body("zh"),
          description="西北工业大学计算机学院本科与研究生课程。")
    write("zh", "news", "最新动态", news_body("zh"),
          description="论文接收、研究进展、招生通知等。")
    write("zh", "contact", "联系方式", contact_body("zh"),
          description="邮箱、办公地址、在线档案、合作机会。")

    # English pages
    write("en", "home", "Home", home_body("en"),
          description="Yu-An Huang, Tenured Professor at Northwestern Polytechnical University.")
    write("en", "publications", "Publications", publications_body("en"),
          description="Complete publication list (122 entries) of Yu-An Huang, sorted by year.")
    write("en", "research", "Research", research_body("en"),
          description="Single-cell omics, computational biology, AI for healthcare, neuroimaging, medical imaging.")
    write("en", "cv", "CV", cv_body("en"),
          description="Academic CV, education, grants, awards, editorial service.")
    write("en", "teaching", "Teaching", teaching_body("en"),
          description="Undergraduate and graduate courses at NWPU.")
    write("en", "news", "News", news_body("en"),
          description="Paper acceptances, research progress, recruiting announcements.")
    write("en", "contact", "Contact", contact_body("en"),
          description="Email, office address, online profiles, collaboration.")

    # Root index — language picker
    (ROOT / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Yu-An Huang · 黄裕安</title>
  <link rel="stylesheet" href="assets/css/style.css">
  <link rel="icon" type="image/svg+xml" href="assets/img/favicon.svg">
  <style>
    .lang-picker {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      max-width: 760px;
      margin: 4rem auto;
      padding: 0 24px;
    }}
    .lang-card {{
      background: var(--c-bg-card);
      border: 1px solid var(--c-border);
      border-radius: var(--radius-lg);
      padding: 2.5rem 2rem;
      text-align: center;
      transition: transform .15s, box-shadow .15s, border-color .15s;
    }}
    .lang-card:hover {{
      transform: translateY(-4px);
      box-shadow: var(--shadow-md);
      border-color: var(--c-accent);
    }}
    .lang-card .label {{
      font-size: 2rem;
      font-weight: 700;
      color: var(--c-text);
      margin-bottom: .3em;
    }}
    .lang-card .sub {{
      color: var(--c-text-muted);
      font-size: 0.95rem;
    }}
    .lang-card .lang {{
      display: inline-block;
      padding: 4px 12px;
      background: var(--c-accent-soft);
      color: var(--c-accent);
      border-radius: 999px;
      font-size: 0.85rem;
      margin-top: 1rem;
      font-weight: 500;
    }}
    .lang-card a {{ border-bottom: none; display: block; color: inherit; }}
  </style>
</head>
<body>
  <header class="site-header">
    <nav class="nav">
      <a class="nav-brand" href="./">Yu-An Huang · 黄裕安</a>
    </nav>
  </header>
  <main>
    <div class="lang-picker">
      <div class="lang-card">
        <a href="./zh/">
          <div class="label">中文</div>
          <div class="sub">个人学术主页</div>
          <span class="lang">进入 →</span>
        </a>
      </div>
      <div class="lang-card">
        <a href="./en/">
          <div class="label">English</div>
          <div class="sub">Personal Academic Site</div>
          <span class="lang">Enter →</span>
        </a>
      </div>
    </div>
    <p style="text-align:center;color:var(--c-text-muted);font-size:.85rem;">
      Or jump directly to <a href="https://yu-anhuang.github.io/">https://yu-anhuang.github.io</a>
    </p>
  </main>
  <footer class="site-footer">
    <p>© 2026 Yu-An Huang · School of Computer Science, NWPU</p>
  </footer>
</body>
</html>
""", encoding="utf-8")
    print(f"  wrote index.html (language picker)")

    print("\nAll pages generated.")


if __name__ == "__main__":
    main()

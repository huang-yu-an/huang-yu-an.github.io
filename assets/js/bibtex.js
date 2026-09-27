/* ==========================================================================
   BibTeX Parser & Renderer (vanilla JS)
   - Parses publications.bib in the browser
   - Hides incomplete / preprint / low-tier entries
   - Shows JOURNAL ABBREVIATION in the left column (instead of bib key)
   - Renders filterable list grouped by year
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------- BibTeX parser ------------------- */

  function tokenize(src) {
    const tokens = [];
    let i = 0;
    const len = src.length;
    while (i < len) {
      const ch = src[i];
      if (/\s/.test(ch)) { i++; continue; }
      if (ch === "%") { while (i < len && src[i] !== "\n") i++; continue; }
      if (ch === "{" || ch === "}" || ch === "," || ch === "=") {
        tokens.push({ type: ch }); i++; continue;
      }
      if (ch === '"') {
        let s = ""; i++;
        while (i < len && src[i] !== '"') {
          if (src[i] === "\\" && i + 1 < len) { s += src[i + 1]; i += 2; continue; }
          s += src[i++];
        }
        i++; tokens.push({ type: "string", value: s }); continue;
      }
      if (ch === "@") {
        let s = "@"; i++;
        while (i < len && /[A-Za-z]/.test(src[i])) { s += src[i++]; }
        tokens.push({ type: "type", value: s }); continue;
      }
      if (/[0-9]/.test(ch)) {
        let s = "";
        while (i < len && /[0-9.\-]/.test(src[i])) { s += src[i++]; }
        tokens.push({ type: "ident", value: s }); continue;
      }
      if (/[A-Za-z_]/.test(ch)) {
        let s = "";
        while (i < len && /[A-Za-z0-9_\-:.]/.test(src[i])) { s += src[i++]; }
        tokens.push({ type: "ident", value: s }); continue;
      }
      if (ch === "#") { tokens.push({ type: "concat" }); i++; continue; }
      i++;
    }
    return tokens;
  }

  function parse(src) {
    const tokens = tokenize(src);
    const entries = [];
    let pos = 0;
    while (pos < tokens.length) {
      while (pos < tokens.length && tokens[pos].type !== "type") pos++;
      if (pos >= tokens.length) break;
      const entryType = tokens[pos].value.toLowerCase(); pos++;
      if (entryType === "@string" || entryType === "@preamble" || entryType === "@comment") {
        let depth = 0;
        while (pos < tokens.length) {
          if (tokens[pos].type === "{") depth++;
          else if (tokens[pos].type === "}") { depth--; if (depth === 0) { pos++; break; } }
          pos++;
        }
        continue;
      }
      if (tokens[pos].type !== "{") continue;
      pos++;
      if (pos >= tokens.length || tokens[pos].type !== "ident") break;
      const key = tokens[pos].value; pos++;
      const fields = {};
      let entryDepth = 1, curField = null, curValue = null;
      while (pos < tokens.length && entryDepth > 0) {
        const tok = tokens[pos];
        if (tok.type === "}") {
          if (curField) { fields[curField.toLowerCase()] = curValue || ""; curField = null; curValue = null; }
          entryDepth--; pos++; break;
        }
        if (tok.type === ",") {
          if (curField) { fields[curField.toLowerCase()] = curValue || ""; curField = null; curValue = null; }
          pos++; continue;
        }
        if (tok.type === "ident" && !curField) {
          curField = tok.value; pos++;
          if (tokens[pos] && tokens[pos].type === "=") pos++;
          continue;
        }
        if (tok.type === "{") {
          let depth = 1, s = "", prevKind = "";
          pos++;
          while (pos < tokens.length && depth > 0) {
            const t = tokens[pos];
            if (t.type === "{") { depth++; s += "{"; prevKind = "punct"; }
            else if (t.type === "}") { depth--; if (depth > 0) s += "}"; prevKind = "punct"; }
            else if (t.type === "string") { if (prevKind === "ident") s += " "; s += t.value; prevKind = "string"; }
            else if (t.type === "ident") { if (prevKind === "ident") s += " "; s += t.value; prevKind = "ident"; }
            else if (t.type === ",") { s += ", "; prevKind = "punct"; }
            else if (t.type === "concat") { s += " "; prevKind = "punct"; }
            else if (t.type === "=") { s += "="; prevKind = "punct"; }
            pos++;
          }
          if (curValue == null) curValue = s; else curValue += s;
          continue;
        }
        if (tok.type === "string") {
          if (curValue == null) curValue = tok.value; else curValue += tok.value;
          pos++; continue;
        }
        pos++;
      }
      if (entryDepth === 0 && Object.keys(fields).length > 0) {
        entries.push({ type: entryType.replace("@", ""), key, fields });
      }
    }
    return entries;
  }

  /* ------------------- Venue blocklist (defensive) ------------------- */
  // Even though .bib is filtered, this hides them again if they sneak back in.
  const HIDDEN_VENUES = [
    "arxiv", "biorxiv", "medrxiv", "preprint",
    "oncotarget",
    // MDPI
    "molecules", "international journal of molecular sciences", "biomed research international",
    // Frontiers
    "frontiers in genetics", "frontiers in microbiology", "frontiers in bioscience",
    // Mega / low-tier
    "scientific reports", "plos one", "scientific programming",
    "computational biomedicine", "current protein and peptide science"
  ];

  function shouldHide(fields) {
    const journal = (fields.journal || "").toLowerCase();
    const booktitle = (fields.booktitle || "").toLowerCase();
    const howpublished = (fields.howpublished || "").toLowerCase();
    const venue = journal + " " + booktitle + " " + howpublished;
    if (!venue.trim()) return true;
    if (!fields.year || !fields.year.trim()) return true;
    for (const bad of HIDDEN_VENUES) if (venue.includes(bad)) return true;
    return false;
  }

  /* ------------------- Journal abbreviation map ------------------- */
  // Maps the full venue name (lowercased, normalized) → short tag shown
  // in the left column. Order matters: longer / more specific matches first.
  const ABBR_MAP = [
    // Q1 journals
    [ "genome biology",                              "Genome Biol." ],
    [ "nature communications",                       "Nat. Commun." ],
    [ "nature methods",                              "Nat. Methods" ],
    [ "nature machine intelligence",                 "Nat. Mach. Intell." ],
    [ "advanced science",                            "Adv. Sci." ],
    [ "briefings in bioinformatics",                 "Brief. Bioinform." ],
    [ "briefings in functional genomics",            "Brief. Funct. Genomics" ],
    [ "bioinformatics",                              "Bioinformatics" ],
    [ "ieee transactions on medical imaging",        "IEEE TMI" ],
    [ "ieee transactions on pattern analysis and machine intelligence", "IEEE TPAMI" ],
    [ "ieee transactions on neural networks and learning systems",       "IEEE TNNLS" ],
    [ "ieee transactions on cybernetics",            "IEEE TCYB" ],
    [ "ieee transactions on information forensics and security", "IEEE TIFS" ],
    [ "ieee transactions on fuzzy systems",          "IEEE TFS" ],
    [ "ieee transactions on big data",               "IEEE TBD" ],
    [ "ieee transactions on biomedical engineering","IEEE TBME" ],
    [ "ieee transactions on geoscience and remote sensing", "IEEE TGRS" ],
    [ "ieee/acm transactions on computational biology and bioinformatics", "IEEE/ACM TCBB" ],
    [ "ieee transactions on computational biology and bioinformatics", "IEEE TCBB" ],
    [ "ieee journal of biomedical and health informatics", "IEEE JBHI" ],
    [ "plos computational biology",                 "PLoS Comput. Biol." ],
    [ "communications biology",                      "Commun. Biol." ],
    [ "bmc biology",                                 "BMC Biol." ],
    [ "cell reports methods",                        "Cell Rep. Methods" ],
    [ "medical image analysis",                      "Med. Image Anal." ],
    [ "knowledge-based systems",                     "Knowl.-Based Syst." ],
    [ "digital discovery",                           "Digit. Discov." ],
    [ "international journal of intelligent systems","Int. J. Intell. Syst." ],
    [ "applied soft computing",                      "Appl. Soft Comput." ],
    [ "complex & intelligent systems",               "Complex Intell. Syst." ],
    [ "complex and intelligent systems",             "Complex Intell. Syst." ],
    [ "neurocomputing",                              "Neurocomputing" ],
    [ "journal of chemical information and modeling","J. Chem. Inf. Model." ],
    [ "journal of cellular and molecular medicine",   "J. Cell. Mol. Med." ],
    [ "journal of translational medicine",           "J. Transl. Med." ],
    [ "journal of computational biophysics and chemistry", "J. Comput. Biophys. Chem." ],
    [ "international journal of biological macromolecules", "Int. J. Biol. Macromol." ],
    [ "bmc bioinformatics",                          "BMC Bioinform." ],
    [ "bmc systems biology",                         "BMC Syst. Biol." ],
    [ "bmc genomics",                                "BMC Genomics" ],
    [ "journal of diabetes",                         "J. Diabetes" ],
    [ "diabetes",                                    "Diabetes" ],
    [ "cell",                                        "Cell" ],
    [ "nature",                                      "Nature" ],
    [ "science",                                     "Science" ],
    // Conferences
    [ "aaai conference on artificial intelligence",  "AAAI" ],
    [ "proceedings of the aaai conference on artificial intelligence", "AAAI" ],
    [ "knowledge discovery and data mining",         "KDD" ],
    [ "proceedings of the acm sigkdd conference on knowledge discovery and data mining", "KDD" ],
    [ "advances in neural information processing systems", "NeurIPS" ],
    [ "international conference on machine learning", "ICML" ],
    [ "international conference on learning representations", "ICLR" ],
    [ "international joint conference on artificial intelligence", "IJCAI" ],
    [ "international conference on robotics and automation", "ICRA" ],
    [ "international conference on computer vision and pattern recognition", "CVPR" ],
    [ "ieee/cvf conference on computer vision and pattern recognition", "CVPR" ],
    [ "ieee international conference on acoustics, speech and signal processing", "ICASSP" ],
    [ "international conference on intelligent computing", "ICIC" ],
    [ "international conference on bioinformatics and biomedicine", "BIBM" ],
    [ "ieee international conference on bioinformatics and biomedicine", "BIBM" ],
    [ "ieee international conference on healthcare informatics", "ICHI" ],
    [ "international conference on bioinformatics and intelligent computing", "ICBIC" ]
  ];

  // Generic fallback: first significant word(s), abbreviated
  function makeAbbrev(fullName) {
    if (!fullName) return "?";
    const cleaned = fullName.replace(/[{}]/g, "").trim();
    // If we have a manual mapping, use it
    const low = cleaned.toLowerCase();
    for (const [key, val] of ABBR_MAP) {
      if (low.includes(key)) return val;
    }
    // Fallback: smart truncation
    // Drop leading "Proceedings of the", "IEEE", year suffixes, etc.
    let s = cleaned
      .replace(/^proceedings\s+of\s+(the\s+)?/i, "")
      .replace(/^ieee\s+/i, "")
      .replace(/^acm\s+/i, "")
      .replace(/\s+\d{4}.*$/, "")   // drop year + tail
      .replace(/\s+\(.*?\)/g, "")    // drop parenthetical
      .trim();
    // Limit length
    if (s.length > 22) s = s.slice(0, 22).trim() + ".";
    return s;
  }

  /* ------------------- Render helpers ------------------- */

  function escapeHTML(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalizeAuthors(authorsRaw) {
    return (authorsRaw || "")
      .split(/\s+and\s+/i)
      .map((a) => a.trim())
      .filter(Boolean);
  }

  function renderAuthors(authors, ownerName) {
    const ownerLower = (ownerName || "huang, yu-an").toLowerCase();
    return authors.map((a) => {
      const isOwner = a.toLowerCase().startsWith(ownerLower);
      return isOwner ? `<strong>${escapeHTML(a)}</strong>` : escapeHTML(a);
    }).join(", ");
  }

  function htmlEntitiesToText(s) {
    return (s || "")
      .replace(/\\&/g, "&").replace(/\\%/g, "%").replace(/\\\$/g, "$")
      .replace(/\\_/g, "_").replace(/\\#/g, "#").replace(/\\"/g, '"')
      .replace(/``/g, '"').replace(/''/g, '"')
      .replace(/--/g, "—").replace(/~/g, " ")
      .replace(/[{}]/g, "");
  }

  function buildSearchText(entry) {
    const f = entry.fields;
    return [
      htmlEntitiesToText(f.title),
      htmlEntitiesToText(f.author),
      htmlEntitiesToText(f.journal),
      htmlEntitiesToText(f.booktitle),
      htmlEntitiesToText(f.publisher),
      f.year
    ].join(" ").toLowerCase();
  }

  function computeStats(entries, ownerName) {
    const ownerLower = (ownerName || "huang, yu-an").toLowerCase();
    let firstAuthor = 0, coAuthor = 0;
    const venues = new Set();
    entries.forEach((e) => {
      const authors = normalizeAuthors(e.fields.author);
      if (authors.length > 0 && authors[0].toLowerCase().startsWith(ownerLower)) firstAuthor++;
      else if (authors.some((a) => a.toLowerCase().startsWith(ownerLower))) coAuthor++;
      const v = htmlEntitiesToText(e.fields.journal || e.fields.booktitle || "");
      if (v) venues.add(v);
    });
    return { total: entries.length, firstAuthor, coAuthor, venues: venues.size };
  }

  /* ------------------- Public render ------------------- */

  async function renderPublications(opts) {
    const { bibPath, target, labels = {} } = opts;
    const L = Object.assign({
      search: "搜索…",
      type: "类型",
      allTypes: "全部类型",
      allVenues: "全部期刊/会议",
      sort: "排序",
      newest: "最新优先",
      oldest: "最早优先",
      countLabel: (n) => `${n} 篇`,
      loading: "正在加载…",
      empty: "没有匹配的论文",
      stats: { papers: "论文", firstAuthor: "第一作者", coAuthor: "合著", venues: "期刊会议" },
      yearHeading: (y) => `${y}`,
      noYear: "未标年份",
      ownerName: "huang, yu-an"
    }, labels);

    target.innerHTML = `<p class="pub-loading">${escapeHTML(L.loading)}</p>`;
    let bibText;
    try {
      const resp = await fetch(bibPath, { cache: "no-store" });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      bibText = await resp.text();
    } catch (err) {
      target.innerHTML = `<p class="pub-empty">⚠️ 加载失败 — ${escapeHTML(err.message)}</p>`;
      return;
    }

    const entries = parse(bibText)
      .filter((e) => e.fields.title && e.fields.author)
      .filter((e) => !shouldHide(e.fields))
      .map((e) => ({
        ...e,
        _year: parseInt((e.fields.year || "0").replace(/\D/g, ""), 10) || 0,
        _authors: normalizeAuthors(htmlEntitiesToText(e.fields.author)),
        _venue: htmlEntitiesToText(e.fields.journal || e.fields.booktitle || e.fields.publisher || ""),
        _venueFull: e.fields.journal || e.fields.booktitle || e.fields.publisher || ""
      }));

    entries.forEach((e) => { e._search = buildSearchText(e); });

    const stats = computeStats(entries, L.ownerName);

    target.innerHTML = "";

    // Stats block
    if (opts.showStats !== false) {
      const statsEl = document.createElement("div");
      statsEl.className = "pub-stats";
      statsEl.innerHTML = `
        <div class="pub-stat"><span class="value">${stats.total}</span><span class="label">${escapeHTML(L.stats.papers)}</span></div>
        <div class="pub-stat"><span class="value">${stats.firstAuthor}</span><span class="label">${escapeHTML(L.stats.firstAuthor)}</span></div>
        <div class="pub-stat"><span class="value">${stats.coAuthor}</span><span class="label">${escapeHTML(L.stats.coAuthor)}</span></div>
        <div class="pub-stat"><span class="value">${stats.venues}</span><span class="label">${escapeHTML(L.stats.venues)}</span></div>
      `;
      target.appendChild(statsEl);
    }

    // Controls
    const controls = document.createElement("div");
    controls.className = "pub-controls";
    controls.innerHTML = `
      <input type="search" placeholder="${escapeHTML(L.search)}" aria-label="${escapeHTML(L.search)}" />
      <select aria-label="${escapeHTML(L.type)}"><option value="__all__">${escapeHTML(L.allTypes)}</option></select>
      <select aria-label="Venue filter"><option value="__all__">${escapeHTML(L.allVenues)}</option></select>
      <select aria-label="${escapeHTML(L.sort)}">
        <option value="newest">${escapeHTML(L.newest)}</option>
        <option value="oldest">${escapeHTML(L.oldest)}</option>
      </select>
      <span class="pub-count"></span>
    `;
    target.appendChild(controls);

    const list = document.createElement("ul");
    list.className = "pub-list";
    target.appendChild(list);

    // Populate type select
    const types = [...new Set(entries.map((e) => e.type))].sort();
    const typeSel = controls.querySelector("select:nth-of-type(1)");
    types.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t;
      opt.textContent = t[0].toUpperCase() + t.slice(1);
      typeSel.appendChild(opt);
    });
    const venues = [...new Set(entries.map((e) => e._venue).filter(Boolean))].sort();
    const venueSel = controls.querySelector("select:nth-of-type(2)");
    venues.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      venueSel.appendChild(opt);
    });

    const search = controls.querySelector("input[type='search']");
    const sortSel = controls.querySelector("select:nth-of-type(3)");
    const countEl = controls.querySelector(".pub-count");

    function render() {
      const q = (search.value || "").trim().toLowerCase();
      const tFilter = typeSel.value;
      const vFilter = venueSel.value;
      const sortOrder = sortSel.value;

      let filtered = entries.filter((e) => {
        if (tFilter !== "__all__" && e.type !== tFilter) return false;
        if (vFilter !== "__all__" && e._venue !== vFilter) return false;
        if (q && !e._search.includes(q)) return false;
        return true;
      });

      filtered.sort((a, b) => {
        if (a._year !== b._year) return sortOrder === "oldest" ? a._year - b._year : b._year - a._year;
        const an = (a._authors[0] || "").split(",")[0].toLowerCase();
        const bn = (b._authors[0] || "").split(",")[0].toLowerCase();
        return an.localeCompare(bn);
      });

      countEl.textContent = L.countLabel(filtered.length);

      list.innerHTML = "";
      if (filtered.length === 0) {
        list.innerHTML = `<p class="pub-empty">${escapeHTML(L.empty)}</p>`;
        return;
      }
      const groups = new Map();
      filtered.forEach((e) => {
        const y = e._year || 0;
        if (!groups.has(y)) groups.set(y, []);
        groups.get(y).push(e);
      });

      const yearKeys = [...groups.keys()].sort((a, b) => sortOrder === "oldest" ? a - b : b - a);
      yearKeys.forEach((y) => {
        const heading = document.createElement("div");
        heading.className = "pub-year";
        heading.textContent = y === 0 ? L.noYear : L.yearHeading(y);
        list.appendChild(heading);
        groups.get(y).forEach((e) => list.appendChild(renderEntry(e)));
      });
    }

    function renderEntry(e) {
      const li = document.createElement("li");
      li.className = "pub-item";
      const title = htmlEntitiesToText(e.fields.title);
      const venue = e._venue;
      const abbrev = makeAbbrev(e._venueFull);
      const authors = renderAuthors(e._authors, L.ownerName);

      const pdf = htmlEntitiesToText(e.fields.pdf || "");
      const url = htmlEntitiesToText(e.fields.url || "");
      const doi = htmlEntitiesToText(e.fields.doi || "");
      const code = htmlEntitiesToText(e.fields.code || "");

      const links = [];
      if (pdf)  links.push(`<a href="${escapeHTML(pdf)}" target="_blank" rel="noopener">PDF</a>`);
      if (code) links.push(`<a href="${escapeHTML(code)}" target="_blank" rel="noopener">Code</a>`);
      if (doi) {
        const doiUrl = doi.startsWith("http") ? doi : `https://doi.org/${doi}`;
        links.push(`<a href="${escapeHTML(doiUrl)}" target="_blank" rel="noopener">DOI</a>`);
      } else if (url) {
        links.push(`<a href="${escapeHTML(url)}" target="_blank" rel="noopener">Link</a>`);
      }
      const linksHTML = links.length ? `<div class="links">${links.join(" · ")}</div>` : "";

      const vol = e.fields.volume ? `, ${escapeHTML(htmlEntitiesToText(e.fields.volume))}` : "";
      const numIssue = e.fields.number ? `(${escapeHTML(htmlEntitiesToText(e.fields.number))})` : "";
      const pages = e.fields.pages ? `: ${escapeHTML(htmlEntitiesToText(e.fields.pages))}` : "";

      li.innerHTML = `
        <div class="venue-tag" title="${escapeHTML(venue)}">${escapeHTML(abbrev)}</div>
        <div class="text">
          <div class="title">${escapeHTML(title)}</div>
          <div class="authors">${authors}</div>
          <div class="venue"><span class="venue-name">${escapeHTML(venue)}</span>${vol}${numIssue}${pages}<span class="pub-year-suffix">${e._year || ""}</span></div>
          ${linksHTML}
        </div>
      `;
      return li;
    }

    search.addEventListener("input", render);
    typeSel.addEventListener("change", render);
    venueSel.addEventListener("change", render);
    sortSel.addEventListener("change", render);

    render();
  }

  window.BibTeX = { renderPublications };
})();

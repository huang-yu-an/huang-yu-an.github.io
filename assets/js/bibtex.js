/* ==========================================================================
   BibTeX Parser & Renderer (vanilla JS, no dependencies)
   Fetches publications.bib, parses entries, groups by year, renders list.
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------- BibTeX parser ------------------- */

  /**
   * Tokenize BibTeX into a list of {type, value} tokens for braces, strings,
   * identifiers, numbers, commas, equals, and quoted strings.
   */
  function tokenize(src) {
    const tokens = [];
    let i = 0;
    const len = src.length;
    while (i < len) {
      const ch = src[i];
      if (/\s/.test(ch)) { i++; continue; }
      if (ch === "%") {
        // LaTeX comment — skip to end of line
        while (i < len && src[i] !== "\n") i++;
        continue;
      }
      if (ch === "{" || ch === "}" || ch === "," || ch === "=") {
        tokens.push({ type: ch });
        i++;
        continue;
      }
      if (ch === '"') {
        // Quoted string — handle brace escapes (not strictly BibTeX but common)
        let s = "";
        i++;
        while (i < len && src[i] !== '"') {
          if (src[i] === "\\" && i + 1 < len) { s += src[i + 1]; i += 2; continue; }
          s += src[i++];
        }
        i++;
        tokens.push({ type: "string", value: s });
        continue;
      }
      if (ch === "@") {
        let s = "@";
        i++;
        while (i < len && /[A-Za-z]/.test(src[i])) { s += src[i++]; }
        tokens.push({ type: "type", value: s });
        continue;
      }
      if (/[0-9]/.test(ch)) {
        // Number — collect as ident so brace-value collection picks it up.
        let s = "";
        while (i < len && /[0-9.\-]/.test(src[i])) { s += src[i++]; }
        tokens.push({ type: "ident", value: s });
        continue;
      }
      if (/[A-Za-z_]/.test(ch)) {
        let s = "";
        while (i < len && /[A-Za-z0-9_\-:.]/.test(src[i])) { s += src[i++]; }
        tokens.push({ type: "ident", value: s });
        continue;
      }
      if (ch === "#") {
        tokens.push({ type: "concat" });
        i++;
        continue;
      }
      // Unknown character — skip
      i++;
    }
    return tokens;
  }

  /**
   * Parse a BibTeX source string into an array of entry objects:
   * {type, key, fields: {field: value, ...}}
   */
  function parse(src) {
    const tokens = tokenize(src);
    const entries = [];

    let pos = 0;
    while (pos < tokens.length) {
      // Skip until next @
      while (pos < tokens.length && tokens[pos].type !== "type") pos++;
      if (pos >= tokens.length) break;

      const entryType = tokens[pos].value.toLowerCase(); // e.g. @article
      pos++;

      // Skip @string / @preamble / @comment blocks by brace counting
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
      const key = tokens[pos].value;
      pos++;

      const fields = {};
      // Track the entry-level brace depth. We start at 1 (inside the entry braces).
      let entryDepth = 1;
      let curField = null;
      let curValue = null;

      while (pos < tokens.length && entryDepth > 0) {
        const tok = tokens[pos];

        // Closing brace of the entry
        if (tok.type === "}") {
          if (curField) { fields[curField.toLowerCase()] = curValue || ""; curField = null; curValue = null; }
          entryDepth--;
          pos++;
          break;
        }

        // Comma between fields (or between authors in author field handled via {})
        if (tok.type === ",") {
          // If we're in the middle of a brace value, this comma is part of it.
          // The brace handler runs before this point when value uses {…},
          // so a top-level comma here is a field separator.
          if (curField) { fields[curField.toLowerCase()] = curValue || ""; curField = null; curValue = null; }
          pos++;
          continue;
        }

        // Field name (only when we don't have a current field)
        if (tok.type === "ident" && !curField) {
          curField = tok.value;
          pos++;
          if (tokens[pos] && tokens[pos].type === "=") pos++;
          continue;
        }

        // Field value as a {…} block — collect nested tokens into a string.
        // Insert spaces between adjacent identifiers so that "Chen, Xing and Huang"
        // renders with spaces even though BibTeX doesn't separate tokens with WS.
        if (tok.type === "{") {
          let depth = 1;
          let s = "";
          let prevKind = ""; // "", "ident", "string", "punct"
          pos++;
          while (pos < tokens.length && depth > 0) {
            const t = tokens[pos];
            if (t.type === "{") { depth++; s += "{"; prevKind = "punct"; }
            else if (t.type === "}") { depth--; if (depth > 0) s += "}"; prevKind = "punct"; }
            else if (t.type === "string") {
              if (prevKind === "ident") s += " ";
              s += t.value;
              prevKind = "string";
            }
            else if (t.type === "ident") {
              if (prevKind === "ident") s += " ";
              s += t.value;
              prevKind = "ident";
            }
            else if (t.type === ",") { s += ", "; prevKind = "punct"; }
            else if (t.type === "concat") { s += " "; prevKind = "punct"; }
            else if (t.type === "=") { s += "="; prevKind = "punct"; }
            pos++;
          }
          if (curValue == null) curValue = s; else curValue += s;
          continue;
        }

        // Quoted string value
        if (tok.type === "string") {
          if (curValue == null) curValue = tok.value;
          else curValue += tok.value;
          pos++;
          continue;
        }

        pos++;
      }

      // Tolerate malformed entries by only pushing complete ones
      if (entryDepth === 0 && Object.keys(fields).length > 0) {
        entries.push({ type: entryType.replace("@", ""), key, fields });
      }
    }

    return entries;
  }

  /* ------------------- Render helpers ------------------- */

  // Known venue tier — top journals/conferences tagged for visibility
  const VENUE_TIER = {
    // Q1 / top journals
    "genome biology": "Q1",
    "nature communications": "Q1",
    "advanced science": "Q1",
    "briefings in bioinformatics": "Q1",
    "bioinformatics": "Q1",
    "ieee transactions on medical imaging": "Q1",
    "ieee transactions on pattern analysis and machine intelligence": "Q1",
    "ieee transactions on neural networks and learning systems": "Q1",
    "ieee transactions on cybernetics": "Q1",
    "ieee transactions on information forensics and security": "Q1",
    "medical image analysis": "Q1",
    "knowledge-based systems": "Q1",
    "plos computational biology": "Q1",
    "communications biology": "Q1",
    "bmc biology": "Q1",
    "cell reports methods": "Q1",
    // A* conferences
    "aaai": "A*",
    "kdd": "A*",
    "nips": "A*",
    "neurips": "A*",
    "icml": "A*",
    "iclr": "A*",
    "ijcai": "A*",
    "icra": "A*",
    "bibm": "CORE",
    "icic": "C"
  };

  function venueTag(venue) {
    if (!venue) return "";
    const v = venue.toLowerCase().replace(/[{}]/g, "");
    for (const key of Object.keys(VENUE_TIER)) {
      if (v.includes(key)) {
        const tier = VENUE_TIER[key];
        if (tier === "Q1") return '<span class="pub-tag q1">Q1</span>';
        if (tier === "A*") return '<span class="pub-tag q1">A*</span>';
        if (tier === "CORE") return '<span class="pub-tag q2">BIBM</span>';
        return `<span class="pub-tag q2">${tier}</span>`;
      }
    }
    return "";
  }

  function escapeHTML(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalizeAuthors(authorsRaw) {
    // BibTeX " and " separator; entries can have Last, First
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
      .replace(/\\&/g, "&")
      .replace(/\\%/g, "%")
      .replace(/\\\$/g, "$")
      .replace(/\\_/g, "_")
      .replace(/\\#/g, "#")
      .replace(/\\"/g, '"')
      .replace(/``/g, '"')
      .replace(/''/g, '"')
      .replace(/--/g, "—")
      .replace(/~/g, " ")
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

  /* ------------------- Public render function ------------------- */

  /**
   * Render a publications list into a target container.
   * @param {Object} opts
   * @param {string} opts.bibPath        Path to the .bib file (relative to the page).
   * @param {HTMLElement} opts.target    Container element.
   * @param {Object} [opts.labels]       Optional bilingual labels override.
   */
  async function renderPublications(opts) {
    const { bibPath, target, labels = {} } = opts;
    const L = Object.assign({
      search: "Search by keyword…",
      type: "Type",
      allTypes: "All types",
      allVenues: "All venues",
      sort: "Sort",
      newest: "Newest first",
      oldest: "Oldest first",
      countLabel: (n) => `${n} publications`,
      loading: "Loading publications…",
      empty: "No matching publications.",
      stats: { papers: "Papers", firstAuthor: "First-author", corresponding: "Corresponding", venues: "Venues" },
      yearHeading: (y) => `${y}`,
      noYear: "Undated",
      ownerName: "huang, yu-an"
    }, labels);

    target.innerHTML = `<p class="pub-empty">${L.loading}</p>`;
    let bibText;
    try {
      const resp = await fetch(bibPath, { cache: "no-store" });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      bibText = await resp.text();
    } catch (err) {
      target.innerHTML = `<p class="pub-empty">⚠️ Failed to load publications.bib — ${escapeHTML(err.message)}</p>`;
      console.error("BibTeX fetch failed", err);
      return;
    }

    const entries = parse(bibText)
      .filter((e) => e.fields.title && e.fields.author)
      .map((e) => ({
        ...e,
        _year: parseInt((e.fields.year || "0").replace(/\D/g, ""), 10) || 0,
        _authors: normalizeAuthors(htmlEntitiesToText(e.fields.author)),
        _search: "",
        _venue: htmlEntitiesToText(e.fields.journal || e.fields.booktitle || e.fields.publisher || "")
      }));

    entries.forEach((e) => { e._search = buildSearchText(e); });

    // Stats
    const stats = computeStats(entries, L.ownerName);

    // Build UI
    target.innerHTML = "";
    if (opts.showStats !== false) {
      const statsEl = document.createElement("div");
      statsEl.className = "pub-stats";
      statsEl.innerHTML = `
        <div class="pub-stat"><span class="num">${stats.total}</span><span class="label">${L.stats.papers}</span></div>
        <div class="pub-stat"><span class="num">${stats.firstAuthor}</span><span class="label">${L.stats.firstAuthor}</span></div>
        <div class="pub-stat"><span class="num">${stats.corresponding}</span><span class="label">${L.stats.corresponding}</span></div>
        <div class="pub-stat"><span class="num">${stats.venues}</span><span class="label">${L.stats.venues}</span></div>
      `;
      target.appendChild(statsEl);
    }

    const controls = document.createElement("div");
    controls.className = "pub-controls";
    controls.innerHTML = `
      <input type="search" placeholder="${L.search}" aria-label="${L.search}" />
      <select aria-label="${L.type}">
        <option value="__all__">${L.allTypes}</option>
      </select>
      <select aria-label="Venue filter">
        <option value="__all__">${L.allVenues}</option>
      </select>
      <select aria-label="${L.sort}">
        <option value="newest">${L.newest}</option>
        <option value="oldest">${L.oldest}</option>
      </select>
      <span class="pub-count"></span>
    `;
    target.appendChild(controls);

    const list = document.createElement("div");
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
    // Populate venue select
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
        // within year: by first author surname
        const an = (a._authors[0] || "").split(",")[0].toLowerCase();
        const bn = (b._authors[0] || "").split(",")[0].toLowerCase();
        return an.localeCompare(bn);
      });

      countEl.textContent = L.countLabel(filtered.length);

      // Group by year
      list.innerHTML = "";
      if (filtered.length === 0) {
        list.innerHTML = `<p class="pub-empty">${L.empty}</p>`;
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
      const div = document.createElement("div");
      div.className = "pub-item";
      const title = htmlEntitiesToText(e.fields.title);
      const venue = e._venue;
      const tag = venueTag(venue);
      const authors = renderAuthors(e._authors, L.ownerName);

      // Look for an external PDF link if present (added by user as `pdf = {...}` or `url = {...}`)
      const pdf = htmlEntitiesToText(e.fields.pdf || "");
      const url = htmlEntitiesToText(e.fields.url || "");
      const doi = htmlEntitiesToText(e.fields.doi || "");
      const code = htmlEntitiesToText(e.fields.code || "");

      const links = [];
      if (pdf) links.push(`<a href="${escapeHTML(pdf)}" target="_blank" rel="noopener">PDF</a>`);
      if (code) links.push(`<a href="${escapeHTML(code)}" target="_blank" rel="noopener">Code</a>`);
      if (doi) {
        const doiUrl = doi.startsWith("http") ? doi : `https://doi.org/${doi}`;
        links.push(`<a href="${escapeHTML(doiUrl)}" target="_blank" rel="noopener">DOI</a>`);
      } else if (url) {
        links.push(`<a href="${escapeHTML(url)}" target="_blank" rel="noopener">Link</a>`);
      }
      const linksHTML = links.length ? `<div class="pub-links">${links.join(" ")}</div>` : "";

      div.innerHTML = `
        <div class="pub-num">${escapeHTML(e.key.replace(/[^a-zA-Z0-9]/g, "").slice(0, 6))}</div>
        <div class="pub-body">
          <div class="pub-authors">${authors}</div>
          <div class="pub-title">${escapeHTML(title)}</div>
          <div class="pub-venue">${escapeHTML(venue)}${e.fields.volume ? `, ${escapeHTML(htmlEntitiesToText(e.fields.volume))}` : ""}${e.fields.number ? `(${escapeHTML(htmlEntitiesToText(e.fields.number))})` : ""}${e.fields.pages ? `: ${escapeHTML(htmlEntitiesToText(e.fields.pages))}` : ""} <span class="pub-year-inline" style="color:var(--c-text-muted);font-family:var(--font-mono);">${e._year || ""}</span>${tag}</div>
          ${linksHTML}
        </div>
      `;
      return div;
    }

    search.addEventListener("input", render);
    typeSel.addEventListener("change", render);
    venueSel.addEventListener("change", render);
    sortSel.addEventListener("change", render);

    render();
  }

  function computeStats(entries, ownerName) {
    const ownerLower = (ownerName || "huang, yu-an").toLowerCase();
    let firstAuthor = 0, corresponding = 0;
    const venueSet = new Set();
    entries.forEach((e) => {
      if (e._venue) venueSet.add(e._venue);
      const authors = e._authors;
      if (authors[0] && authors[0].toLowerCase().startsWith(ownerLower)) firstAuthor++;
      // Corresponding authors are often marked by an asterisk in HTML lists,
      // but in BibTeX there's no standard. We'll leave this as 0 unless user
      // adds a custom field. To approximate: if owner appears anywhere, count.
      if (authors.some((a) => a.toLowerCase().startsWith(ownerLower))) corresponding++;
    });
    return {
      total: entries.length,
      firstAuthor,
      corresponding,
      venues: venueSet.size
    };
  }

  // Expose globally
  window.BibTeX = { parse, renderPublications };
})();

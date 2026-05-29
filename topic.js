(function () {
  const PAGE_SIZE = 20;
  const search = document.getElementById("search");
  const list = document.getElementById("post-list");
  const empty = document.getElementById("empty-state");
  const resultCount = document.getElementById("result-count");
  const pagination = document.getElementById("pagination");
  const cards = Array.from(list.querySelectorAll(".post-card"));

  function publishedTimestamp(card) {
    const raw = card.dataset.published || "";
    const t = Date.parse(raw);
    return Number.isNaN(t) ? 0 : t;
  }

  cards.sort((a, b) => publishedTimestamp(b) - publishedTimestamp(a));
  cards.forEach((card) => list.appendChild(card));

  let currentPage = 1;

  function readUrlState() {
    const params = new URLSearchParams(window.location.search);
    const page = parseInt(params.get("page") || "1", 10);
    currentPage = Number.isFinite(page) && page > 0 ? page : 1;
    if (search && params.get("q")) {
      search.value = params.get("q");
    }
  }

  function writeUrlState() {
    const params = new URLSearchParams();
    const q = (search.value || "").trim();
    if (q) params.set("q", q);
    if (currentPage > 1) params.set("page", String(currentPage));
    const query = params.toString();
    const next = query ? `${window.location.pathname}?${query}` : window.location.pathname;
    window.history.replaceState(null, "", next);
  }

  function getFilteredCards() {
    const q = (search.value || "").trim().toLowerCase();
    return cards.filter((card) => {
      const title = card.dataset.title || "";
      const tags = card.dataset.tags || "";
      const category = card.dataset.category || "";
      return (
        !q ||
        title.includes(q) ||
        tags.includes(q) ||
        category.toLowerCase().includes(q)
      );
    });
  }

  function renderPagination(totalPages) {
    if (!pagination) return;
    if (totalPages <= 1) {
      pagination.hidden = true;
      pagination.innerHTML = "";
      return;
    }

    pagination.hidden = false;
    const parts = [];

    parts.push(
      `<button type="button" class="page-btn" data-page="prev" ${
        currentPage <= 1 ? "disabled" : ""
      } aria-label="이전 페이지">←</button>`
    );

    const windowSize = 5;
    let start = Math.max(1, currentPage - Math.floor(windowSize / 2));
    let end = Math.min(totalPages, start + windowSize - 1);
    start = Math.max(1, end - windowSize + 1);

    if (start > 1) {
      parts.push(`<button type="button" class="page-btn" data-page="1">1</button>`);
      if (start > 2) parts.push('<span class="page-ellipsis">…</span>');
    }

    for (let p = start; p <= end; p += 1) {
      parts.push(
        `<button type="button" class="page-btn${
          p === currentPage ? " active" : ""
        }" data-page="${p}"${p === currentPage ? ' aria-current="page"' : ""}>${p}</button>`
      );
    }

    if (end < totalPages) {
      if (end < totalPages - 1) parts.push('<span class="page-ellipsis">…</span>');
      parts.push(
        `<button type="button" class="page-btn" data-page="${totalPages}">${totalPages}</button>`
      );
    }

    parts.push(
      `<button type="button" class="page-btn" data-page="next" ${
        currentPage >= totalPages ? "disabled" : ""
      } aria-label="다음 페이지">→</button>`
    );

    pagination.innerHTML = parts.join("");
  }

  function goToPage(page) {
    const filtered = getFilteredCards();
    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    currentPage = Math.min(Math.max(1, page), totalPages);
    writeUrlState();
    applyView();
  }

  function updateCount(visible, totalFiltered, totalPages) {
    if (visible === 0) {
      resultCount.textContent = "검색 결과 없음";
      return;
    }
    const from = (currentPage - 1) * PAGE_SIZE + 1;
    const to = Math.min(currentPage * PAGE_SIZE, totalFiltered);
    if (totalFiltered === cards.length && totalPages <= 1) {
      resultCount.textContent = `${cards.length}개 글`;
    } else {
      resultCount.textContent = `${from}–${to} / ${totalFiltered}개 · ${currentPage}/${totalPages}페이지`;
    }
  }

  function applyView() {
    const filtered = getFilteredCards();
    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));

    if (currentPage > totalPages) currentPage = totalPages;

    cards.forEach((card) => {
      card.hidden = true;
    });

    let visibleOnPage = 0;
    filtered.forEach((card, index) => {
      const page = Math.floor(index / PAGE_SIZE) + 1;
      if (page === currentPage) {
        card.hidden = false;
        visibleOnPage += 1;
      }
    });

    empty.hidden = filtered.length > 0;
    list.hidden = filtered.length === 0;
    updateCount(visibleOnPage, filtered.length, totalPages);
    renderPagination(totalPages);

    if (filtered.length > 0 && visibleOnPage === 0) {
      currentPage = 1;
      applyView();
    }
  }

  if (pagination) {
    pagination.addEventListener("click", (e) => {
      const btn = e.target.closest(".page-btn");
      if (!btn || btn.disabled) return;
      const raw = btn.dataset.page;
      if (raw === "prev") goToPage(currentPage - 1);
      else if (raw === "next") goToPage(currentPage + 1);
      else goToPage(parseInt(raw, 10));
      list.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  search.addEventListener("input", () => {
    currentPage = 1;
    writeUrlState();
    applyView();
  });

  readUrlState();
  applyView();
})();

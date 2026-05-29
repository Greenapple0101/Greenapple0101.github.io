(function () {
  const search = document.getElementById("search");
  const list = document.getElementById("post-list");
  const empty = document.getElementById("empty-state");
  const resultCount = document.getElementById("result-count");
  const filterTags = document.getElementById("filter-tags");
  const cards = Array.from(list.querySelectorAll(".post-card"));

  const categories = [...new Set(cards.map((c) => c.dataset.category))].sort(
    (a, b) => a.localeCompare(b, "ko")
  );

  let activeCategory = "";

  function updateCount(visible) {
    resultCount.textContent =
      visible === cards.length
        ? `${cards.length}개 글`
        : `${visible} / ${cards.length}개`;
  }

  function applyFilters() {
    const q = (search.value || "").trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const title = card.dataset.title || "";
      const tags = card.dataset.tags || "";
      const category = card.dataset.category || "";
      const matchSearch =
        !q || title.includes(q) || tags.includes(q) || category.toLowerCase().includes(q);
      const matchCategory = !activeCategory || category === activeCategory;
      const show = matchSearch && matchCategory;
      card.hidden = !show;
      if (show) visible += 1;
    });

    empty.hidden = visible > 0;
    list.hidden = visible === 0;
    updateCount(visible);
  }

  categories.forEach((cat) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "filter-btn";
    btn.textContent = cat;
    btn.addEventListener("click", () => {
      activeCategory = activeCategory === cat ? "" : cat;
      filterTags.querySelectorAll(".filter-btn").forEach((b) => {
        b.classList.toggle("active", b.textContent === activeCategory);
      });
      applyFilters();
    });
    filterTags.appendChild(btn);
  });

  search.addEventListener("input", applyFilters);
  updateCount(cards.length);
})();

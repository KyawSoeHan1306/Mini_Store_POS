document.addEventListener("DOMContentLoaded", function () {
    // Elements
    const salesSearch = document.getElementById("sales-search");
    const searchButton = document.getElementById("search-button");
    const dateFrom = document.getElementById("date-from");
    const dateTo = document.getElementById("date-to");
    const filterButton = document.getElementById("filter-button");

    // Set default date range (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);

    if (!dateTo.value) dateTo.valueAsDate = today;
    if (!dateFrom.value) dateFrom.valueAsDate = thirtyDaysAgo;

    /**
     * Helper: Update URL with params and reload
     */
    function updateURL(params) {
        const url = new URL(window.location.href);

        // Merge provided params
        for (const key in params) {
            if (params[key]) {
                url.searchParams.set(key, params[key]);
            } else {
                url.searchParams.delete(key);
            }
        }

        // Always reset page when filtering
        url.searchParams.delete("page");
        window.location.href = url.toString();
    }

    /**
     * 🔍 Search functionality
     */
    searchButton.addEventListener("click", function () {
        const query = salesSearch.value.trim();
        updateURL({ search: query });
    });

    salesSearch.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            searchButton.click();
        }
    });

    /**
     * 📅 Date filter functionality
     */
    filterButton.addEventListener("click", function () {
        const fromDate = dateFrom.value;
        const toDate = dateTo.value;

        if (fromDate && toDate && new Date(fromDate) > new Date(toDate)) {
            alert("⚠️ 'From' date cannot be after 'To' date.");
            return;
        }

        updateURL({ from_date: fromDate, to_date: toDate });
    });

    /**
     * Initialize form values from URL params
     */
    const urlParams = new URLSearchParams(window.location.search);

    const searchParam = urlParams.get("search");
    const fromDateParam = urlParams.get("from_date");
    const toDateParam = urlParams.get("to_date");

    if (searchParam) salesSearch.value = searchParam;
    if (fromDateParam) dateFrom.value = fromDateParam;
    if (toDateParam) dateTo.value = toDateParam;

    /**
     * Small UX enhancement: highlight active filters
     */
    if (searchParam) {
        salesSearch.style.border = "2px solid #007bff";
    }
    if (fromDateParam || toDateParam) {
        filterButton.classList.add("btn-success");
        filterButton.innerHTML = '<i class="fas fa-filter"></i> Filtered';
    }
});

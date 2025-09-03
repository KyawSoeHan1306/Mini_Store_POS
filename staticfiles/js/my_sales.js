// static/js/my_sales.js
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    var salesSearch = document.getElementById('sales-search');
    var searchButton = document.getElementById('search-button');
    var dateFrom = document.getElementById('date-from');
    var dateTo = document.getElementById('date-to');
    var filterButton = document.getElementById('filter-button');

    // Set initial date values
    var today = new Date();
    var thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);

    dateTo.valueAsDate = today;
    dateFrom.valueAsDate = thirtyDaysAgo;

    // Search functionality
    searchButton.addEventListener('click', function() {
        var searchQuery = salesSearch.value.trim();
        var url = new URL(window.location.href);

        if (searchQuery) {
            url.searchParams.set('search', searchQuery);
        } else {
            url.searchParams.delete('search');
        }

        url.searchParams.delete('page');
        window.location.href = url.toString();
    });

    salesSearch.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchButton.click();
        }
    });

    // Date filter functionality
    filterButton.addEventListener('click', function() {
        var fromDate = dateFrom.value;
        var toDate = dateTo.value;
        var url = new URL(window.location.href);

        if (fromDate) {
            url.searchParams.set('from_date', fromDate);
        } else {
            url.searchParams.delete('from_date');
        }

        if (toDate) {
            url.searchParams.set('to_date', toDate);
        } else {
            url.searchParams.delete('to_date');
        }

        url.searchParams.delete('page');
        window.location.href = url.toString();
    });

    // Initialize search field from URL parameters
    var urlParams = new URLSearchParams(window.location.search);
    var searchParam = urlParams.get('search');
    var fromDateParam = urlParams.get('from_date');
    var toDateParam = urlParams.get('to_date');

    if (searchParam) {
        salesSearch.value = searchParam;
    }

    if (fromDateParam) {
        dateFrom.value = fromDateParam;
    }

    if (toDateParam) {
        dateTo.value = toDateParam;
    }
});
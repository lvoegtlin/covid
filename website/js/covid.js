$(document).ready(function() {

    google.charts.load('current', {packages: ['corechart', 'controls']});
    google.charts.setOnLoadCallback(init);

    // Show Scroll to Top
    var searchBox = $('#search-box');
    var header = $('.page-header');
    $(window).scroll(function () {
        var height = header.outerHeight();
        if ($(this).scrollTop() > height) {
            $('#back-to-top').fadeIn();
            searchBox.addClass('sticky');
        } else {
            $('#back-to-top').fadeOut();
            searchBox.removeClass('sticky');
        }
    });

    // Scroll to Top
    $('#back-to-top').click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 'slow');
        return false;
    });

    // Scroll to Country Anchor
    $('.anchor').on('click', function(e) {
        e.preventDefault();
        var target = $($(this).attr('href'));
        $('html,body').animate({scrollTop: target.offset().top - 80}, 'slow');
    });

    //Toggle/hide a country
    $(document).on('click', '.hide-country', function(e) {
        e.preventDefault();
        var that = $(this);
        var parent = that.parent().parent().parent();
        var key = parent.attr('id');
        toggleCountryData(key);
    });

});

var initial = ['switzerland', 'germany', 'us', 'world-wide'];
var countries = [];
var countries_data = {};

/**
 * Load data from ./data/data-example.json
 * Add an entry for each country and load data
 */
function init() {
    var countryList = getCountryList();
    loadTemplate(function(template) {
        loadData(function() {
            setupCountryList(countries_data, template);
            toggleCountryData(countryList);
            setupTypeahead();
        });
    });
}

/**
 * Get Countries to display from local storage
 */
function getCountryList() {
    var countryListString = localStorage.getItem('countryList');
    return countryListString ? countryListString.split('|') : initial;
}

/**
 * Update Countries to display in local storage
 */
function updateCountryList() {
    var countryList = [];
    $.each(countries_data, function(key, country) {
        if (country.shown) {
            countryList.push(key);
        }
    });
    var countryListString = countryList.join('|');
    localStorage.setItem('countryList', countryListString)
}

/**
 * Load Template for Countries
 * @param cb
 */
function loadTemplate(cb) {
    var url = 'data/template.html?_t='+new Date().getTime();
    $.get(url, function(data) {
        cb(data);
    });
}

/**
 * Load Country data from JSON
 * @param cb
 */
function loadData(cb) {
    var url = 'data/data.json?_t='+new Date().getTime();
    $.get(url, function(data) {
        $.each(data.country_data, function(i, country) {
            country.key = country.key.replace(/ /g, '-').replace(/[()'*,]/g, '');
            countries_data[country.key] = country;
            countries.push({name:country.name, key:country.key});
        });
        cb();
    });
}

/**
 * Setup Typeahead for country filter
 */
function setupTypeahead() {
    var th = $('#search-box .typeahead');
    th.typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },  {
        name: 'countries',
        source: countryMatcher(),
        display: 'name'
    });
    th.bind('typeahead:select', function(e, country) {
        toggleCountryData(country.key, country.key);
        th.typeahead('val', '');
        th.blur();
    });
}

/**
 * Setup Simple Matcher
 */
function countryMatcher() {
    return function findMatches(q, cb) {
        var matches, substringRegex;
        matches = [];
        substringRegex = new RegExp(q, 'i');
        $.each(countries, function(i, country) {
            if (substringRegex.test(country.name)) {
                matches.push(country);
            }
        });
        cb(matches);
    };
}

/**
 * Setup template for each country
 * @param countries
 * @param template
 */
function setupCountryList(countries, template) {
    var countryList = $('#country-list');
    $.each(countries, function(i, country) {
        var templateInstance = $(template);
        templateInstance.attr('id', country.key);
        templateInstance.find('.country-title').html(country.name + '<a class="hide-country">(hide)</a>');
        templateInstance.find('.collapse').attr('id', 'collapse-'+country.key);
        templateInstance.find('.filter').attr('id', 'filter-'+country.key);
        templateInstance.find('.country-graph').attr('id', 'graph-'+country.key);
        var header = templateInstance.find('.card-header');
        header.attr('id', 'header-'+country.key);
        var btn = header.find('button');
        btn.data('target', '#collapse-'+country.key);
        btn.attr('data-target', '#collapse-'+country.key);
        btn.html('Report for ' + country.name);
        if (country.key === 'switzerland') {
            countryList.prepend(templateInstance);
        } else {
            countryList.append(templateInstance);
        }
    });
}

/**
 * Load report data for each country
 * Initialize graphs for each country
 * @param countries_keys
 * @param goto
 */
function toggleCountryData(countries_keys, goto) {
    countries_keys = (Array.isArray(countries_keys)) ? countries_keys : [countries_keys];
    var countryList = $('#country-list');
    $.each(countries_keys, function(i, key) {
        var country = countries_data[key];
        var countryContainer = countryList.find('#'+country.key);
        if (country.loaded !== true) {
            loadGraph(countryContainer.find('.country-graph'), countryContainer.find('.country-dashboard'), country);
            loadReport(countryContainer.find('.country-report'), country.report);
        }
        //Scroll to added country
        if (goto && goto === country.key) {
            country.shown = true;
            countryContainer.removeClass('d-none');
            var target = $('#'+goto);
            $('html,body').animate({scrollTop: target.offset().top - 80}, 'slow');
        } else {
            country.shown = !country.shown;
            countryContainer.toggleClass('d-none');
        }
    });
    updateCountryList();
}

/**
 * Render graph to country-graph container
 * @param chartContainer
 * @param dashboardContainer
 * @param countryData
 */
function loadGraph(chartContainer, dashboardContainer, countryData) {
    var graph = countryData.graph;
    var dates = countryData.dates;
    var headers = countryData.headers;
    var headerConfig = {
        original: {
            type: 'number',
            longName: 'Original Data',
            shortName: 'Original',
            series: {color: '#000000', pointShape: 'circle', pointSize: 6, lineWidth: 0}
        },
        logistic: {
            type: 'number',
            longName: 'Logistic Curve',
            shortName: 'Logistic',
            series: {color: '#0000ff', lineDashStyle: [10, 4]}
        },
        exponential: {
            type: 'number',
            longName: 'Exponential Curve',
            shortName: 'Exponential',
            series: {color: '#ff0000', lineDashStyle: [10, 4]}
        },
    };

    var chartData = new google.visualization.DataTable();
    chartData.addColumn('date', 'Date');

    var series = {};
    var data = prepareData(graph, dates);
    $.each(headers, function(i, headerKey) {
        var header = headerConfig[headerKey];
        chartData.addColumn(header.type, header.longName);
        series[i] = header.series;
    });
    chartData.addRows(data);

    var options = {
        tooltip: {
            isHtml: true
        },
        focusTarget: 'category',
        curveType: 'function',
        interpolateNulls: true,
        chartArea: {
            width: '80%',
            height: '80%'
        },
        legend: {
            position: 'in',
            textStyle: {
                bold: false,
                fontSize: 16
            }
        },
        hAxis: {
            title: 'Date',
            titleTextStyle: {
                bold: true,
                fontSize: 16,
                italic: false
            }
        },
        vAxis: {
            format: '0',
            title: 'Total Cases',
            titleTextStyle: {
                bold: true,
                fontSize: 16,
                italic: false
            }
        },
        series: series
    };

    var dashboard = new google.visualization.Dashboard(dashboardContainer.get(0));
    var dateRangeSlider = new google.visualization.ControlWrapper({
        'controlType': 'DateRangeFilter',
        'containerId': 'filter-'+countryData.key,
        'options': {
            'filterColumnLabel': 'Date'
        }
    });
    var lineChart = new google.visualization.ChartWrapper({
        chartType: 'LineChart',
        containerId: chartContainer.attr('id'),
        options: options
    });

    dashboard.bind(dateRangeSlider, lineChart);
    dashboard.draw(chartData);

    countryData.loaded = true;
}

/**
 * Column 0 contains DateString ('yyyy-MM-dd') which is parsed as Date
 * @param graph
 * @param dates
 */
function prepareData(graph, dates) {
    return dates.map(function(row, idx) {
        return [new Date(row)].concat(graph[idx]);
    });
}

/**
 * Add report to country-report container
 * @param container
 * @param data
 */
function loadReport(container, data) {
    var report = data.join('<br/>');
    var countryReport = $("<div>"+report+"</div>");
    container.append(countryReport);
}
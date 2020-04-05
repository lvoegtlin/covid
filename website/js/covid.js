$(document).ready(function() {

    loadReports();

    google.charts.load('current', {packages: ['corechart', 'controls']});
    google.charts.setOnLoadCallback(init);

    // Show Scroll to Top
    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
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
        $('html,body').animate({
                scrollTop: target.offset().top
            }, 'slow');
    });

});

/**
 * Load Reports for all countries
 * @deprecated
 */
function loadReports() {
    $('.report-container').each(function () {
        var that = $(this);
        var src = that.data('src');
        var url = 'reports/'+src+'.html?_t='+new Date().getTime();
        $.get(url, function(data) {
            that.html(data);
        });
    });
}

/**
 * Load data from ./data/data-example.json
 * Add an entry for each country and load data
 */
function init() {
    loadTemplate(function(template) {
        loadData(function(data) {
            if (data && data.country_data) {
                setupCountryList(data.country_data, template);
                setupCountryData(data.country_data);
            }
        });
    });

}
function loadTemplate(cb) {
    var url = 'data/template.html?_t='+new Date().getTime();
    $.get(url, function(data) {
        cb(data);
    });
}
function loadData(cb) {
    var url = 'data/data.json?_t='+new Date().getTime();
    $.get(url, function(data) {
        cb(data);
    });
}

/**
 * Setup template for each country
 * @param countries
 */
function setupCountryList(countries, template) {
    var countryList = $('#country-list');
    $.each(countries, function(i, country) {
        country.key = country.key.replace(/ /g, '-').replace(/[()'*,]/g, '');
        var templateInstance = $(template);
        templateInstance.find('.country').attr('id', country.key);
        templateInstance.find('.country-title').html(country.name);
        templateInstance.find('.collapse').attr('id', 'collapse-'+country.key);
        templateInstance.find('.filter').attr('id', 'filter-'+country.key);
        templateInstance.find('.country-graph').attr('id', 'graph-'+country.key);
        var header = templateInstance.find('.card-header');
        header.attr('id', 'header-'+country.key);
        var btn = header.find('button');
        btn.data('target', '#collapse-'+country.key);
        btn.attr('data-target', '#collapse-'+country.key);
        btn.html('Report for ' + country.name);
        countryList.append(templateInstance);
    });
}

/**
 * Load report data for each country
 * Initialize graphs for each country
 * @param countries
 */
function setupCountryData(countries) {
    var countryList = $('#country-list');
    $.each(countries, function(i, country) {
        var countryContainer = countryList.find('#'+country.key);
        loadGraph(countryContainer.find('.country-graph'), countryContainer.find('.country-dashboard'), country);
        loadReport(countryContainer.find('.country-report'), country.report);
    });
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
            series: {color: '#000000', pointShape: 'circle', pointSize: 10, lineWidth: 0}
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
    if (data[0].length === 2) {
        headers = ['original'];
    }
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
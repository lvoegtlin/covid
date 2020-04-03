$(document).ready(function() {

    loadReports();

    google.charts.load('current', {packages: ['corechart']});
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
    //TODO switch to data.json
    var url = 'data/data.json?_t='+new Date().getTime();
    $.get(url, function(data) {
        if (data && data.countries) {
            setupCountryList(data.countries);
            setupCountryData(data.countries);
        }
    });
}

/**
 * Setup template for each country
 * @param countries
 */
var template = "<div class=\"row\"> <div class=\"col-12 country\" id=\"\"> <h1 class=\"country-title\"></h1> <div class=\"country-graph\"></div><div class=\"country-report\"></div></div></div><hr class=\"mb-4 mt-5\"/>";
function setupCountryList(countries) {
    var countryList = $('#country-list');
    $.each(countries, function(i, country) {
        var templateInstance = $(template);
        templateInstance.find('.country').attr('id', country.key);
        templateInstance.find('.country-title').html(country.name);
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
        loadGraph(countryContainer.find('.country-graph'), country.graph, country.dates, country.headers);
        loadReport(countryContainer.find('.country-report'), country.report);
    });
}

/**
 * Render graph to country-graph container
 * @param container
 * @param graph
 * @param dates
 * @param dates
 */
function loadGraph(container, graph, dates, headers) {

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
    $.each(headers, function(i, headerKey) {
        var header = headerConfig[headerKey];
        chartData.addColumn(header.type, header.longName);
        series[i] = header.series;
    });

    var data = prepareData(graph, dates);
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

    var chart = new google.visualization.LineChart(container.get(0));
    chart.draw(chartData, options);
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
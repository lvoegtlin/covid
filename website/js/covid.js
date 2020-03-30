$(document).ready(function() {
    loadReports();
});

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
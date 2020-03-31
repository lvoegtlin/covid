$(document).ready(function() {

    loadReports();

    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });

    $('#back-to-top').click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 'slow');
        return false;
    });

    $('.anchor').on('click', function(e) {
        e.preventDefault();
        var target = $($(this).attr('href'));
        $('html,body').animate({
                scrollTop: target.offset().top
            }, 'slow');
    });

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
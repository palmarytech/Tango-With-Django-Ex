$(document).ready(function () {
    $('#like_btn').click(function(){
        var categoryIdVar;
        categoryIdVar = $(this).attr('data-categoryid');

        $.get("/rango/like_category",
        {'category_id':categoryIdVar},
        function (data) {
            $('#like_count').html(data);
            $('#like_btn').hide();
          })
    });

    $('#search-input').keyup(function () { 
        var query;
        query = $(this).val();

        $.get('/rango/suggest',
        {'suggestion': query},
        function(data){
            $('#categories-listing').html(data);
        })
    });

    $('.rango-page-add').click(function () { 
        var categoryid = $(this).attr('data-categoryid');
        var title = $(this).attr('data-title');
        var url = $(this).attr('data-url');
        var clickButton = $(this);

        $.get('/rango/search_add_pages/',
        {'category_id': categoryid, 'title': title, 'url': url},
        function(data){
            $('#page-listing').html(data);
            clickButton.hide();
        })
    });
});
var backendServer = 'http://127.0.0.1:5000/';

$(document).ready(function() {
    searchArticles();
});

var searchArticles = function searchArticles() {
    var query = getUrlParameter('q');

    $.ajax({
        type: 'GET',
        url: backendServer + 'search?q=' + query,
        success: function(articles) {
            $.each(articles, function(i, article) {
                var htmlArticle = createArticle(article);
                $('.results').append(htmlArticle);
            });
            $('.search input').val(query);
        },
        error: function(e) {
            console.log(e)
        }
    });
}

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
};

var createArticle = function createArticle(article) {
    return $([
        '<div class="result-wrapper">',
            '<div class="result">',
                '<div class="result-header">',
                    '<a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">',
                        '<h3>Article Title: ' + article.title + '</h1>',
                        '<p>https://www.youtube.com/watch?v=dQw4w9WgXcQ</p>',
                    '</a>',
                '</div>',
                '<div class="result-source">',
                    '<p class="result-text">' + article.text + '. The text gathered from the backend is just one word, that is why I wrote this long sentence.</p>',
                    '<div class="result-topics">',
                        '<p class="topic">Topic 1</p>',
                        '<p class="topic">Topic 2</p>',
                        '<p class="topic">Topic 3</p>',
                    '</div>',
                    '<div class="result-stats">',
                        '<p class="stats">Stats: 12%</p>',
                        '<p class="stats">PageRank: ' + article.pagerank + '</p>',
                        '<p class="stats">Linking Index: 12</p>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>'
    ].join("\n"));
}
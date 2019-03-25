var backendServer = 'http://127.0.0.1:5000/';

$(document).ready(function() {
    searchArticles();
});

var searchArticles = function searchArticles() {
    var query = getUrlParameter('q');

    $('#search input').val(replacePlus(query, ' '));

    $.ajax({
        type: 'GET',
        url: backendServer + 'search?q=' + replacePlus(query),
        success: function(articles) {
            $.each(articles, function(i, article) {
                var htmlArticle = createArticle(article);
                $('#results').append(htmlArticle);
            });
            $('#result-count p').html('About ' + articles.length + ' search results')
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
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]).replace(/\++$/, "");
        }
    }
};

var replacePlus = function replacePlus(input, repl = ",") {
    return input.replace(/\+/g, repl);
}

var createArticle = function createArticle(article) {
    return $([
        '<div class="result-wrapper">',
            '<div class="result">',
                '<div class="result-header">',
                    '<a href="https://en.wikipedia.org/wiki/' + ((article.title).replace(/\s/g, '_')).replace(/[!'()*]/g, escape) + '">',
                        '<h3>' + article.title + '</h1>',
                        '<p>https://en.wikipedia.org/wiki/' + ((article.title).replace(/\s/g, '_')).replace(/[!'()*]/g, escape) + '</p>',
                    '</a>',
                '</div>',
                '<div class="result-source">',
                    '<p class="result-text">' + article.text + '. The text gathered from the backend is just one word, that is why I wrote this long sentence.</p>',
                    '<div class="result-topics">',
                        getTopics(article),
                    '</div>',
                    '<div class="result-stats">',
                        '<p class="stats">Cosine Similarity:' + article.cosine_sim + '</p>',
                        '<p class="stats">PageRank: ' + article.pagerank + '</p>',
                        '<p class="stats">Harmonic Mean:' + article.harmonic_mean + '</p>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>'
    ].join("\n"));
}

var getTopics = function getTopics(article) {
    topics = "";

    $.each(article.topics, function(i, topic) {
        topics += '<p class="topic">' + topic + '</p>';
    });

    return topics;
}
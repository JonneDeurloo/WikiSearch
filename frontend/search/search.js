var backendServer = 'http://127.0.0.1:5000/';

$(document).ready(function() {
    // Validate Enter Press
    $( "#search-form" ).submit(function( event ) {
        validate();
        event.preventDefault();
    });

    // Search for articles
    searchArticles();
});

/** Validate form */
function validate() {
    if ( $('.search-bar input').val().trim() !== "" ) {
        document.forms[0].submit();
    }
}

/** Query the server for search results */
function searchArticles() {
    $("#loadbar").removeClass('hidden');

    var query = getUrlParameter('q');
    var start = new Date().getTime();

    $('#search input').val(replacePlus(query, ' '));

    // Send request to the server
    $.ajax({
        type: 'GET',
        url: backendServer + 'search?q=' + replacePlus(query),
        success: function(articles) {
            $.each(articles, function(i, article) {
                var htmlArticle = createArticle(article);
                $('#results').append(htmlArticle);
            });

            var end = new Date().getTime();
            if (articles.length > 0) {
                $('#result-count p').html('About ' + articles.length + ' search results (' + (end - start) / 1000 + ' seconds)');
            } else {
                $('#result-count p').html('No results found...');
            }

        },
        error: function(e) {
            console.log(e)
        },
        complete: function() {
            $("#loadbar").addClass('hidden');
        }
    });
}

/** Get parameters from the URL */
function getUrlParameter(sParam) {
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

/** Create article html object */
function createArticle(article) {
    var url = 'https://en.wikipedia.org/wiki/' + escapeHTML(article.title);
    return $([
        '<div class="result-wrapper">',
            '<div class="result">',
                '<div class="result-header">',
                    '<a href="' + url + '">',
                        '<h3>' + article.title + '</h1>',
                        '<br>',
                        '<p>' + url + '</p>',
                    '</a>',
                '</div>',
                '<div class="result-source">',
                    '<p class="result-text">' + article.text + '</p>',
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


// Helper functions

/** Replaces plus in string with replacement */ 
function replacePlus(input, repl = ",") {
    return input.replace(/\+/g, repl);
}

/** Escape characters to HTML format */
function escapeHTML(input) {
    return (input.replace(/\s/g, '_')).replace(/[!'*]/g, escape);
}

/** Get <p> tag list of topics from article */
function getTopics(article) {
    if (article.topics.length > 0) {

        topics = '<p class="topic">Topics:</p>';

        $.each(article.topics, function (i, topic) {
            topics += '<p class="topic">' + topic + '</p>';
        });

        return topics;
    } else {
        return "";
    }
}
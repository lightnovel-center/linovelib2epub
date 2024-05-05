$(document).ready(function () {
    var prevpage = "/novel/2600/catalog";
    var nextpage = "/novel/2600/100948.html";
    var bookpage = "/novel/2600.html";
    $("body").keydown(function (event) {
        var isInput = event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA';
        if (!isInput) {
            if (event.keyCode == 37) {
                location = prevpage
            } else if (event.keyCode == 39) {
                location = nextpage
            }
        }
    })
});
function refreshTag(url, tagId, refreshRate) {
    function refresh() {
        $.getJSON(url, function(data) {
            if (data.finished == true) {
                $(tagId).html(data.html);
            } else {
                window.setTimeout(refresh, refreshRate);
            }
        });
    };
    window.setTimeout(refresh, refreshRate);
};

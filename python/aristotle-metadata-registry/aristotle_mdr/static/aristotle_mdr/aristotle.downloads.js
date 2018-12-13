let interval = setInterval(getDownloadStatus, 1000);
let downloadReady = false;

function success(data) {
    if (data.is_expired) {
        expireDownload();
    }
    else if (data.is_ready && !downloadReady) {
        readyDownload(data.file_details);
    }
}

function getDownloadStatus() {
    $.ajax({
        dataType: 'json',
        url: '/dlstatus',
        data: {format: 'json'},
        contentType: 'application/json',
        success: success
    }).fail(function (error) {
        console.log("failure", error);
    });
}

function expireDownload() {
    let ErrorText = $('<div></div>').text('Your download expired, Please refresh this page to restart download');
    $('#download-link-wrapper>p').html(ErrorText);
    clearInterval(interval);
}

function readyDownload(file_details) {
    downloadReady = true;
    let downloadIcon = $('<i></i>').addClass('fa fa-download');
    let downloadLink = $('<a></a>').text(' Download now');
    let downloadText = $('<div></div>').text('Your download will expire in ' + file_details.ttl + ' minutes.');
    let downloadReadyText = $('<h5></h5>').text('You document is ready to download.');
    downloadText.addClass('small')
    downloadLink.attr({
        'id': 'document-link',
        'download': '',
        'href': file_details.download_url,
        'target': '_blank',
    });
    downloadLink.addClass('btn btn-primary');
    $('#download-link-wrapper>p').html(downloadReadyText);
    downloadLink.prepend(downloadIcon);
    $('#download-link-wrapper>p').append(downloadLink);
    $('#download-link-wrapper>p').append(downloadText);
    initDocumentDownload();
}

function goBackDownloadButton() {
    let goBackButton = $('<button></button>');
    goBackButton.append($('<i></i>').attr("class", "fa fa-arrow-left"));
    goBackButton.append($('<span></span>').text(" Go Back"));
    goBackButton.attr({
        id: 'go-back-button',
        onclick: 'history.go(-1)',
        class: 'btn btn-primary pull-left'
    });
    if (history.length <= 1) {
        goBackButton.attr('disabled', '')
    }
    $('div#download-nav-controls').append(goBackButton);
}

function getDownload() {
    $('a#document-link').click(function (event) {
        let thankYouDownload = $('<div></div>').text('Thank you for downloading the document');
        $('#download-link-wrapper>p').html(thankYouDownload);
    })
}

function initDocumentDownload() {
    clearInterval(interval);
    interval = setInterval(getDownloadStatus, 10000);
    getDownload()
}

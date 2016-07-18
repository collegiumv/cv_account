Foundation.Abide.defaults.liveValidate = true;
$(document).foundation()

var HttpRequest = function() {
    this.get = function(Url, Callback) {
	var HttpRequest = new XMLHttpRequest();
	HttpRequest.onreadystatechange = function() {
	    if (HttpRequest.readyState == 4 && HttpRequest.status == 200)
		Callback(HttpRequest.responseText);
	    else
		Callback('error');
	}

	HttpRequest.open( "GET", Url, true );
	HttpRequest.send( null );
	return HttpRequest.responseText;
    }
}

httpClient = new HttpRequest()


$('#netID').on('input', function() {
    var url = '/ums/validate/netID/' + $('#netID').val()
    httpClient.get(url, function(result) {
	if( result == 'true' ) {
	    var url2 = '/ums/validate/exists/byNetID/' + $('#netID').val()
	    result = httpClient.get(url2, function(result) {
		if( result == 'false' ) {
		    showClass($('#provisionAccount'))
		    hideClass($('#provisionButton'))
		    hideClass($('#usernameTaken'))
		    hideClass($('#changePassword'))
		}

		if( result == 'true' ) {
		    showClass($('#changePassword'))
		    hideClass($('#provisionAccount'))
		}
	    })
	    $formError = $('#netID').siblings(".form-error")
	    hideClass($('#netID-error'))
	} else if (result == 'false' ) {
	    hideClass($('#provisionButton'))
	    hideClass($('#changePassword'))
	    hideClass($('#provisionAccount'))
	    showClass($('#netID-error'))
	}
    })
})


$('#username').on('input', function() {
    var url = '/ums/validate/uname/' + $('#username').val()
    if ($('username').val() == '') {
	hideClass($('#provisionButton'))
	showClass($('#username-error'))
    }
    result = httpClient.get(url, function(result) {
	if( result == 'true' ) {
	    var url2 = '/ums/validate/exists/byUID/' + $('#username').val()
	    result = httpClient.get(url2, function(result) {
		if( result == 'false' ) {
		    showClass($('#provisionButton'))
		    hideClass($('#username-error'))
		}

		if( result == 'true' ) {
		    hideClass($('#provisionButton'))
		    showClass($('#username-error'))
		}
	    })
	} else if (result == 'false') {
	    hideClass($('#provisionButton'))
	    showClass($('#username-error'))
	}
    })
})

function showClass(el) {
    el.removeClass("is-hidden");
    el.addClass("is-visible");
}

function hideClass(el) {
    el.removeClass("is-visible");
    el.addClass("is-hidden");
}


function changePassword() {
    var url = '/ums/changePassword/' + $('#netID').val()
    httpClient.get( url, function(result) {
	if( result == 'true' ) {
	    successAlert();
	} else {
	    errorAlert();
	}
    })
}

function createAccount() {
    var url = '/ums/provision/' + $('#netID').val() + "/" + $('#username').val()
    httpClient.get( url, function(result) {
	if( result == 'true' ) {
	    successAlert();
	} else {
	    errorAlert();
	}
    })
}

function successAlert() {
    swal({
	title: "Success!",
	text: "Please check your UT Dallas email for further instructions.",
	type: "success",
    },
    function() {
	window.location.reload();
    })
}

function errorAlert() {
    swal({
	title: "An Error Occurred",
	text: "Please contact cvadmins@utdallas.edu or try again later.",
	type: "error",
    })
}


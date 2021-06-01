function progressBar() {
	var progressBar = $('#progressBar');
	var percentVal = 0;
	var right = true;

  // Show and animate the copy progress bar
	$('#progressBar').css("display", "block")
	// Run the progress bar
	window.setInterval(function(){
	    percentVal += 5;
	    if (right == true) {
		    progressBar.css("margin-right", 100-percentVal+ '%');
	    } else {
		    progressBar.css("margin-left", percentVal+ '%');
	    }


	    if (percentVal == 100 || percentVal == 50 && right)
	    {
		percentVal = 0;
		if (right == true) {
			progressBar.css("margin-left", percentVal+ '%');
			progressBar.css("margin-right", 0+ '%');
		} else {
			progressBar.css("margin-left", 0+ '%');
			progressBar.css("margin-right", 100+ '%');
		}
		right = !right;
	    }

	}, 100);
}

$(document).ready(function() {

	$('form').on('submit', function() {
		$('#progressBar').show()

	});
});

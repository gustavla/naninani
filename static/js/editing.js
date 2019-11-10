
function story_keydown(e)
{
	var keynum;
	if (window.event) // IE
		keynum = e.keyCode;
	else if(e.which) // Netscape/Firefox/Opera
		keynum = e.which;
	else
		return false;
	
	if (keynum == 27)
	{
		var value = document.getElementById('id_story_sv').value;
		var last = value.lastIndexOf(' ');
		//var word = value.substr(last+1,value.length);
		word = value
		
// 		word = word.replace('\'','\’');
		// We're trying to stay away from escape(), since it converts our
		//  unicode too, encodeURI seems to do the trick, but it doesn't handle
		//  semicolon.
		
	//	alert(encodeURI(';'));
		
		if (word!="")
		{
			escaped = encodeURIComponent(word).replace(';', escape(';'));
			ajaxExec('/translate/?word='+escaped, story_ready);
		}

		return false;
	}
}

function story_ready()
{
	if (ajaxOK())
	{
		story = document.getElementById('id_story_sv');

		var content = ajaxContent();
		if (content != "")
			story.value = content;

		return true;
	}
}

function load() 
{
	comment = document.getElementById('id_comment');
	comment.style.width = "400px";
	story = document.getElementById('id_story_sv');
	story.onkeydown=story_keydown;
}
window.onload=load;
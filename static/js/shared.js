


var last_hash;

function deploy(response)
{
	$('kanjicard_wrapper').innerHTML = response;
	$('kanjicard_wrapper').show();
	
	if ($('flashcard_wrapper'))
		$('flashcard_wrapper').hide();
}

function set_from_hash()
{
	var hash=location.hash.substr(1);
	if (hash != last_hash)
	{
		if (hash)
		{
			last_hash = hash;
			$('kanjicard_wrapper').show();
			if ($('flashcard_wrapper'))
				$('flashcard_wrapper').hide();
			load_kanjicard(hash);
		}
		else
		{
			$('kanjicard_wrapper').hide();
			if ($('flashcard_wrapper'))
				$('flashcard_wrapper').show();
		}
	}
}



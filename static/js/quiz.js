

var kanji_queue = Array();
var current_kanji = null;
var current_kanjicard = null; // Could be separate from current_kanji

function update_debug()
{
	debug = $('debug');
	if (debug)
	{
		var value = "DEBUG\n";
	
		kanji_queue.each(function(kanji){
			value += kanji.id + " " + kanji.kanji + " " + kanji.keyword_sv + "\n";
		});
	
		debug.value = value;
	}
}

function store_kanjis(kanjis)
{
	var d = false;
	if (kanji_queue.length == 0 && !current_kanji)
		d = true;
	
	kanjis.each(function(kanji){
		kanji_queue.push(kanji);		
	});
	
	if (d)
	{
		next_kanji();
	}
}

function next_kanji()
{
	// We don't want to load new ones if these aren't set,
	//  because that probably means a process is running but
	//  haven't finished.
	if (kanji_queue.length > 0)
	{
		current_kanji = kanji_queue.shift();
		deploy_flashcard(current_kanji);
//		deploy_kanjicard(current_kanji);
	}

	if (kanji_queue.length <= 3)
	{
		// refill queue
		ajax.fetch_random_kanjis(user_id, store_kanjis);
	}

	update_debug();
}

// Deploys a kanji to the HTML
function deploy_flashcard(kanji)
{
	if (kanji)
	{
		$('flashcard_id').textContent = kanji.id;
		$('flashcard_kanji').textContent = kanji.kanji;
		$('flashcard_keyword_sv').textContent = kanji.keyword_sv;
		$('flashcard_cardlink').href = "/#"+kanji.id;
		$('flashcard_cardlink').href = "/#"+kanji.id;
		$('story_button').onclick = function() { 
			load_kanjicard(kanji.id); 
		}
	}
}

/*function deploy_kanjicard(kanji)
{
	if (kanji)
	{
		current_kanjicard = kanji;
		
		// Notice heisig id and not kanji id.
		if (kanji.kanji_type == 'kanji')
			$('kanjicard_id').textContent = "#"+kanji.heisig; 
		else
			$('kanjicard_id').textContent = "*";
			
		$('kanjicard_kanji').textContent = kanji.kanji;
		$('kanjicard_keyword_sv').textContent = kanji.keyword_sv;
		$('kanjicard_story_sv').innerHTML = kanji.story_sv.replace(/\n/g,"</p><p>");
		
		if (kanji.published)
			$('kanjicard_not_published').hide();
		else
			$('kanjicard_not_published').show();
		
		var link = $('kanjicard_edit_link');
		link.href = "/admin/kanjikeys/kanji/"+kanji.id+"/";
			
		// Open in new window
		link.onclick = function ()
		{
			window.open(this.href);
			return false;
		};
		
		// If Kanji has meanings
		if (kanji.meanings.length > 0)
		{
			$('kanjicard_meanings_wrapper').show();
			$('kanjicard_meanings').textContent = kanji.meanings.join(' / ');
		}
		else
		{
			$('kanjicard_meanings_wrapper').hide();
		}
		
		// If kanji has primitives
		if (kanji.parts.length > 0)
		{
			var text = '';
			kanji.parts.each(function(part){
				text += '<div class="prim_kanji_link" onclick="load_kanjicard(' + part.id + ')">';
				text += '<p class="prim_kanji">' + part.kanji + '</p>';
				text += '<p class="prim_meanings">' + part.meanings.join('<br />') + '</p>';
				text += '</div>';
			});
			$('kanjicard_primitives').innerHTML = text;
		}
		else
		{
			$('kanjicard_primitives').innerHTML = "";
		}
	}
}*/

// This submits the success status and loads a new kanji
function submit_kanji(success)
{
	update_debug();
	reset_flashcard();
	if (success != -1)
		ajax.report_stat(user_id, current_kanji.id, success, function() {});
	next_kanji();
	update_debug();
}

function flip_card()
{
	var key = $('keyword_side');
	var kan = $('kanji_side');
	key.style.display = ((key.style.display=='none')?'inline':'none');
	kan.style.display = ((kan.style.display=='none')?'inline':'none');
}

function reset_flashcard()
{
	$('story_button').style.display = '';
	$('keyword').style.marginTop = '';
	var key = $('keyword_side');
	var kan = $('kanji_side');
	key.style.display = 'inline';
	kan.style.display = 'none';
}

function show_story()
{
	deploy_kanjicard(current_kanji);
	$('flashcard_wrapper').hide();
	$('kanjicard_wrapper').show();
/*	$('story_button').style.display = 'none';
	$('keyword').style.marginTop = '40px';*/
}

function unload_kanjicard()
{
	$('flashcard_wrapper').show();
	$('kanjicard_wrapper').hide();
}

function load_kanjicard(id)
{
	ajax.kanjicard(id, deploy);
}

window.onload = function() {
	ajax.fetch_random_kanjis(user_id, store_kanjis);
	set_from_hash();
}


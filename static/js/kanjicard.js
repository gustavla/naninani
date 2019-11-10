
function load_kanjicard(id)
{
	ajax.kanjicard_lesson(id, deploy);
}


window.onload = function()
{
	set_from_hash();
}
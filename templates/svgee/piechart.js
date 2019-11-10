var piechart{{ key }}=new Array();
{% for part in parts %}
	piechart{{ key }}[{{ part.id }}] = new Array("{{ part.text|safe }}", {{ part.hoverx }}, {{ part.hovery }});
{% endfor %}

var i = 0;
var last_hover_{{ key }} = null;
var last_id_{{ key }} = null;
function hover{{ key }}(evt, id) 
{
	var pos = $('svg_container{{ key }}').positionedOffset();
	var svg_x = pos.left;
	var svg_y = pos.top;
//	if (last_hover)
//		last_hover.setAttribute("fill-opacity", "1");
		
	var segment = $(evt.target.id);
//	segment.setAttribute("fill-opacity", "0.7");
	var relx = segment.pathSegList.getItem(1).x;
	var rely = segment.pathSegList.getItem(1).y;

	var h = $('hover');
	
	// We want to set this value before calling getWidth.
	h.innerHTML = piechart{{ key }}[id][0];
	
	var left = (svg_x + piechart{{ key }}[id][1]);
	if (piechart{{ key }}[id][1] < {{ halfside }})
		left -= h.getWidth();
	
	var top = (svg_y + piechart{{ key }}[id][2]);
	if (piechart{{ key }}[id][2] < {{ halfside }})
		top -= h.getHeight();
	
	var size = document.viewport.getDimensions();
//	alert(document.documentElement.clientWidth + " " + size.width);
	var size = {"width": document.documentElement.clientWidth, "height": document.documentElement.clientHeight + document.viewport.getScrollOffsets().top};

	h.style.left = Math.min(size.width-h.getWidth()-3, Math.max(3, left)) + "px";	
	h.style.top = Math.min(size.height-h.getHeight()-3, Math.max(3, top)) + "px";
		
	h.show();
	h.onmouseout = function() { unhover{{ key }}(evt, true); }
	
	if (last_id_{{ key }} != null && $('pielegend_{{ key }}_' + last_id_{{ key }})) // 0 is still valid
	{
		$('pielegend_{{ key }}_' + last_id_{{ key }}).style.textDecoration = "";
		$('pielegend_{{ key }}_' + last_id_{{ key }}).style.color = "black";
		//$('line_{{ key }}_' + last_id).style.display = "none";
	}
	if (last_id_{{ key }} != null)
	{
		$('backfill_{{ key }}_' + last_id_{{ key }}).setAttribute("fill", "white");
	}
	
	if ($('pielegend_{{ key }}_' + id))
	{
		$('pielegend_{{ key }}_' + id).style.textDecoration = "underline";
		$('pielegend_{{ key }}_' + id).style.color = "#800";
		//$('line_{{ key }}_' + id).style.display = "";
	}

	$('backfill_{{ key }}_' + id).setAttribute("fill", "{{ backfill }}");
	
	last_hover_{{ key }} = segment;
	last_id_{{ key }} = id;
}

function unhover{{ key }}(evt, doit) 
{
	var pos = $('svg_container{{ key }}').positionedOffset();
	var svg_x = pos.left;
	var svg_y = pos.top;
	var segment = evt.target;
	var mx = Event.pointerX(evt);
	var my = Event.pointerY(evt);
	var prex = (mx-svg_x-{{ halfside }});
	var prey = (my-svg_y-{{ halfside }});
	
	// So that it doesn't start blinking if it's above the piechart and the hover object
	if (doit || prex*prex+prey*prey > {{ r }}*{{ r }})
	{
//		var segment = evt.target;
//		segment.setAttribute("fill-opacity", "1.0");
		$('hover').hide();
//		segment.pathSegList.getItem(0).y = segment.pathSegList.getItem(0).y - 10;

		if (last_id_{{ key }} != null && $('pielegend_{{ key }}_' + last_id_{{ key }})) // 0 is still valid
		{
			$('pielegend_{{ key }}_' + last_id_{{ key }}).style.textDecoration = "";
			$('pielegend_{{ key }}_' + last_id_{{ key }}).style.color = "black";
			//$('line_{{ key }}_' + last_id).style.display = "none";
		}
		if (last_id_{{ key }} != null)
		{
			$('backfill_{{ key }}_' + last_id_{{ key }}).setAttribute("fill", "white");
		}
	}
}

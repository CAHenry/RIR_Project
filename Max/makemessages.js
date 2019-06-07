
inlets = 1;
outlets = 1;

setinletassist(0, "msg stimulus room condition action parameter");

var stimuli = ['TakeFive', 'Speech'];
var nDirectSources = [5, 1];
var rooms = ['Library', 'Trapezoid'];
var conditions = ['Direct', '0OA', '1OA', '2OA', '3OA', '4OA'];
var nSourcesPerCondition = [1, 6, 6, 12, 20, 32];

var nsources = 316
var N = 24; // stimuli.length * rooms.length * conditions.length;
var lookuptable = new Array(N);


// Making the look-up table. This has to be coherent with the script CreateXML
/*ind = 0;
source = 1;
for(i=0; i<stimuli.length; i++) {
	for(j=0; j<rooms.length; j++) {
		for(k=0; k<conditions.length; k++) {
			s = conditions_n[k]; // number of sources for this condition
			if(k==0) { // direct
				s = stimuli_n[i];
				direct = [source, source+s-1];
			}	
			lookuptable[ind] = [source, source+s-1];
			ind = ind + 1;
			source = source + s;
		}
	}
}*/
/*
function focus(stimulus,room,condition) {
	stim_ind = findInList(stimulus,stimuli);
	room_ind = findInList(room,rooms);
	cond_ind = findInList(condition,conditions);
	
	nrooms = rooms.length;
	nconds = conditions.length;
	
	ind = stim_ind*nrooms*nconds + room_ind*nconds + cond_ind;
	
	s = lookuptable[ind]
	
	firstSource = s[0];
	lastSource = s[1];
	
	for
	
	
	outlet(0,s);
}*/

function bang() {
	a = [[1, 2],[3, 4]];
	post(a);
}

function msg(stimulus,room,condition,action,parameter) {
	sourceID = 1;
	for(i=0; i<stimuli.length; i++) {
		for(j=0; j<rooms.length; j++) {
			for(k=0; k<conditions.length; k++) {
				nsources = nSourcesPerCondition[k];
				direct = 0;
				if(k==0) { // direct
					direct = 1;
					nsources = nDirectSources[i];
				}
				foundStimAndRoom = 0;
				found = 0;
				if(stimuli[i]==stimulus && rooms[j]==room) {
 					foundStimAndRoom = 1;
					if(conditions[k]==condition || condition=="All") {
						found = 1;
					}
				}
				// post("found="+found+",direct="+direct+",stimroom="+foundStimAndRoom+"\n");
				counter=0;
				lastSourceID = sourceID+nsources-1;
				while(sourceID<=lastSourceID) {	
					//post("sourceID="+sourceID+"\n")
					if(action=="focus") { // focus==unmute this & mute the rest
						oscmsg = "/3DTI-OSC/source"+sourceID+"/mute ";
						if(found || (direct && foundStimAndRoom)) {
							oscmsg = oscmsg + "0";
						} else {
							oscmsg = oscmsg + "1";
						}
						outlet(0,oscmsg);
					} else if(found){
						oscmsg = "/3DTI-OSC/source"+sourceID+"/"+action;
						if(action=="mute" || action=="reverb" || action=="gain") {
							oscmsg = oscmsg + " " + parameter;
						}
						outlet(0,oscmsg);
					}
					sourceID = sourceID + 1;
					
				}
			}	
		}
	}
}

function findInList(str,strlist) {
	for(i=0;i<strlist.length;i++) {
		if(str==strlist[i]) {
			return i;
		}
	}
	return -1;
}

function playAll() {
	outlet(0,"play",1,nsources);
}

function pauseAll() {
	outlet(0,"pause",1,nsources);	
}

function stopAll() {
	outlet(0,"stop",1,nsources);	
}


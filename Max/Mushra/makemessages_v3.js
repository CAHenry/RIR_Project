
inlets = 1;
outlets = 1;

setinletassist(0, "msg program room condition action parameter");

var programs = ['TakeFive', 'Speech'];
var nDirectSources =  [5, 1];
var rooms =  ['Library', 'Trapezoid'];// ['Trapezoid']
var conditions = ['Direct', '0OA', '1OA', '2OA', '3OA', '4OA'];
var nSourcesPerCondition = [1, 6, 6, 12, 20, 32];

var nSourcesTotal = 316;
var sourceState = new Array(nSourcesTotal);

for(i=0; i<nSourcesTotal; i++) {
	sourceState[i] = 1;
}

function msg(program,room,condition,action,parameter) {
	sourceID = 1;
	for(i=0; i<programs.length; i++) {
		for(j=0; j<rooms.length; j++) {
			for(k=0; k<conditions.length; k++) {
				nsources = nSourcesPerCondition[k];
				direct = 0;
				if(k==0) { // direct
					direct = 1;
					nsources = nDirectSources[i];
				}
				foundProgAndRoom = 0;
				if(programs[i]==program && rooms[j]==room) {
					foundProgAndRoom = 1;	
				}
				found = 0;
				if(condition=="All" || (foundProgAndRoom && conditions[k]==condition)) {
					found = 1;
				}
				counter=0;
				lastSourceID = sourceID+nsources-1;
				while(sourceID<=lastSourceID) {	
					if(action=="focus") { // focus: unmute this & mute the rest
						currentState = sourceState[sourceID-1]; // -1 because 0 indexing
						if(found || (direct && foundProgAndRoom)) {
							newState = 1;
						} else {
							newState = 0;
						}
						if(newState != currentState) {
							oscmsg = "/3DTI-OSC/source"+sourceID+"/mute ";
							if(newState == 1) {
								oscmsg = oscmsg + "0";
							} else {
								oscmsg = oscmsg + "1";
							}
							outlet(0,oscmsg);
							sourceState[sourceID-1] = newState;
						}
					} else if(found){
						if(action == "mute") {
							currentState = sourceState[sourceID-1]; // -1 because 0 indexing
							if(action == "1") {
								newState = 0;
							} else {
								newState = 1;
							}
							if(newState != currentState) {
								oscmsg = "/3DTI-OSC/source"+sourceID+"/mute ";
								if(newState == 1) {
									oscmsg = oscmsg + "0";
								} else {
									oscmsg = oscmsg + "1";
								}
								outlet(0,oscmsg);
								sourceState[sourceID-1] = newState;
							}
						} else {
							oscmsg = "/3DTI-OSC/source"+sourceID+"/"+action;
							if(action=="reverb" || action=="gain") {
								oscmsg = oscmsg + " " + parameter;
							}
							outlet(0,oscmsg);
						}
					}
					sourceID = sourceID + 1;
					
				}
			}	
		}
	}
}


inlets = 2;
outlets = 2;

setinletassist(0, "msg program room condition action parameter");
setoutletassist(0, "all head-tracked sources, to first toolkit");
setoutletassist(1, "static reverb, to second toolkit");

var programs = ['TakeFive', 'Speech'];
var nDirectSources =  [5, 1];
//var rooms =  ['Library', 'Trapezoid'];// ['Trapezoid']
var conditions = ['direct', '1OA','1OAS'];
var nSourcesPerCondition = [1, 6, 6];
var plus6db = 1;
var currRoom = 'Library';

function msg_int(n) {
	if(inlet == 1) {
		plus6dB = n;
		if(currRoom=="Library") {
			gain = 0;
			if(plus6dB) {
				gain = gain + 6;
			}
		} else {
			gain = 0;
			if(plus6dB) {
				gain = gain + 6;
			}
		}
		oscmsg = "/3DTI-OSC/environment/gain " + gain;
		outlet(0,oscmsg);
	}
}

function msg(program,room,condition,action,parameter) { // room has no effect here
	currRoom = room; // most recent room
	if(condition=="ABIR" && (action=="focus" || (action=="mute" && parameter==0))) {
		outlet(0,"/3DTI-OSC/environment/order 3D");
		if(room=="Library") {
			gain = 0;
			if(plus6dB) {
				gain = gain + 6;
			}
		} else {
			gain = 0;
			if(plus6dB) {
				gain = gain + 6;
			}
		}
		oscmsg = "/3DTI-OSC/environment/gain " + gain;
		outlet(0,oscmsg);
	}
	sourceID = 1;
	for(i=0; i<programs.length; i++) {
			for(k=0; k<conditions.length; k++) {
				nsources = nSourcesPerCondition[k];
				direct = 0;
				if(k==0) { // direct
					direct = 1;
					nsources = nDirectSources[i];
				}
				foundProgAndRoom = 0;
				if(programs[i]==program) {
					foundProgAndRoom = 1;	
				}
				found = 0;
				if(condition=="All" || (foundProgAndRoom && conditions[k]==condition) || (foundProgAndRoom && condition=="ABIR" && conditions[k]=="direct")) {
					found = 1;
				}
				lastSourceID = sourceID+nsources-1;
				while(sourceID<=lastSourceID) {	
					if(action=="focus") { // focus: unmute this & mute the rest
						oscmsg = "/3DTI-OSC/source"+sourceID+"/mute ";
						if(found || (direct && foundProgAndRoom)) {
							oscmsg = oscmsg + "0";
						} else {
							oscmsg = oscmsg + "1";
						}
						outlet(0,oscmsg);
						if(direct) {
							if(foundProgAndRoom && condition=="ABIR") {
								outlet(0,"/3DTI-OSC/source"+sourceID+"/reverb 1");
							}
							if(!foundProgAndRoom || (foundProgAndRoom && condition!="ABIR")) {
								outlet(0,"/3DTI-OSC/source"+sourceID+"/reverb 0");
							}
						}
					} else if(found){
						if(condition=="ABIR" && action=="mute") {
							action = "reverb";
							if(parameter==0) {
								parameter = 1;
							} else {
								parameter = 0;
							}
						}
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

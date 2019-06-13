
inlets = 1;
outlets = 1;

var nsources = 12;

var r = 1.5; // 1.5 for library, 1.2 for trapezoid

var sources = [ [ r,  0,  0],
                [ 0,  r,  0],
		   		[-r,  0,  0],
		     	[ 0, -r,  0],
		   		[ 0,  0,  1],
		   		[ 0,  0, -1],
				[ r,  0,  0],
                [ 0,  r,  0],
		   		[-r,  0,  0],
		     	[ 0, -r,  0],
		   		[ 0,  0,  r],
		   		[ 0,  0, -r]];
		
var sourceIDs = [17, 18, 19, 20, 21, 22, 31, 32, 33, 34, 35, 36];

function pry(pitch,roll,yaw) {
	for(i=0; i<nsources; i++) {
		xyz = sources[i];
		xyz = eulerRotate(xyz,-pitch,roll,-yaw);
		str = "/3DTI-OSC/source"+sourceIDs[i]+"/pos";
		outlet(0,str,xyz)
	}
}

function eulerRotate(xyz,pitch,roll,yaw) {
	psi = roll;
	tht = pitch;
	phi = yaw;	
	
	x = xyz[0];
	y = xyz[1];
	z = xyz[2];
	
	xx = x*(Math.cos(tht)*Math.cos(phi)) + y*(Math.sin(psi)*Math.sin(tht)*Math.cos(phi)-Math.cos(psi)*Math.sin(phi)) + z*(Math.cos(psi)*Math.sin(tht)*Math.cos(phi)+Math.sin(psi)*Math.sin(phi));
	yy = x*(Math.cos(tht)*Math.sin(phi)) + y*(Math.sin(psi)*Math.sin(tht)*Math.sin(phi)+Math.cos(psi)*Math.cos(phi)) + z*(Math.cos(psi)*Math.sin(tht)*Math.sin(phi)-Math.sin(psi)*Math.cos(phi));
	zz = x*(-Math.sin(tht)) + y*(Math.sin(psi)*Math.cos(tht)) + z*(Math.cos(psi)*Math.cos(tht));

	xyz = [xx, yy, zz];
	return xyz;
}

function room(str) {
	if(str == "Library") {
		r = 1.5; // 1.5 for library, 1.2 for trapezoid
	} else {
		r = 1.2;
	}
	sources = [ [ r,  0,  0],
                [ 0,  r,  0],
		   		[-r,  0,  0],
		     	[ 0, -r,  0],
		   		[ 0,  0,  1],
		   		[ 0,  0, -1],
				[ r,  0,  0],
                [ 0,  r,  0],
		   		[-r,  0,  0],
		     	[ 0, -r,  0],
		   		[ 0,  0,  r],
		   		[ 0,  0, -r]];
}